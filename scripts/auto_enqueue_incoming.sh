#!/usr/bin/env bash
set -euo pipefail

IN_DIR="<NAS_ROOT>/06_MEDIA/incoming"
OUT_DIR="<NAS_ROOT>/06_MEDIA/outcoming"
STATE_DIR="<NAS_ROOT>/06_MEDIA/.state"
JOB_DIR="/data/jobs"

# 기본 프록시 인코딩 설정 (속도 우선)
FFARGS='-c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k'

mkdir -p "$IN_DIR" "$OUT_DIR" "$STATE_DIR" "$JOB_DIR"
echo "[$(date '+%F %T')] auto-enqueue watcher started"

while true; do
  mapfile -t FILES < <(find "$IN_DIR" -maxdepth 1 -type f \( \
    -iname "*.mp4" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.avi" -o -iname "*.mxf" -o -iname "*.m4v" \
  \) ! -name '._*' | sort)

  for f in "${FILES[@]}"; do
    bn="$(basename "$f")"
    stem="${bn%.*}"

    # 파일 복사 중일 수 있으니 최근 60초 이내 변경 파일은 스킵
    now=$(date +%s)
    mtime=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    age=$((now - mtime))
    if [ "$age" -lt 60 ]; then
      continue
    fi

    marker="$STATE_DIR/${stem}.queued"
    [ -f "$marker" ] && continue

    out="$OUT_DIR/${stem}_proxy.mp4"
    job="$JOB_DIR/job-$(date +%s)-$RANDOM.job"

    cat > "$job" <<EOF
INPUT=$f
OUTPUT=$out
ARGS=$FFARGS
EOF

    touch "$marker"
    echo "[$(date '+%F %T')] queued: $bn -> $(basename "$out")"
  done

  sleep 10
done
