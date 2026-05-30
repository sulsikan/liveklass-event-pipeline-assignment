-- events 테이블 생성 정의
-- Step 2. 요구사항 및 사용자 지정 스키마 반영

CREATE TABLE IF NOT EXISTS events (
    event_id        BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    session_id      VARCHAR(100) NOT NULL,
    event_type      VARCHAR(50) NOT NULL,
    product_id      INTEGER NULL,
    price           INTEGER NULL,
    event_time      TIMESTAMP NOT NULL
);

-- 대시보드에서 실제로 자주 쓰는 시간 필터와 error 비율 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_events_event_time ON events (event_time);
CREATE INDEX IF NOT EXISTS idx_events_error_time ON events (event_time) WHERE event_type = 'error';
