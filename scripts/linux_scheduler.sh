#!/usr/bin/env bash
set -euo pipefail

# Docker 노드용 Scheduler (SSH 없음)
# 역할:
# 1) incoming_jobs/*.json 감시
# 2) JSON -> ffmpeg .job 변환
# 3) encoding-cluster/cluster-data/jobs 로 투입
# 4) 상태 디렉토리(queued/invalid) 관리

BASE="<NAS_ROOT>/06_MEDIA"
INCOMING_JOBS="$BASE/incoming_jobs"
QUEUED="$BASE/queue"
INVALID="$BASE/invalid"
LOGS="$BASE/logs"

# encoding-cluster 쪽 큐 디렉토리
CLUSTER_DIR="<WORKSPACE_ROOT>/encoding-cluster/cluster-data"
JOBS_DIR="$CLUSTER_DIR/jobs"

mkdir -p "$INCOMING_JOBS" "$QUEUED" "$INVALID" "$LOGS" "$JOBS_DIR"

log() { echo "[$(date '+%F %T')] $*" | tee -a "$LOGS/scheduler.log"; }

# python3로 안전하게 JSON 파싱해서 INPUT/OUTPUT/ARGS 추출
json_to_env() {
  local jf="$1"
  python3 - "$jf" <<'PY'
import json,sys,os
p=sys.argv[1]
with open(p,'r',encoding='utf-8') as f:
    j=json.load(f)

# 스키마 최소 호환:
# source.input_files[0], target.output_path, target.filename, render.ffmpeg_args
try:
    input_file = j["source"]["input_files"][0]
    out_path = j["target"]["output_path"]
    out_name = j["target"]["filename"]
except Exception as e:
    print(f"ERROR=missing_required_fields:{e}")
    sys.exit(0)

ffargs = j.get("render",{}).get("ffmpeg_args", "-c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k")
output_file = os.path.join(out_path, out_name)

print(f"INPUT={input_file}")
print(f"OUTPUT={output_file}")
print(f"ARGS={ffargs}")
PY
}

resolve_input_path() {
  local p="$1"
  python3 - "$p" <<'PY'
import os, sys, unicodedata
p = sys.argv[1]
if os.path.isfile(p):
    print(p)
    raise SystemExit(0)

dirname = os.path.dirname(p) or "."
base = os.path.basename(p)
if not os.path.isdir(dirname):
    print("")
    raise SystemExit(0)

def norm(s):
    return unicodedata.normalize("NFC", s)

want = norm(base)
for name in os.listdir(dirname):
    if norm(name) == want:
        cand = os.path.join(dirname, name)
        if os.path.isfile(cand):
            print(cand)
            raise SystemExit(0)
print("")
PY
}

make_job_file() {
  local src_json="$1"
  local base job_file parsed input output args err resolved

  base="$(basename "$src_json" .json)"
  if ! parsed="$(json_to_env "$src_json" 2>/tmp/scheduler_json_err.log)"; then
    mv "$src_json" "$INVALID/$(basename "$src_json")"
    log "INVALID job=$(basename "$src_json") reason=json_parse_failed detail=$(tr '\n' ' ' </tmp/scheduler_json_err.log | sed 's/  */ /g')"
    return 1
  fi

  err="$(printf '%s\n' "$parsed" | sed -n 's/^ERROR=//p')"
  if [[ -n "$err" ]]; then
    mv "$src_json" "$INVALID/$(basename "$src_json")"
    log "INVALID job=$(basename "$src_json") reason=$err"
    return 1
  fi

  input="$(printf '%s\n' "$parsed" | sed -n 's/^INPUT=//p')"
  output="$(printf '%s\n' "$parsed" | sed -n 's/^OUTPUT=//p')"
  args="$(printf '%s\n' "$parsed" | sed -n 's/^ARGS=//p')"

  # 입력 파일 존재 확인 (macOS<->Linux 유니코드 정규화 차이 보정)
  resolved="$(resolve_input_path "$input")"
  if [[ -z "$resolved" || ! -f "$resolved" ]]; then
    mv "$src_json" "$INVALID/$(basename "$src_json")"
    log "INVALID job=$(basename "$src_json") reason=input_not_found input=$input"
    return 1
  fi
  input="$resolved"

  job_file="$JOBS_DIR/${base}.job"
  cat > "$job_file" <<EOF
INPUT=$input
OUTPUT=$output
ARGS=$args
EOF

  mv "$src_json" "$QUEUED/$(basename "$src_json")"
  log "QUEUED job=${base}.job input=$(basename "$input") output=$(basename "$output")"
  return 0
}

log "docker-node scheduler started"

while true; do
  shopt -s nullglob
  files=("$INCOMING_JOBS"/*.json)

  if [[ ${#files[@]} -eq 0 ]]; then
    sleep 2
    continue
  fi

  for jf in "${files[@]}"; do
    make_job_file "$jf" || true
  done

done
