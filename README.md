# liveklass-event-pipeline-assignment

웹 서비스에서 발생하는 가상 사용자 행동 이벤트를 생성하고, PostgreSQL에 저장한 뒤, Grafana로 시각화하는 간단한 이벤트 파이프라인입니다.

## 1. 실행 방법

### 필요한 도구
- Docker
- Docker Compose
- Python 3.11 이상

### 설치 및 실행
1. 전체 스택 실행
   ```bash
   docker compose up
   ```

2. PostgreSQL 확인
   ```bash
   docker compose exec db psql -U postgres -d assignment_db
   ```

3. Grafana 접속
- URL: `http://localhost:3000`
- ID: `admin`
- PW: `admin2026`


## 2. 스키마 설명

### events 테이블

| 컬럼명        | 타입           | 설명                                            |
| ---------- | ------------ | --------------------------------------------- |
| event_id   | BIGSERIAL    | 이벤트 고유 ID (PK)                                |
| user_id    | INTEGER      | 사용자 ID                                        |
| session_id | VARCHAR(100) | 세션 식별자                                        |
| event_type | VARCHAR(50)  | 이벤트 유형 (`view`, `enroll`, `payment`, `error`) |
| product_id | INTEGER      | 강의 ID                                         |
| price      | INTEGER      | 강의 가격                                         |
| event_time | TIMESTAMP    | 이벤트 발생 시각                                     |

온라인 강의 플랫폼의 사용자 행동 데이터를 가정하여 스키마를 설계했습니다. 

`events` 테이블은 이벤트 분석과 운영 모니터링에 필요한 핵심 필드만 포함하도록 단순하게 구성했습니다. `user_id`와 `session_id`를 통해 사용자 및 세션 단위 분석이 가능하며, `product_id`와 `price`를 통해 강의 탐색 및 결제 흐름을 확인할 수 있도록 설계했습니다.

또한 `event_type`과 `event_time`을 활용하여 이벤트 발생 현황, 에러 비율, 사용자 활동량 등 주요 운영 지표를 집계하고 Grafana 대시보드로 시각화할 수 있도록 구성했습니다.


## 3. 구현하면서 고민한 점

### Step 1. 이벤트 생성기

#### (1) 세션 기반 이벤트 흐름 설계
초기 구현에서는 이벤트 1건이 하나의 세션을 의미하는 구조로 데이터를 생성했습니다. 그러나 실제 온라인 서비스에서는 사용자가 하나의 세션 내에서 여러 행동을 연속적으로 수행하므로, 단일 이벤트만 반복 생성하는 방식은 실제 사용자 행동 패턴을 충분히 반영하지 못한다고 판단했습니다.

이를 개선하기 위해 세션 단위 이벤트 생성 방식을 적용했으며, 하나의 세션에서 view → enroll → payment와 같은 연속적인 행동 흐름이 발생하도록 구현했습니다. 이를 통해 세션 기반 지표를 활용한 모니터링이 가능하도록 구성했습니다.

#### (2) 이벤트 타입 선정
이벤트 타입은 온라인 강의 플랫폼 환경을 가정하여 설계했습니다. 강의 조회, 수강 신청, 결제와 같은 주요 사용자 행동을 반영하기 위해 view, enroll, payment 이벤트를 정의했으며, 운영 환경에서의 장애 상황을 모니터링하기 위해 error 이벤트를 추가했습니다.

과제의 목적이 데이터 분석보다는 데이터 파이프라인 구축 및 운영 모니터링에 있다고 판단하여, 복잡한 사용자 행동 이벤트를 다수 추가하기보다는 서비스 상태를 파악할 수 있는 핵심 이벤트 중심으로 구성했습니다.

#### (3) 데이터 품질 검증
각 강의 ID에 대해 강의명과 가격 정보를 고정값으로 관리하여 동일한 강의에 서로 다른 가격이 저장되는 문제를 방지했습니다. 또한 데이터 적재 전 검증 로직을 추가하여 필수 컬럼 누락, 잘못된 이벤트 타입 등 비정상 데이터가 데이터베이스에 저장되지 않도록 구성했습니다. 이를 통해 데이터 생성 단계부터 데이터 품질을 관리할 수 있도록 구현했습니다.

#### (4) 데이터베이스 재시도 및 자동 복구 로직
Docker 환경에서는 데이터베이스가 완전히 준비되기 전에 애플리케이션이 먼저 실행되거나, 운영 중 일시적인 연결 장애가 발생할 수 있기 때문에 데이터베이스 연결 시 Exponential Backoff 기반 재시도 로직을 적용했습니다. 연결 실패 시 일정 시간 대기 후 재접속을 시도하도록 구현했으며, 운영 중 연결이 유실된 경우 자동으로 데이터베이스 연결을 복구하도록 구성했습니다.

#### (5) 로그 관리
파이프라인 운영 상태를 확인할 수 있도록 주요 동작 과정에 대한 로그를 기록하도록 구성했습니다.

애플리케이션 기동, 데이터베이스 연결, 이벤트 적재 성공, 데이터 검증 실패, 예외 발생 및 복구 과정 등을 로그로 남기도록 구현했으며, 운영자가 파이프라인 상태를 추적할 수 있도록 했습니다.

### Step 2. 로그 저장

#### PostgreSQL을 선택한 이유
이벤트 데이터를 단순 저장하는 것보다, 저장된 데이터를 실시간으로 집계하고 모니터링하는 과정이 중요하다고 판단했습니다.

이를 위해 PostgreSQL을 이벤트 저장소로 선택했습니다. PostgreSQL은 SQL 기반 집계 기능을 제공하므로 이벤트 발생 건수, 에러 비율, 활성 사용자 수와 같은 운영 지표를 효율적으로 계산할 수 있습니다. 또한 Grafana와의 연동이 용이하여 저장된 데이터를 기반으로 실시간 대시보드를 구성할 수 있습니다. 이를 통해 이벤트 적재부터 집계, 시각화까지 하나의 흐름으로 구성할 수 있었습니다.

### Step 3. 데이터 집계 분석

전체 추이, 이벤트 타입별 분포, 유저별 총 이벤트 수처럼 바로 확인할 수 있는 쿼리를 중심으로 두고, 시간 버킷은 대시보드와 같은 기준으로 맞춰 분석 결과가 화면과 어긋나지 않도록 했습니다.

분석 쿼리는 4. 데이터 집계 분석 쿼리에 정리해두었습니다.

### Step 4. Docker로 실행 가능하게 만들기

`docker compose up` 한 번으로 PostgreSQL, 이벤트 생성기, Grafana가 함께 실행되도록 구성했습니다.

데이터베이스 데이터는 Docker Volume을 사용하여 컨테이너 재시작 이후에도 유지되도록 했으며, 애플리케이션 로그는 로컬 폴더에 저장하여 운영 상태를 확인할 수 있도록 구성했습니다.

### Step 5. 결과 시각화
비즈니스 인사이트를 더 풍부하게 보여주는 대시보드를 만들 수도 있었지만, 과제의 기본에 충실하기 위해 시스템 운영 이벤트를 확인하는 방향에 집중했습니다. 그래서 추가적인 컬럼 확장은 하지 않았고, Grafana도 운영 관점에서 집계할 만한 지표들 중심으로 구성했습니다. 대시보드는 전체 이벤트 흐름, error 비율, 활성 사용자, 세션 활동 같은 운영 지표가 바로 보이도록 배치했습니다.


## 4. 데이터 집계 분석 쿼리

### (1). 이벤트 타입별 발생 횟수

```sql
SELECT
    event_type,
    COUNT(*) AS event_count
FROM events
GROUP BY event_type
ORDER BY event_count DESC, event_type ASC;
```

이벤트 타입별 발생 건수를 집계하여 서비스 내 사용자 행동 분포를 확인합니다.

---

### (2) 유저별 총 이벤트 수

```sql
SELECT
    user_id,
    COUNT(*) AS event_count
FROM events
GROUP BY user_id
ORDER BY event_count DESC, user_id ASC
LIMIT 10;
```

이벤트 발생 횟수가 많은 상위 사용자를 조회하여 사용자 활동량을 확인합니다.

---

### (3) 시간대별 이벤트 추이

```sql
SELECT
    date_trunc('minute', event_time) AS time,
    COUNT(*) AS event_count
FROM events
GROUP BY 1
ORDER BY 1;
```

시간에 따른 전체 이벤트 발생량을 집계하여 서비스 트래픽 변화를 확인합니다.

※ Grafana에서는 10분 단위 그룹화(`$__timeGroupAlias`)를 적용하여 시각화했습니다.

---

### (4) 에러 이벤트 비율

```sql
SELECT
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE event_type = 'error')
        / NULLIF(COUNT(*), 0),
        2
    ) AS error_ratio
FROM events;
```

전체 이벤트 대비 에러 이벤트의 비율을 계산하여 서비스 안정성을 모니터링합니다.

---

### (5) 활성 사용자 수

```sql
SELECT
    date_trunc('minute', event_time) AS time,
    COUNT(DISTINCT user_id) AS active_users
FROM events
GROUP BY 1
ORDER BY 1;
```

특정 시간 구간 동안 활동한 사용자 수를 집계하여 서비스 이용 현황을 확인합니다.

---

### (6) 평균 세션 활동 수

```sql
SELECT
    date_trunc('minute', event_time) AS time,
    ROUND(
        COUNT(*)::numeric
        / NULLIF(COUNT(DISTINCT session_id), 0),
        2
    ) AS avg_events_per_session
FROM events
GROUP BY 1
ORDER BY 1;
```

세션당 평균 이벤트 수를 계산하여 사용자의 평균 활동량을 확인합니다.



## 5. 시각화

Grafana 대시보드는 `docker compose up` 이후 `http://localhost:3000`에서 확인할 수 있습니다. 주요 패널은 다음과 같습니다.

<img src="docs/images/grafana-dashboard-01.png" alt="Grafana dashboard overview" width="100%">

- `Total Events` : 현재까지 적재된 전체 이벤트 수를 확인합니다.
- `Error Ratio` : 전체 이벤트 중 error 이벤트가 차지하는 비율을 확인합니다.
- `Event Type Distribution` : view, enroll, payment, error 이벤트가 어떤 비중으로 발생했는지 비교합니다.

<img src="docs/images/grafana-dashboard-02.png" alt="Grafana dashboard overview" width="100%">

- `Overall Event Trend` : 시간 흐름에 따른 전체 이벤트 발생 추이를 확인합니다.

<img src="docs/images/grafana-dashboard-03.png" alt="Grafana dashboard overview" width="100%">

- `Average Events per User` : 시간 구간별 사용자 1명당 평균 이벤트 수를 확인합니다.
- `Active Users` : 시간 구간별 이벤트를 발생시킨 고유 사용자 수를 확인합니다.

<img src="docs/images/grafana-dashboard-04.png" alt="Grafana dashboard overview" width="100%">

- `Average Session Activity` : 시간 구간별 세션 1개당 평균 이벤트 수를 확인합니다.
- `Top Users` : 이벤트를 가장 많이 발생시킨 상위 사용자를 확인합니다.

