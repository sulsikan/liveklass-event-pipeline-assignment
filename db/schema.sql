-- events 테이블 생성 정의
-- Step 2. 요구사항 및 사용자 지정 스키마 반영

CREATE TABLE IF NOT EXISTS events (
    event_id        BIGSERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL,
    session_id      VARCHAR(100) NOT NULL,
    event_type      VARCHAR(50) NOT NULL,
    category_id     INTEGER,
    category_name   VARCHAR(100),
    product_id      INTEGER NULL,
    price           INTEGER NULL,
    age_group       VARCHAR(20),
    event_time      TIMESTAMP NOT NULL
);

-- 자주 조회되거나 분석 쿼리 필터에 사용될 주요 인덱스 설계
CREATE INDEX IF NOT EXISTS idx_events_event_time ON events (event_time);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events (event_type);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events (user_id);
