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
