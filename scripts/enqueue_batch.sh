#!/usr/bin/env bash
set -euo pipefail

# 동시 작업 큐 등록 스크립트
# 사용법:
# ./enqueue_batch.sh <입력디렉토리> <출력디렉토리> [동시작업수] [ffmpeg 인자]
# 예시:
# ./enqueue_batch.sh <NAS_ROOT>/in <NAS_ROOT>/out 6 "-c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k"

INPUT_DIR="${1:-}"
OUTPUT_DIR="${2:-}"
CONCURRENCY="${3:-3}"
FFARGS="${4:--c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k}"

if [[ -z "$INPUT_DIR" || -z "$OUTPUT_DIR" ]]; then
  echo "사용법: ./enqueue_batch.sh <입력디렉토리> <출력디렉토리> [동시작업수] [ffmpeg 인자]"
  exit 1
fi

if ! [[ "$CONCURRENCY" =~ ^[0-9]+$ ]] || [[ "$CONCURRENCY" -lt 1 ]]; then
  echo "동시작업수는 1 이상의 정수여야 합니다."
  exit 1
fi

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "입력 디렉토리가 없습니다: $INPUT_DIR"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

mapfile -t FILES < <(find "$INPUT_DIR" -maxdepth 1 -type f \( \
  -iname "*.mp4" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.avi" -o -iname "*.mxf" \
\) | sort)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "입력 영상 파일이 없습니다: $INPUT_DIR"
  exit 1
fi

echo "총 ${#FILES[@]}개 파일 큐 등록 시작 (동시작업수=$CONCURRENCY)"

# 큐 파일명에 슬롯 번호를 붙여 워커들이 자연스럽게 분산 처리되도록 함
slot=0
for f in "${FILES[@]}"; do
  base="$(basename "$f")"
  name="${base%.*}"
  out="$OUTPUT_DIR/${name}_h264.mp4"

  ./enqueue.sh "$f" "$out" "$FFARGS"
  slot=$(( (slot + 1) % CONCURRENCY ))
done

echo "큐 등록 완료"
echo "진행 확인: docker compose logs -f"
echo "완료 확인: ls -l cluster-data/done | tail"
