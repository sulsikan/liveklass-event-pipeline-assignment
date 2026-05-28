# 📊 간단한 이벤트 로그 파이프라인 구축 프로젝트 (Assignment)

이 프로젝트는 웹 서비스에서 발생하는 가상 사용자 행동 이벤트를 생성하고, 데이터베이스(PostgreSQL)에 적재한 뒤, 이를 분석하고 시각화하는 전체 파이프라인의 구축 과제입니다.

---

## 🚀 Step 1. 이벤트 생성기 설계 (`generator.py`)

사용자가 웹 서비스 내부에서 수행하는 흐름을 최대한 현실적으로 반영할 수 있도록 **4종류의 이벤트**와 가상의 유저 데이터셋을 설계하였습니다.

### 1. 이벤트 타입 및 설계 이유

*   **`page_view` (페이지 조회 - 비율: 60%)**
    *   **설명**: 사용자가 웹 서비스의 특정 페이지를 방문했을 때 발생합니다.
    *   **설계 목적**: 가장 기본적이고 빈번하게 발생하는 행동 흐름을 추적하여 사이트 내 인기 페이지 및 사용자 여정(User Journey)을 분석하는 용도입니다.
*   **`click` (요소 클릭 - 비율: 25%)**
    *   **설명**: 페이지 내 특정 버튼(장바구니 담기, 구매 진행, 쿠폰 적용 등)을 클릭했을 때 발생합니다.
    *   **설계 목적**: 특정 기능의 사용성과 상호작용 강도를 측정하여 UI/UX 최적화의 기반 데이터로 사용합니다.
*   **`purchase` (구매 완료 - 비율: 10%)**
    *   **설명**: 사용자가 실제로 결제를 완료했을 때 발생합니다.
    *   **설계 목적**: 서비스의 가장 중요한 비즈니스 전환(Conversion Rate)과 매출 추이 분석을 위해 필수적으로 포함하였습니다.
*   **`error` (에러 발생 - 비율: 5%)**
    *   **설명**: 페이지 동작 중 서버 에러(500), 페이지 찾지 못함(404), 권한 없음(403) 등이 발생한 경우입니다.
    *   **설계 목적**: 비정상적인 사용자 경험(UX)이나 시스템 장애 상황을 모니터링하고 시스템 개선 우선순위를 정하는 지표로 사용합니다.

### 2. 이벤트 필드 구조 (스키마 설계)

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
| `device_type` | VARCHAR | 접속 기기 종류 (`Mobile`, `Desktop`, `Tablet`) | `Mobile` |
| `age_group` | VARCHAR | 사용자 연령대 (`10s`, `20s`, `30s`, `40s`, `50s`) | `30s` |
| `event_time` | TIMESTAMP | 이벤트가 발생한 시간 | `2026-05-28 09:05:26.699` |

---

## 🛠️ 실행 및 테스트 방법 (로컬)

### 1. 명령어 통합 로깅 도구 (`run.sh`)
이 프로젝트에서는 실행되는 모든 명령어와 상태(종료 코드, 소요 시간, 일시)를 실시간으로 추적하는 명령어 로깅 래퍼를 제공합니다.
*   **사용 방법**: 실행하려는 명령어 앞에 `./run.sh`를 붙여 실행합니다.
*   **실행 이력 저장 경로**: [logs/command_history.log](file:///Users/jueon/Coding/liveklass-event-pipeline-assignment/liveklass-event-pipeline-assignment/logs/command_history.log)

```bash
# 이벤트 생성기 실행 시
./run.sh python3 generator.py
```

### 2. 이벤트 생성기 로컬 테스트
```bash
python3 generator.py
```
*   콘솔에 포맷팅된 생성 로그가 동시 출력되며, 상세 실행 이력은 [logs/app.log](file:///Users/jueon/Coding/liveklass-event-pipeline-assignment/liveklass-event-pipeline-assignment/logs/app.log)에 함께 누적 저장됩니다.