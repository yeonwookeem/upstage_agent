# PR 자동 분석 AI Agent

GitHub Pull Request가 생성되면 자동으로 코드를 분석하고 Slack으로 상세한 리뷰 리포트를 전송하는 AI Agent입니다.

## 주요 기능

- 🔍 **자동 코드 분석**: PR이 생성되면 변경된 코드(diff)를 자동으로 분석
- 🛡️ **보안 검사**: API Key 노출, 보안 취약점 탐지
- 🔄 **코드 품질 검토**: 중복 코드, 로직 개선 제안
- ✅ **테스트 검증**: 테스트 코드 누락 확인
- 📊 **Slack 리포트**: 요약, 위험요소, 리뷰 제안이 담긴 상세 리포트 전송

## 기술 스택

- **언어**: Python 3.9+
- **LLM**: Upstage Solar Pro
- **웹훅**: Flask
- **통합**: GitHub API, Slack API

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/pr-review-agent.git
cd pr-review-agent
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 값을 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```
# Upstage Solar Pro API
UPSTAGE_API_KEY=your_upstage_api_key_here

# GitHub
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Slack
SLACK_WEBHOOK_URL=your_slack_webhook_url
SLACK_BOT_TOKEN=your_slack_bot_token

# Server
PORT=5000
HOST=0.0.0.0
```

## API Key 발급 방법

### 1. Upstage Solar Pro API Key
1. [Upstage Console](https://console.upstage.ai/) 접속
2. 회원가입/로그인
3. API Keys 메뉴에서 새 키 생성
4. `UPSTAGE_API_KEY`에 입력

### 2. GitHub Token
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token 클릭
3. 권한 선택: `repo` (전체), `admin:repo_hook`
4. `GITHUB_TOKEN`에 입력

### 3. GitHub Webhook Secret
1. 임의의 강력한 비밀키 생성 (예: `openssl rand -hex 32`)
2. `GITHUB_WEBHOOK_SECRET`에 입력

### 4. Slack Webhook URL
1. [Slack API](https://api.slack.com/apps) → Create New App
2. "From scratch" 선택
3. Incoming Webhooks 활성화
4. "Add New Webhook to Workspace" 클릭
5. 채널 선택 후 Webhook URL 복사
6. `SLACK_WEBHOOK_URL`에 입력

## 실행 방법

### 로컬 개발 환경

```bash
python app.py
```

서버가 `http://0.0.0.0:5000`에서 실행됩니다.

### ngrok을 사용한 테스트 (로컬 환경)

```bash
# 다른 터미널에서
ngrok http 5000
```

ngrok이 제공하는 HTTPS URL을 GitHub Webhook URL로 사용합니다.

### 프로덕션 배포 (Docker)

```bash
docker build -t pr-review-agent .
docker run -p 5000:5000 --env-file .env pr-review-agent
```

## GitHub Webhook 설정

1. GitHub 저장소 → Settings → Webhooks → Add webhook
2. Payload URL: `https://your-server.com/webhook/github`
3. Content type: `application/json`
4. Secret: `.env`의 `GITHUB_WEBHOOK_SECRET` 값 입력
5. Events: "Let me select individual events" 선택 → `Pull requests` 체크
6. Active 체크 후 Add webhook

## 사용 예시

PR이 생성되면 Slack에 다음과 같은 메시지가 전송됩니다:

```
🔍 PR 리뷰 분석 결과

📋 PR 정보
• 제목: Add user authentication feature
• 작성자: @developer
• 브랜치: feature/auth → main

📊 요약
이 PR은 사용자 인증 기능을 추가합니다. JWT 토큰 기반 인증을 구현했으며, 
총 3개 파일이 수정되었습니다.

⚠️ 위험 요소
1. [높음] API Key가 코드에 하드코딩되어 있습니다 (auth.py:45)
2. [중간] SQL 쿼리에서 문자열 포매팅 사용 - SQL Injection 위험
3. [낮음] 에러 핸들링이 누락된 부분이 있습니다

💡 리뷰 제안
1. API Key를 환경변수로 이동하세요
2. ORM 또는 Parameterized Query 사용을 권장합니다
3. try-except 블록 추가를 고려하세요
4. 테스트 코드가 누락되었습니다 - 단위 테스트 추가 권장

🔗 PR 링크: https://github.com/user/repo/pull/123
```

## 프로젝트 구조

```
pr-review-agent/
├── app.py                 # 메인 애플리케이션
├── services/
│   ├── github_service.py  # GitHub API 연동
│   ├── llm_service.py     # Upstage Solar Pro 연동
│   └── slack_service.py   # Slack 메시지 전송
├── utils/
│   ├── config.py          # 환경변수 관리
│   └── webhook_validator.py  # Webhook 검증
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 설정
├── .env.example          # 환경변수 템플릿
├── .gitignore           # Git 무시 파일
└── README.md            # 문서
```

## 커스터마이징

### 분석 프롬프트 수정
`services/llm_service.py`의 `REVIEW_PROMPT` 변수를 수정하여 분석 방식을 커스터마이징할 수 있습니다.

### Slack 메시지 포맷 변경
`services/slack_service.py`의 `format_review_message()` 함수를 수정하여 메시지 형식을 변경할 수 있습니다.

## 문제 해결

### Webhook이 동작하지 않는 경우
1. GitHub Webhook 설정에서 Recent Deliveries 확인
2. 서버 로그 확인: `tail -f app.log`
3. Webhook Secret이 일치하는지 확인

### LLM 응답이 느린 경우
- `llm_service.py`의 `max_tokens` 값을 조정
- 비동기 처리 고려 (Celery, Redis Queue 등)

## 라이선스

MIT License

## 기여

PR과 이슈는 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
