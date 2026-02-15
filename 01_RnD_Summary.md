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
