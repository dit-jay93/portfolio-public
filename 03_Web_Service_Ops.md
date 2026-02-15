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
