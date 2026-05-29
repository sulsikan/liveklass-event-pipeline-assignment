import time
import random
import uuid
import logging
import os
import psycopg2
from datetime import datetime, timezone

# 1. 로깅 및 경로 설정 (DataOps)
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
    ]
)

# 2. 데이터베이스 접속 설정 (Security - 환경 변수 활용)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "assignment_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secure_password_2026")

# 3. 데이터 품질 관리 기준 데이터셋 (Data Management)
CATEGORIES = {
    1: {"name": "Electronics", "products": {
        101: {"name": "Laptop", "price": 1200000},
        102: {"name": "Smartphone", "price": 900000},
        103: {"name": "Wireless Earbuds", "price": 150000}
    }},
    2: {"name": "Clothing", "products": {
        201: {"name": "Hoodie", "price": 59000},
        202: {"name": "Jeans", "price": 79000},
        203: {"name": "Sneakers", "price": 120000}
    }},
    3: {"name": "Books", "products": {
        301: {"name": "SQL Guide", "price": 28000},
        302: {"name": "Data Pipeline Design", "price": 35000}
    }},
    4: {"name": "Home & Kitchen", "products": {
        401: {"name": "Coffee Maker", "price": 89000},
        402: {"name": "Air Fryer", "price": 129000}
    }},
    5: {"name": "Sports", "products": {
        501: {"name": "Treadmill", "price": 580000},
        502: {"name": "Yoga Mat", "price": 25000}
    }}
}

AGE_GROUPS = ["10s", "20s", "30s", "40s", "50s"]
EVENT_TYPES = ["view", "click", "purchase", "error"]

def _make_event(user_id, session_id, age_group, event_type, category_id=None, product_id=None):
    """
    세션 컨텍스트를 반영한 단일 이벤트를 만듭니다.
    """
    event = {
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event_type,
        "category_id": None,
        "category_name": None,
        "product_id": None,
        "price": None,
        "age_group": age_group,
        "event_time": datetime.now(timezone.utc).isoformat()
    }

    if category_id is not None:
        cat_info = CATEGORIES[category_id]
        event["category_id"] = category_id
        event["category_name"] = cat_info["name"]

    if product_id is not None and category_id is not None:
        prod_info = CATEGORIES[category_id]["products"][product_id]
        event["product_id"] = product_id
        event["price"] = prod_info["price"]

    if event_type == "error" and event["category_id"] is None and random.random() < 0.5:
        cat_id = random.choice(list(CATEGORIES.keys()))
        event["category_id"] = cat_id
        event["category_name"] = CATEGORIES[cat_id]["name"]

    return event

def choose_session_profile():
    """
    한 세션에서 공통으로 유지할 사용자 프로필과 탐색 맥락을 고릅니다.
    """
    user_id = random.randint(1, 1000)
    session_id = str(uuid.uuid4())
    age_group = random.choices(AGE_GROUPS, weights=[0.10, 0.35, 0.30, 0.15, 0.10], k=1)[0]
    category_id = random.choice(list(CATEGORIES.keys()))
    product_id = random.choice(list(CATEGORIES[category_id]["products"].keys()))

    return {
        "user_id": user_id,
        "session_id": session_id,
        "age_group": age_group,
        "category_id": category_id,
        "product_id": product_id
    }

def generate_session_events():
    """
    하나의 세션 안에서 여러 이벤트가 이어지도록 생성합니다.
    """
    profile = choose_session_profile()
    session_length = random.choices([1, 2, 3, 4, 5, 6], weights=[0.08, 0.15, 0.25, 0.24, 0.18, 0.10], k=1)[0]
    events = []

    # 세션은 보통 상품 탐색(view)으로 시작합니다.
    events.append(
        _make_event(
            profile["user_id"],
            profile["session_id"],
            profile["age_group"],
            "view",
            category_id=profile["category_id"],
            product_id=profile["product_id"]
        )
    )

    # 중간에는 클릭, 추가 조회, 간헐적 에러가 섞일 수 있습니다.
    for _ in range(session_length - 1):
        roll = random.random()
        if roll < 0.10:
            event_type = "error"
            events.append(
                _make_event(
                    profile["user_id"],
                    profile["session_id"],
                    profile["age_group"],
                    event_type,
                    category_id=profile["category_id"]
                )
            )
        elif roll < 0.55:
            event_type = "click"
            if random.random() < 0.70:
                product_id = profile["product_id"]
            else:
                product_id = random.choice(list(CATEGORIES[profile["category_id"]]["products"].keys()))
            events.append(
                _make_event(
                    profile["user_id"],
                    profile["session_id"],
                    profile["age_group"],
                    event_type,
                    category_id=profile["category_id"],
                    product_id=product_id
                )
            )
        elif roll < 0.80:
            event_type = "view"
            product_id = random.choice(list(CATEGORIES[profile["category_id"]]["products"].keys()))
            events.append(
                _make_event(
                    profile["user_id"],
                    profile["session_id"],
                    profile["age_group"],
                    event_type,
                    category_id=profile["category_id"],
                    product_id=product_id
                )
            )
        else:
            event_type = "purchase"
            events.append(
                _make_event(
                    profile["user_id"],
                    profile["session_id"],
                    profile["age_group"],
                    event_type,
                    category_id=profile["category_id"],
                    product_id=profile["product_id"]
                )
            )

    # 구매가 없었던 세션은 가끔 마지막에 구매로 마무리하게 합니다.
    if not any(event["event_type"] == "purchase" for event in events) and random.random() < 0.35:
        events.append(
            _make_event(
                profile["user_id"],
                profile["session_id"],
                profile["age_group"],
                "purchase",
                category_id=profile["category_id"],
                product_id=profile["product_id"]
            )
        )

    return events

# 4. 데이터 품질 관리 레이어 (Data Management / Data Quality)
def validate_event(event):
    """
    생성된 이벤트가 적합한 스키마 규격을 만족하는지 검증합니다.
    """
    try:
        # 필수 필드 누락 검사
        required_fields = ["user_id", "session_id", "event_type", "age_group", "event_time"]
        for field in required_fields:
            if event.get(field) is None:
                logging.warning(f"[품질 검증 실패] 필수 필드 {field} 누락됨.")
                return False

        # 데이터 타입 정밀 검사
        if not isinstance(event["user_id"], int):
            logging.warning(f"[품질 검증 실패] user_id가 정수형이 아님: {type(event['user_id'])}")
            return False

        # 비즈니스 정합성 규칙 검사: purchase인 경우 반드시 product_id와 price가 있어야 함
        if event["event_type"] == "purchase":
            if event["product_id"] is None or event["price"] is None:
                logging.warning("[품질 검증 실패] purchase 이벤트에 상품 또는 가격 정보가 누락됨.")
                return False
                
        return True
    except Exception as e:
        logging.error(f"이벤트 검증 중 오류 발생: {e}")
        return False

# 5. 복구력 및 재시도 메커니즘 (Software Engineering - Exponential Backoff Retry)
def get_db_connection(max_retries=5, base_delay=2):
    """
    재시도 로직을 적용하여 PostgreSQL 데이터베이스 커넥션을 획득합니다.
    """
    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5
            )
            logging.info("데이터베이스 연결에 성공했습니다.")
            return conn
        except psycopg2.OperationalError as e:
            retries += 1
            delay = base_delay ** retries + random.uniform(0, 1)
            logging.warning(
                f"데이터베이스 연결 실패. 재시도 중 ({retries}/{max_retries}). "
                f"{delay:.2f}초 후 다시 시도합니다. 에러: {e}"
            )
            time.sleep(delay)
    
    logging.critical("최대 재시도 횟수를 초과하여 데이터베이스 연결에 실패했습니다.")
    raise ConnectionError("데이터베이스에 연결할 수 없습니다.")

# 6. 데이터 영구 적재 로직 (Data Architecture / Software Engineering)
def insert_event(conn, event):
    """
    컨텍스트 매니저를 통해 리소스 누수 없이 안전하게 이벤트를 삽입합니다.
    """
    insert_query = """
    INSERT INTO events (
        user_id, session_id, event_type, category_id, category_name, product_id, price, age_group, event_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    # with 커서 컨텍스트 매니저를 활용한 안전한 리소스 관리
    with conn.cursor() as cur:
        cur.execute(
            insert_query,
            (
                event["user_id"],
                event["session_id"],
                event["event_type"],
                event["category_id"],
                event["category_name"],
                event["product_id"],
                event["price"],
                event["age_group"],
                event["event_time"]
            )
        )
    conn.commit()

if __name__ == "__main__":
    logging.info("=========================================")
    logging.info("이벤트 로그 실시간 적재 파이프라인 기동")
    logging.info(f"DB_HOST: {DB_HOST} | DB_NAME: {DB_NAME}")
    logging.info("=========================================")

    # 최초 기동 시 데이터베이스 연결 시도 (Exponential Backoff 적용)
    try:
        connection = get_db_connection()
    except Exception as ex:
        logging.critical(f"초기 커넥션 실패로 파이프라인을 종료합니다: {ex}")
        exit(1)

    logging.info("실시간 이벤트 수집 및 데이터베이스 적재를 시작합니다. (Ctrl+C로 종료)")
    event_count = 0

    try:
        while True:
            # 1. 세션 단위 이벤트 생성
            session_events = generate_session_events()

            for raw_event in session_events:
                # 2. 데이터 품질 검증 계층 통과 (Data Management)
                if not validate_event(raw_event):
                    logging.warning(f"오염된 이벤트 유입으로 적재가 생략되었습니다: {raw_event}")
                    continue

                # 3. 데이터베이스 적재 (오류 발생 시 자동 복구 로직 적용)
                try:
                    insert_event(connection, raw_event)
                    event_count += 1

                    if event_count % 10 == 0:
                        logging.info(f"현재 누적 적재 성공 이벤트 수: {event_count}개")

                    # 세션 안에서 이벤트 간 간격을 두어 실제 사용자 행동처럼 보이게 함
                    time.sleep(random.uniform(0.2, 0.8))

                except (psycopg2.InterfaceError, psycopg2.OperationalError) as db_err:
                    logging.error(f"적재 중 데이터베이스 연결 유실 감지: {db_err}. 재접속 시도...")
                    try:
                        connection.close()
                    except Exception:
                        pass
                    connection = get_db_connection() # 복구 메커니즘 기동

                except Exception as e:
                    logging.error(f"이벤트 적재 실패 (일시적 오류): {e}")
                    time.sleep(1)

            # 세션 간에는 조금 더 긴 간격을 둡니다.
            time.sleep(random.uniform(0.8, 2.0))

    except KeyboardInterrupt:
        logging.info("사용자 중단 요청(Ctrl+C)을 감지했습니다.")
    finally:
        # 안전한 데이터베이스 리소스 클린업 (Software Engineering)
        if connection:
            connection.close()
            logging.info("데이터베이스 연결을 안전하게 종료하고 리소스를 반환했습니다.")
        logging.info("파이프라인이 정상적으로 완전히 종료되었습니다.")
