-- Step 3. 데이터 집계 분석

-- 1) 이벤트 타입별 발생 횟수
SELECT event_type, COUNT(*) AS event_count
FROM events
GROUP BY event_type
ORDER BY event_count DESC;

-- 2) 전체 이벤트 추이
SELECT date_trunc('hour', event_time AT TIME ZONE 'Asia/Seoul')
       + INTERVAL '10 minutes' * FLOOR(EXTRACT(MINUTE FROM event_time AT TIME ZONE 'Asia/Seoul') / 10) AS event_time_10m,
       COUNT(*) AS event_count
FROM events
GROUP BY event_time_10m
ORDER BY event_time_10m;

-- 3) 유저별 총 이벤트 수
SELECT user_id, COUNT(*) AS event_count
FROM events
GROUP BY user_id
ORDER BY event_count DESC, user_id ASC
LIMIT 10;

-- 4) 유저별 평균 이벤트 수
SELECT date_trunc('hour', event_time AT TIME ZONE 'Asia/Seoul')
       + INTERVAL '10 minutes' * FLOOR(EXTRACT(MINUTE FROM event_time AT TIME ZONE 'Asia/Seoul') / 10) AS event_time_10m,
       ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT user_id), 0), 2) AS avg_events_per_user
FROM events
WHERE $__timeFilter(event_time AT TIME ZONE 'Asia/Seoul')
GROUP BY event_time_10m
ORDER BY event_time_10m;
