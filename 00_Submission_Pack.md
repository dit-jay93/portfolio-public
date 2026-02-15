# R&D 경력기술 증빙 패키지

- 작성일: 2026-02
- 작성자: Jay
- 목적: 이력서/경력기술서 첨부용 증빙 문서

---

## 목차
1. R&D 요약
2. Media Infra Home Lab
3. Web Service Ops
4. Pipeline Experiment
5. Artifact Index

---

# 1) R&D 요약

# R&D 요약 (이력서 첨부용)

## 1) Media Infra Home Lab
- **내용**: Linux(Ubuntu) 서버 구축, NAS 공유(SMB/NFS), VM/Docker 환경 구성
- **핵심 수행**:
  - Ubuntu 서버 운영 환경 정비
  - SMB/NFS 접근 정책 및 권한 구조 실험/정리
  - Docker 기반 서비스 운영(인코딩/모니터링)
- **산출물**:
  - 구성도 문서
  - 운영 체크리스트
  - 서비스별 설정/운영 스크립트

## 2) Web Service Ops
- **내용**: Nginx/HTTP(S) 운영, 도메인 연결, 포트폴리오 사이트 배포
- **핵심 수행**:
  - Nginx 리버스프록시/정적서빙 설정
  - 도메인 라우팅/SSL 인증서 적용
  - 포트/접근 정책 점검
- **산출물**:
  - 서비스 URL 목록
  - 배포/운영 메모
  - 점검 명령어 세트

## 3) Pipeline Experiment
- **내용**: 클러스터/파일/권한/전송/모니터링 운영 실험
- **핵심 수행**:
  - `incoming -> queue -> worker -> outcoming` 파이프라인 구현
  - Resolve 연동 Job Manifest 생성 스크립트 구성
  - 권한/경로/유니코드 파일명 이슈 분석 및 보완
  - Grafana/Prometheus/Loki/Dozzle/DCGM 모니터링 운영
- **산출물**:
  - 실험 문서
  - 운영 스크립트(스케줄러/워커/보조 스크립트)
  - 점검 로그 및 운영 메모


---

# 2) Media Infra Home Lab

# Media Infra Home Lab 증빙

## A. 아키텍처 구성도 (요약)
```text
[Client Mac/PC]
   |  SMB / SFTP / HTTPS
   v
[Ubuntu Server]
  - Nginx
  - Samba (SMB)
  - SSH/SFTP
  - Docker (Encoding/Monitoring)
  - Scheduler Scripts
   |
   +--> [<NAS_ROOT>]  (NAS 데이터 루트)
   +--> [Docker Volumes / Cluster Data]
```

## B. 운영 체크리스트

### 1) 서버 기본 상태
- [ ] OS/서비스 상태 확인 (`openclaw status`, `systemctl status`)
- [ ] 디스크 여유공간/마운트 상태 확인
- [ ] 네트워크 인터페이스(Tailscale 포함) 확인

### 2) 공유/전송
- [ ] SMB 접근 가능 여부(권한/가시성)
- [ ] SFTP 계정별 chroot/권한 확인
- [ ] 필요 시 NFS 접근 정책 확인

### 3) 보안/접근제어
- [ ] 외부 공개 포트(22/80/443) 정책 확인
- [ ] 모니터링 포트 tailnet 바인딩 확인
- [ ] SMB allow/deny 정책 확인

### 4) 운영 안정성
- [ ] 서비스 자동시작(enable) 확인
- [ ] 장애 시 재시작 절차 문서 확인
- [ ] 백업/복구 경로 확인

## C. 핵심 운영 포인트
- 운영 경로 표준화: `<NAS_ROOT>`
- 업무 폴더 표준화: `00_INBOX`, `06_MEDIA`, `08_PIPELINE` 등
- 권한 정책/경로 정책 불일치 시 즉시 로그 기반 원인 분리


---

# 3) Web Service Ops

# Web Service Ops 증빙

## A. 서비스/도메인
- Portfolio: `https://<PORTFOLIO_DOMAIN_REDACTED>`
- Jarvis Voice(운영 엔드포인트): `https://<SERVICE_DOMAIN_REDACTED>`

> 실제 제출 시 최신 도메인/상태 스크린샷 첨부 권장

## B. 배포/운영 메모
- Nginx 기반 정적 사이트/프록시 라우팅 구성
- HTTP(80) -> HTTPS(443) 리다이렉트 구성
- SSL 인증서(Let's Encrypt) 적용 및 서버 블록 분리
- 기본 default site 비활성화로 불필요 노출 축소

## C. 점검 명령 (운영 체크용)
```bash
# nginx 구성 확인
sudo nginx -t

# 활성 사이트 확인
ls -l /etc/nginx/sites-enabled

# 리스닝 포트 확인
ss -lntp | grep -E ':80|:443'
```

## D. 리스크/대응 요약
- 리스크: 잘못된 server block 우선순위, 인증서 갱신 실패, 불필요 포트 노출
- 대응: 구성 검증 자동화(`nginx -t`), 포트 제한, 서비스별 분리 설정


---

# 4) Pipeline Experiment

# Pipeline Experiment 증빙

## A. 실험 목표
- 미디어 파일 자동 인코딩 파이프라인 구축
- DaVinci Resolve 작업 지시와 서버 처리 자동 연결
- 운영 이슈(권한/경로/인코딩/모니터링) 재현 및 해결

## B. 파이프라인 흐름
```text
Resolve Script(UI)
  -> incoming_jobs/*.json
  -> linux_scheduler.sh
  -> cluster-data/jobs/*.job
  -> Docker workers(ffmpeg)
  -> outcoming 결과물
```

## C. 주요 구성 요소
- 인코딩 클러스터: `encoding-cluster/`
- 스케줄러: `pipeline/linux_scheduler.sh`
- Resolve 연동: `pipeline/resolve_export_job.py`
- 자동 ingest: `encoding-cluster/auto_enqueue_incoming.sh`

## D. 운영 실험 이슈 & 대응
1) 권한 이슈(`Permission denied`)
- 원인: 공유 경로 소유권/마스크 불일치
- 대응: 계정/그룹 권한 정렬 및 서비스 설정 일관화

2) 경로 이슈(SMB/NFS 혼선)
- 원인: 클라이언트 경로와 서버 경로 불일치
- 대응: 운영 표준 경로 고정 및 스크립트 경로 통일

3) 인코딩 경로(CPU/GPU)
- ProRes: CPU 경로
- H.264/H.265: NVENC 경로 분리

4) 모니터링 재시작 루프
- 원인: 볼륨 권한/쓰기 권한 문제
- 대응: named volume 및 권한 재정렬

## E. 관측성 스택
- Dozzle / Grafana / Loki / Promtail / Prometheus / DCGM exporter
- 로그 + 메트릭 통합 모니터링으로 장애 탐지/원인 분석


---

# 5) Artifact Index

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
