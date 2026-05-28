#!/bin/bash

# 명령어 로그 저장용 디렉토리 및 파일 설정
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/command_history.log"

mkdir -p "$LOG_DIR"

if [ $# -eq 0 ]; then
    echo "❌ 실행할 명령어를 전달해주세요."
    echo "사용법: ./run.sh [명령어]"
    echo "예시  : ./run.sh python3 generator.py"
    exit 1
fi

COMMAND="$*"
START_TIME=$(date "+%Y-%m-%d %H:%M:%S")
START_EPOCH=$(date +%s)

echo "🚀 [$(date '+%H:%M:%S')] 실행 중: $COMMAND"
echo "--------------------------------------------------"

# 명령어 실행
eval "$COMMAND"
EXIT_CODE=$?

END_TIME=$(date "+%Y-%m-%d %H:%M:%S")
END_EPOCH=$(date +%s)
DURATION=$((END_EPOCH - START_EPOCH))

echo "--------------------------------------------------"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ [$(date '+%H:%M:%S')] 성공 완료 (소요 시간: ${DURATION}초)"
else
    echo "❌ [$(date '+%H:%M:%S')] 실패 완료 (에러 코드: $EXIT_CODE, 소요 시간: ${DURATION}초)"
fi

# 로그 기록 저장
echo "[$START_TIME ~ $END_TIME] (소요: ${DURATION}초) [종료코드: $EXIT_CODE] [사용자: $USER] -> $COMMAND" >> "$LOG_FILE"
