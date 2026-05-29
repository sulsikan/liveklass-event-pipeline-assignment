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

def generate_event(user_id=None, session_id=None):
    """
    무작위 사용 행태 이벤트를 생성합니다.
    """
    if user_id is None:
        user_id = random.randint(1, 1000)
    if session_id is None:
        session_id = str(uuid.uuid4())

    age_group = random.choices(AGE_GROUPS, weights=[0.10, 0.35, 0.30, 0.15, 0.10], k=1)[0]
    event_type = random.choices(EVENT_TYPES, weights=[0.65, 0.20, 0.10, 0.05], k=1)[0]

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

    if event_type in ["view", "click", "purchase"]:
        cat_id = random.choice(list(CATEGORIES.keys()))
        cat_info = CATEGORIES[cat_id]
        
        event["category_id"] = cat_id
        event["category_name"] = cat_info["name"]

        prod_id = random.choice(list(cat_info["products"].keys()))
        prod_info = cat_info["products"][prod_id]
        
        event["product_id"] = prod_id
        event["price"] = prod_info["price"]

        if event_type in ["view", "click"] and random.random() < 0.20:
            event["product_id"] = None
            event["price"] = None

    elif event_type == "error":
        if random.random() < 0.20:
            cat_id = random.choice(list(CATEGORIES.keys()))
            event["category_id"] = cat_id
            event["category_name"] = CATEGORIES[cat_id]["name"]

    return event

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
            # 1. 무작위 이벤트 생성
            raw_event = generate_event()
            
            # 2. 데이터 품질 검증 계층 통과 (Data Management)
            if not validate_event(raw_event):
                logging.warning(f"오염된 이벤트 유입으로 적재가 생략되었습니다: {raw_event}")
                continue
            
            # 3. 데이터베이스 적재 (오류 발생 시 자동 복구 로직 적용)
            try:
                insert_event(connection, raw_event)
                event_count += 1
                
                # 대량의 데이터 생성 속도 조절 및 실시간 흐름 묘사 (0.5초 ~ 1.5초 무작위 딜레이)
                if event_count % 10 == 0:
                    logging.info(f"현재 누적 적재 성공 이벤트 수: {event_count}개")
                    
                time.sleep(random.uniform(0.5, 1.5))
                
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

    except KeyboardInterrupt:
        logging.info("사용자 중단 요청(Ctrl+C)을 감지했습니다.")
    finally:
        # 안전한 데이터베이스 리소스 클린업 (Software Engineering)
        if connection:
            connection.close()
            logging.info("데이터베이스 연결을 안전하게 종료하고 리소스를 반환했습니다.")
        logging.info("파이프라인이 정상적으로 완전히 종료되었습니다.")
