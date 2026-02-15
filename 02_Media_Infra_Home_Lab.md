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
