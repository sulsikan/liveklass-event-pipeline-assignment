-- Step 3. 데이터 집계 분석

-- 1) 이벤트 타입별 발생 횟수
SELECT event_type, COUNT(*) AS event_count
FROM events
GROUP BY event_type
ORDER BY event_count DESC;

-- 2) 시간대별 이벤트 추이
SELECT DATE_TRUNC('hour', event_time) AS event_hour,
       COUNT(*) AS event_count
FROM events
GROUP BY event_hour
ORDER BY event_hour;

-- 3) 유저별 총 이벤트 수
SELECT user_id, COUNT(*) AS event_count
FROM events
GROUP BY user_id
ORDER BY event_count DESC, user_id ASC
LIMIT 10;
