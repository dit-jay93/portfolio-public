# Artifact Index (실경로 기반)

## 핵심 코드/설정
- 인코딩 클러스터
  - `<WORKSPACE_ROOT>/encoding-cluster/docker-compose.yml`
  - `<WORKSPACE_ROOT>/encoding-cluster/docker-compose.gpu.yml`
  - `<WORKSPACE_ROOT>/encoding-cluster/worker.sh`
  - `<WORKSPACE_ROOT>/encoding-cluster/auto_enqueue_incoming.sh`

- 파이프라인
  - `<WORKSPACE_ROOT>/pipeline/linux_scheduler.sh`
  - `<WORKSPACE_ROOT>/pipeline/resolve_export_job.py`
  - `<WORKSPACE_ROOT>/pipeline/job.schema.json`

- 모니터링
  - `<WORKSPACE_ROOT>/monitoring/docker-compose.yml`
  - `<WORKSPACE_ROOT>/monitoring/prometheus.yml`
  - `<WORKSPACE_ROOT>/monitoring/promtail-config.yml`
  - `<WORKSPACE_ROOT>/monitoring/loki-config.yaml`

- 웹 서비스
  - `/etc/nginx/sites-available/portfolio`
  - `/etc/nginx/sites-available/jarvis-voice`

## 데이터 경로
- NAS 루트: `<NAS_ROOT>`
- 파이프라인 데이터: `<NAS_ROOT>/06_MEDIA`
- SFTP 프로젝트 예시: `<NAS_ROOT>/00_INBOX/sftp/PRJ999`

## 제출용 첨부 권장
- 구성도 이미지(수기/다이어그램 툴)
- 운영 화면 캡처(Grafana, Dozzle)
- 파이프라인 성공 로그 샘플(queued/start/done)
- 서비스 접속 URL 캡처(포트폴리오/운영 페이지)
