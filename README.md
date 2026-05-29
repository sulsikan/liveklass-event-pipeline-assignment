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
   docker compose up -d --build
   ```

2. PostgreSQL 접속 확인
   ```bash
   docker compose exec db psql -U postgres -d assignment_db
   ```

3. Grafana 접속
- URL: `http://localhost:3000`
- ID: `admin`
- PW: `admin2026`


## 2. 스키마 설명

`events` 테이블은 이벤트 분석에 필요한 핵심 필드만 남겨 정규화된 형태로 설계했습니다. `event_type`, `product_id`, `price`, `event_time`처럼 집계와 필터링에 자주 쓰이는 값을 컬럼으로 분리해 SQL 분석과 Grafana 시각화가 쉽도록 했습니다.

`user_id`와 `session_id`는 사용자 단위, 세션 단위 분석에 필요하고, `product_id`와 `price`는 강의 서비스에서의 탐색 흐름과 구매 전환을 표현하는 데 사용합니다. 인덱스는 시간 필터와 error 비율 조회에 맞춰 `event_time`과 `error` 전용 부분 인덱스로 단순하게 가져갔습니다.

## 3. 구현하면서 고민한 점

### Step 1. 이벤트 생성기
가장 많이 고민한 부분은 데이터가 너무 “랜덤”해 보이지 않도록 만드는 일이었습니다. 단일 이벤트만 계속 생성하면 세션 분석이 의미가 약해져서, 한 세션 안에서 `view -> click -> purchase` 같은 흐름이 이어지도록 생성 로직을 바꿨습니다. 그래서 `Average Session Activity`나 `Average Events per User` 같은 지표가 실제 서비스처럼 보이게 했습니다.

### Step 2. 로그 저장
저장소는 단순 JSON 파일보다 SQL 집계에 유리한 PostgreSQL을 선택했고, 이벤트를 분석할 때 필요한 핵심 필드만 남기도록 스키마를 정리했습니다. 처음에는 도메인 정보를 더 넣을 수도 있었지만, 운영 이벤트를 보는 과제의 기본에 맞추기 위해 컬럼 수를 최소화하는 방향을 택했습니다.

### Step 3. 데이터 집계 분석
Step 3에서는 대표적인 집계 쿼리를 따로 정리해 두었습니다. 전체 추이, 이벤트 타입별 분포, 유저별 총 이벤트 수처럼 바로 확인할 수 있는 쿼리를 중심으로 두고, 시간 버킷은 대시보드와 같은 기준으로 맞춰 분석 결과가 화면과 어긋나지 않도록 했습니다.

### Step 4. Docker로 실행 가능하게 만들기
`docker compose up -d --build` 한 번으로 DB와 앱, Grafana가 같이 올라가도록 구성했습니다. DB 데이터는 Docker volume에 두고 로그만 로컬 폴더에 남겨서, 환경을 다시 띄워도 같은 방식으로 재현할 수 있게 했습니다.

### Step 5. 결과 시각화
비즈니스 인사이트를 더 풍부하게 보여주는 대시보드를 만들 수도 있었지만, 과제의 기본에 더 충실하기 위해 시스템 운영 이벤트를 확인하는 방향에 집중했습니다. 그래서 추가적인 컬럼 확장은 하지 않았고, Grafana도 운영 관점에서 집계할 만한 지표들 중심으로 구성했습니다. 대시보드는 전체 이벤트 흐름, error 비율, 활성 사용자, 세션 활동 같은 운영 지표가 바로 보이도록 배치했습니다.

## 4. 시각화

Grafana 대시보드는 `docker compose up -d` 이후 `http://localhost:3000`에서 확인할 수 있습니다. 주요 패널은 다음과 같습니다.

- Total Events
- Error Ratio
- Event Type Distribution
- Overall Event Trend
- Average Events per User
- Active Users
- Average Session Activity
- Top Users

분석 쿼리는 `sql/analysis_queries.sql`에 별도로 정리해 두었습니다.
