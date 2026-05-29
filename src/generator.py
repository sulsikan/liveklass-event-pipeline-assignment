import time
import random
import uuid
import logging
import os
from datetime import datetime, timezone

# 로그 디렉토리 및 파일 설정
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
APP_LOG_FILE = os.path.join(LOG_DIR, "app.log")

# 로깅 설정 (콘솔 및 파일 출력 모두 지원)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(APP_LOG_FILE, encoding="utf-8")
    ]
)

# 데이터셋 정의
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
    제시된 새로운 스키마 규격에 최적화된 무작위 사용 행태 이벤트를 생성합니다.
    """
    # 1. 고유 유저 ID (정수형: 1~1000) 및 세션 ID 설정
    if user_id is None:
        user_id = random.randint(1, 1000)
    if session_id is None:
        session_id = str(uuid.uuid4())

    # 2. 메타 정보 설정 (연령대)
    age_group = random.choices(AGE_GROUPS, weights=[0.10, 0.35, 0.30, 0.15, 0.10], k=1)[0]

    # 3. 이벤트 종류 설정
    event_type = random.choices(EVENT_TYPES, weights=[0.65, 0.20, 0.10, 0.05], k=1)[0]

    # 4. 기본 이벤트 딕셔너리 구성 (event_id는 DB에서 BIGSERIAL로 생성하므로 제외 가능하지만 시뮬레이션을 위해 유지)
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

    # 5. 이벤트 타입별 카테고리/상품 세부 필드 바인딩
    if event_type in ["view", "click", "purchase"]:
        # 카테고리 무작위 선택
        cat_id = random.choice(list(CATEGORIES.keys()))
        cat_info = CATEGORIES[cat_id]
        
        event["category_id"] = cat_id
        event["category_name"] = cat_info["name"]

        # 뷰, 클릭, 구매는 특정 상품과 연관될 가능성이 큼
        prod_id = random.choice(list(cat_info["products"].keys()))
        prod_info = cat_info["products"][prod_id]
        
        event["product_id"] = prod_id
        event["price"] = prod_info["price"]

        # 단순 뷰나 클릭 시 간혹 특정 상품이 아닌 카테고리 메인 페이지를 보는 상황 묘사 (20% 확률로 상품 정보 비움)
        if event_type in ["view", "click"] and random.random() < 0.20:
            event["product_id"] = None
            event["price"] = None

    elif event_type == "error":
        # 에러 이벤트는 서비스 전역 혹은 일시적인 상황을 묘사하므로 카테고리/상품은 일반적으로 없음
        # 다만 시스템에 따라 20% 확률로 에러가 발생한 지점의 카테고리 정보를 기록
        if random.random() < 0.20:
            cat_id = random.choice(list(CATEGORIES.keys()))
            event["category_id"] = cat_id
            event["category_name"] = CATEGORIES[cat_id]["name"]

    return event

if __name__ == "__main__":
    logging.info("=========================================")
    logging.info("이벤트 로그 생성기 시뮬레이션을 시작합니다.")
    logging.info(f"애플리케이션 실행 로그 저장 경로: {APP_LOG_FILE}")
    logging.info("=========================================")
    
    try:
        for i in range(1, 6):
            event = generate_event()
            logging.info(
                f"[이벤트 {i}] 시간={event['event_time']} | 유저={event['user_id']} ({event['age_group']}) | "
                f"타입={event['event_type']} | 카테고리={event['category_name']}({event['category_id']}) | "
                f"상품={event['product_id']} | 가격={event['price']}"
            )
            time.sleep(0.1)
        logging.info("이벤트 생성 시뮬레이션이 성공적으로 완료되었습니다.")
    except Exception as e:
        logging.error(f"시뮬레이션 중 오류가 발생했습니다: {e}")
