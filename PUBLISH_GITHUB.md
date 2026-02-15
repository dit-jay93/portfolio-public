# GitHub 등록 가이드

이 환경에는 `gh` CLI가 없어 GitHub 원격 저장소 자동 생성은 불가합니다.
대신 아래 3줄로 바로 푸시할 수 있습니다.

```bash
cd <NAS_ROOT>/03_DOCS/resume_evidence_2026-02
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

> 예시 URL:
> - HTTPS: `https://github.com/<username>/<repo>.git`
> - SSH: `git@github.com:<username>/<repo>.git`

## 참고
- 현재 로컬 git commit은 완료되어 있습니다.
- 원격 repo만 생성해서 URL 넣으면 바로 업로드됩니다.
