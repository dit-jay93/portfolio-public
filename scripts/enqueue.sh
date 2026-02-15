#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "사용법: ./enqueue.sh <입력파일> <출력파일> [ffmpeg 인자...]"
  echo "예시: ./enqueue.sh ./cluster-data/input/a.mov ./cluster-data/output/a_h264.mp4 \"-c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k\""
  exit 1
fi

INPUT="$1"
OUTPUT="$2"
ARGS="${3:--c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k}"

# 컨테이너 내부 경로로 자동 변환
# ./cluster-data/... 또는 cluster-data/... 로 넣으면 /data/... 로 치환
if [[ "$INPUT" == ./cluster-data/* ]]; then
  INPUT="/data/${INPUT#./cluster-data/}"
elif [[ "$INPUT" == cluster-data/* ]]; then
  INPUT="/data/${INPUT#cluster-data/}"
fi

if [[ "$OUTPUT" == ./cluster-data/* ]]; then
  OUTPUT="/data/${OUTPUT#./cluster-data/}"
elif [[ "$OUTPUT" == cluster-data/* ]]; then
  OUTPUT="/data/${OUTPUT#cluster-data/}"
fi

mkdir -p ./cluster-data/jobs
id="$(date +%s)-$RANDOM"
job="./cluster-data/jobs/job-$id.job"

cat > "$job" <<EOF
INPUT=$INPUT
OUTPUT=$OUTPUT
ARGS=$ARGS
EOF

echo "작업 등록 완료: $job"
