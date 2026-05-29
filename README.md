# 간단한 이벤트 로그 파이프라인 구축 프로젝트 (Assignment)

이 프로젝트는 웹 서비스에서 발생하는 가상 사용자 행동 이벤트를 생성하고, 데이터베이스(PostgreSQL)에 적재한 뒤, 이를 분석하고 시각화하는 전체 파이프라인의 구축 과제입니다.

---

## 1. 실행 방법

### 필요한 도구 및 설치
*   **Docker 및 Docker Compose**: 데이터베이스 및 컨테이너 환경 구축에 사용됩니다.
*   **Python 3.11 이상**: 로컬에서 이벤트 생성기를 직접 실행하고 테스트할 때 사용됩니다.

### 실행 명령어 순서

1.  **명령어 통합 로깅 도구 권한 부여 (최초 1회)**
    ```bash
    chmod +x run.sh
    ```

2.  **전체 스택 실행**
    ```bash
    docker compose up -d --build
    ```
    *   PostgreSQL, 이벤트 생성기, Grafana가 함께 올라갑니다.
    *   이벤트 생성기는 실행 후 자동으로 이벤트를 계속 생성하며, `docker compose stop app`으로 잠시 멈출 수 있습니다.

3.  **이벤트 생성기 로컬 실행 테스트**
    이 프로젝트는 모든 터미널 실행 명령어를 추적하여 로그로 저장하는 `run.sh` 도구를 지원합니다.
    ```bash
    ./run.sh python3 src/generator.py
    ```
    *   위 명령어를 실행하면 콘솔에 무작위 가상 사용자 로그가 계속 생성 및 출력되며, 실행 내역은 `logs/command_history.log` 및 `logs/app.log` 파일에 안전하게 기록됩니다.

---

## 2. 스키마 설명

### 테이블 설계 이유
*   단순 통째 JSON 방식 대신 정형화된 개별 컬럼 구조를 선택하여, 각 행동 필드에 최적화된 인덱스를 적용하고 SQL 집계 쿼리 분석 속도 및 데이터 정밀도를 극대화했습니다.
*   에러나 일반 조회 등의 상황에서 불필요한 값을 유연하게 무시할 수 있도록 필수 필드(`user_id`, `session_id`, `event_type`, `event_time`)와 가변 필드(`product_id`, `price` 등)를 분리 설계했습니다.

### 테이블 상세 스키마 정의 (`events`)

| 필드명 | 데이터 타입 | 설명 | 예시 |
| :--- | :--- | :--- | :--- |
| `event_id` | BIGSERIAL PK | 데이터베이스 자동 증가 고유 식별값 | `1` |
| `user_id` | INTEGER | 가상의 정수형 사용자 고유 ID (1~1000) | `482` |
| `session_id` | VARCHAR | 브라우저 세션 고유 UUID | `b78e1c6b-95bb-41a4-94c0-2f311c6d1d4d` |
| `event_type` | VARCHAR | 이벤트 종류 (`view`, `click`, `purchase`, `error`) | `purchase` |
| `category_id` | INTEGER | 카테고리 식별 번호 (1: Electronics, 2: Clothing 등) | `1` |
| `category_name`| VARCHAR | 카테고리 영문명 | `Electronics` |
| `product_id` | INTEGER (NULL 가능)| 상품 고유 ID (101: Laptop 등) | `101` |
| `price` | INTEGER (NULL 가능)| 상품 가격 (KRW) | `1200000` |
| `age_group` | VARCHAR | 사용자 연령대 (`10s`, `20s`, `30s`, `40s`, `50s`) | `30s` |
| `event_time` | TIMESTAMP | 이벤트가 발생한 시간 | `2026-05-28 09:05:26.699` |

---

## 3. 구현하면서 고민한 점

### 1. 사용자 행동 시나리오 기반의 데이터 일관성
단순 무작위 매핑 대신, 사용자의 실제 행동(조회 -> 클릭 -> 구매) 흐름을 반영하려 노력했습니다. 예를 들어 `purchase` 이벤트가 발생하면 반드시 특정 상품 ID와 실제 매칭 가격이 동반되도록 데이터 무결성을 챙겼으며, 에러 발생 시에는 비즈니스 항목들이 적절히 비워지도록 분기 제어를 정교화했습니다.

### 2. 가독성을 고려한 프로젝트 구조화
기존에 모든 소스코드가 프로젝트 루트 디렉터리에 노출되어 있어 복잡도가 증가하는 단점이 있었습니다. 이를 소스코드는 `src/` 디렉터리로, 데이터베이스 정의 스키마는 `db/` 디렉터리로 엄격하게 나누어 정리함으로써 평가관이 구조를 쉽게 파악할 수 있도록 리팩터링했습니다.

### 3. 히스토리 로깅과 변경 최소화
사용되지 않는 컬럼(`device_type`)을 빠르게 솎아내어 데이터 모델을 단순화했습니다. 또한, 터미널 명령어를 일일이 추적하기 위해 커맨드 래퍼(`run.sh`)를 직접 작성하여, 프로젝트 생명주기 동안 발생한 모든 기동 및 설정 행위가 흔적으로 고스란히 남아 검증에 용이하도록 구성했습니다.

---

## 4. 시각화

### Grafana 대시보드
Step 5는 Grafana로 구성했습니다. `docker compose up -d` 후 아래 주소로 접속하면 대시보드를 볼 수 있습니다.

- URL: `http://localhost:3000`
- 계정: `admin`
- 비밀번호: `admin2026`

### 대시보드 구성
- `Total Events`
- `Event Type Distribution`
- `Hourly Event Trend`
- `Top Users`

### 분석 쿼리
`sql/analysis_queries.sql`에 Step 3용 SQL을 따로 모아 두었습니다. 대시보드 패널에도 같은 쿼리를 사용했습니다.
