# Project Summary (STAR)

## Situation
미디어 작업에서 파일 전송/권한/렌더가 분리되어 운영 복잡도가 높았음.

## Task
Resolve 작업 지시부터 서버 인코딩 결과물 산출까지 E2E 자동화.

## Action
- SMB/SFTP/Nginx 운영 표준화
- Docker 인코딩 클러스터 및 자동 큐 구축
- Resolve 연동 스크립트(UI) 개발
- 모니터링/로그 수집 체계 구축

## Result
- incoming -> queue -> worker -> outcoming 자동 처리 검증
- 운영 장애(권한/경로/재시작 루프) 재현 및 개선
