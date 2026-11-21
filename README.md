# US Market Reader
미국 증시 뉴스(Fed, BLS, CNBC, MarketWatch, WSJ, NYT)를 하루 2번 자동 수집하고, 영어 단어를 누르면 뜻이 나오는 페이지.

## 설정 (한 번만)
1. 이 파일들을 GitHub 저장소 루트에 업로드 (`.github` 폴더 포함)
2. Settings → Pages → Branch: `main` / `(root)` 저장
3. Settings → Actions → General → Workflow permissions → **Read and write permissions**
4. Actions 탭 → "Update news" → Run workflow (첫 `news.json` 생성)
5. `https://<아이디>.github.io/<저장소>/` 접속 (폰 홈 화면에 추가하면 앱처럼 사용)
