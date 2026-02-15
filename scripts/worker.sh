#!/usr/bin/env bash
set -euo pipefail

mkdir -p /data/jobs /data/processing /data/done /data/failed /data/logs

echo "[$(date '+%F %T')] worker started: $(hostname)"

while true; do
  shopt -s nullglob
  jobs=(/data/jobs/*.job)

  if [ ${#jobs[@]} -eq 0 ]; then
    sleep 2
    continue
  fi

  for job in "${jobs[@]}"; do
    base="$(basename "$job")"
    proc="/data/processing/$base"

    if mv "$job" "$proc" 2>/dev/null; then
      ts="$(date +%s)"
      log="/data/logs/${base%.job}_$ts.log"

      INPUT="$(grep '^INPUT=' "$proc" | sed 's/^INPUT=//')"
      OUTPUT="$(grep '^OUTPUT=' "$proc" | sed 's/^OUTPUT=//')"
      ARGS="$(grep '^ARGS=' "$proc" | sed 's/^ARGS=//')"

      echo "[$(date '+%F %T')] start $base" | tee -a "$log"
      echo "INPUT=$INPUT" | tee -a "$log"
      echo "OUTPUT=$OUTPUT" | tee -a "$log"
      echo "ARGS=$ARGS" | tee -a "$log"

      if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
        echo "invalid job format" | tee -a "$log"
        mv "$proc" "/data/failed/$base"
        continue
      fi

      mkdir -p "$(dirname "$OUTPUT")"

      if ffmpeg -hide_banner -y -i "$INPUT" $ARGS "$OUTPUT" >>"$log" 2>&1; then
        echo "[$(date '+%F %T')] done $base" | tee -a "$log"
        mv "$proc" "/data/done/$base"
      else
        echo "[$(date '+%F %T')] failed $base" | tee -a "$log"
        mv "$proc" "/data/failed/$base"
      fi
    fi
  done

done
