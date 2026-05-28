import time
import random
import uuid
from datetime import datetime, timezone

# 가상 유저 데이터셋 정의
USER_IDS = [f"user_{i:03d}" for i in range(1, 101)]  # 100명의 가상 유저
PAGES = [
    {"url": "/home", "name": "메인 페이지"},
    {"url": "/products", "name": "상품 목록 페이지"},
    {"url": "/products/101", "name": "파이프라인 입문 강의"},
    {"url": "/products/102", "name": "고급 SQL 정복 가이드"},
    {"url": "/cart", "name": "장바구니"},
    {"url": "/checkout", "name": "결제 페이지"},
]
CLICK_ELEMENTS = ["btn_add_to_cart", "btn_apply_coupon", "btn_submit_payment", "btn_view_details", "nav_contact"]
ERROR_SCENARIOS = [
    {"code": 404, "message": "Page Not Found"},
    {"code": 500, "message": "Internal Server Error"},
    {"code": 403, "message": "Forbidden Access"},
    {"code": 503, "message": "Service Unavailable"},
]

def generate_event(user_id=None, session_id=None):
    """
    하나의 웹 서비스 사용자 행동(이벤트)을 무작위로 생성합니다.
    사용자 시나리오의 흐름을 반영하여 현실감 있는 이벤트를 생성합니다.
    """
    if not user_id:
        user_id = random.choice(USER_IDS)
    if not session_id:
        session_id = str(uuid.uuid4())
        
    event_type = random.choices(
        ["page_view", "click", "purchase", "error"],
        weights=[0.60, 0.25, 0.10, 0.05],  # 현실적인 비율: 페이지 조회 > 클릭 > 구매 > 에러
        k=1
    )[0]
    
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event_type,
        "page_url": None,
        "amount": None,
        "status_code": None,
        "error_message": None,
        "element_id": None
    }
    
    if event_type == "page_view":
        page = random.choice(PAGES)
        event["page_url"] = page["url"]
        event["status_code"] = 200
        
    elif event_type == "click":
        page = random.choice(PAGES)
        event["page_url"] = page["url"]
        event["element_id"] = random.choice(CLICK_ELEMENTS)
        event["status_code"] = 200
        
    elif event_type == "purchase":
        event["page_url"] = "/checkout"
        # 구매 금액을 10,000원 ~ 150,000원 사이에서 5,000원 단위로 랜덤 설정
        event["amount"] = random.randint(2, 30) * 5000
        event["status_code"] = 200
        
    elif event_type == "error":
        page = random.choice(PAGES)
        event["page_url"] = page["url"]
        err = random.choice(ERROR_SCENARIOS)
        event["status_code"] = err["code"]
        event["error_message"] = err["message"]
        
    return event

if __name__ == "__main__":
    print("--- 테스트용 이벤트 5개 생성 예시 ---")
    # 세션별 흐름을 모방한 시뮬레이션
    for _ in range(5):
        event = generate_event()
        print(f"[{event['timestamp']}] {event['user_id']} ({event['session_id'][:8]}): "
              f"type={event['event_type']}, url={event['page_url']}, "
              f"amount={event['amount']}, status={event['status_code']}, "
              f"element={event['element_id']}, err={event['error_message']}")
        time.sleep(0.1)
