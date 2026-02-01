# 설정 가이드

## 1. 환경변수 설정

### `.env` 파일 생성

```bash
cp .env.example .env
```

그 다음 `.env` 파일을 열어서 각 항목을 설정합니다.

### 필수 환경변수

#### 1. UPSTAGE_API_KEY
Upstage Solar Pro API 키를 발급받아 입력합니다.

**발급 방법:**
1. https://console.upstage.ai/ 접속
2. 회원가입 또는 로그인
3. 좌측 메뉴에서 "API Keys" 클릭
4. "Create API Key" 버튼 클릭
5. 생성된 키를 복사하여 `.env` 파일에 입력

```env
UPSTAGE_API_KEY=up_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 2. GITHUB_TOKEN
GitHub Personal Access Token을 생성하여 입력합니다.

**발급 방법:**
1. GitHub 로그인 → 우측 상단 프로필 클릭 → Settings
2. 좌측 하단 "Developer settings" 클릭
3. "Personal access tokens" → "Tokens (classic)" 클릭
4. "Generate new token" → "Generate new token (classic)" 클릭
5. Note: "PR Review Agent" (설명 입력)
6. Expiration: 원하는 만료 기간 선택
7. 권한 선택:
   - `repo` (전체 선택)
   - `admin:repo_hook` (Webhooks 관리)
8. "Generate token" 클릭
9. 생성된 토큰을 **반드시** 복사 (다시 볼 수 없습니다!)

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 3. GITHUB_WEBHOOK_SECRET
Webhook 보안을 위한 비밀 키를 생성합니다.

**생성 방법:**
```bash
# 터미널에서 실행
openssl rand -hex 32
```

또는 온라인 생성기 사용: https://www.random.org/strings/

```env
GITHUB_WEBHOOK_SECRET=your_generated_secret_here
```

#### 4. SLACK_WEBHOOK_URL
Slack Incoming Webhook URL을 생성하여 입력합니다.

**발급 방법:**
1. https://api.slack.com/apps 접속
2. "Create New App" 클릭
3. "From scratch" 선택
4. App Name: "PR Review Bot" (원하는 이름)
5. Workspace 선택 후 "Create App"
6. 좌측 메뉴에서 "Incoming Webhooks" 클릭
7. "Activate Incoming Webhooks" 토글 켜기
8. 페이지 하단 "Add New Webhook to Workspace" 클릭
9. 메시지를 받을 채널 선택 (예: #dev-notifications)
10. "Allow" 클릭
11. 생성된 Webhook URL 복사

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

#### 5. SLACK_BOT_TOKEN (선택사항)
더 고급 기능을 위해 필요한 경우 설정합니다.

```env
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx
```

## 2. GitHub Webhook 설정

애플리케이션을 실행한 후 GitHub에서 Webhook을 설정합니다.

### 로컬 개발 환경 (ngrok 사용)

1. ngrok 설치
```bash
# macOS
brew install ngrok

# Windows
choco install ngrok

# 또는 https://ngrok.com/download 에서 다운로드
```

2. ngrok 실행
```bash
ngrok http 5000
```

3. ngrok이 제공하는 HTTPS URL 복사 (예: `https://abcd1234.ngrok.io`)

### GitHub에서 Webhook 설정

1. GitHub 저장소로 이동
2. "Settings" 탭 클릭
3. 좌측 메뉴에서 "Webhooks" 클릭
4. "Add webhook" 버튼 클릭
5. 설정 입력:
   - **Payload URL**: `https://your-domain.com/webhook/github`
     - 로컬 개발: `https://abcd1234.ngrok.io/webhook/github`
     - 프로덕션: 실제 서버 URL
   - **Content type**: `application/json`
   - **Secret**: `.env` 파일의 `GITHUB_WEBHOOK_SECRET` 값
   - **Which events would you like to trigger this webhook?**
     - "Let me select individual events" 선택
     - "Pull requests" 체크
   - **Active** 체크
6. "Add webhook" 클릭

### Webhook 테스트

1. GitHub Webhook 설정 페이지에서 "Recent Deliveries" 탭 확인
2. 테스트 PR 생성
3. Webhook이 정상적으로 전달되는지 확인
4. 서버 로그 확인: `tail -f app.log`

## 3. 실행 확인

### 헬스 체크
```bash
curl http://localhost:5000/
```

예상 응답:
```json
{
  "status": "healthy",
  "service": "PR Review Agent",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 수동 테스트
```bash
python test_script.py health
python test_script.py analyze owner/repo 1
```

## 4. 문제 해결

### Webhook이 동작하지 않는 경우

1. **서명 검증 실패**
   - `.env`의 `GITHUB_WEBHOOK_SECRET`가 GitHub 설정과 일치하는지 확인
   - GitHub Webhook 설정에서 Secret을 다시 입력

2. **API 응답 없음**
   - 서버 로그 확인: `tail -f app.log`
   - 네트워크 연결 확인
   - API 키가 올바른지 확인

3. **ngrok 세션 만료**
   - ngrok을 재시작하면 URL이 변경됩니다
   - 무료 플랜은 8시간마다 재시작 필요
   - GitHub Webhook URL을 새 ngrok URL로 업데이트

4. **Slack 메시지 전송 실패**
   - Webhook URL이 올바른지 확인
   - Slack 앱이 채널에 추가되었는지 확인
   - Webhook URL 재생성 후 다시 시도

### 로그 확인
```bash
# 실시간 로그 확인
tail -f app.log

# 최근 100줄 확인
tail -n 100 app.log

# 에러만 필터링
grep "ERROR" app.log
```

## 5. 프로덕션 배포

### Docker Compose 사용
```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 일반 서버 배포
```bash
# Gunicorn으로 실행
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app

# 또는 systemd 서비스로 등록
sudo systemctl enable pr-review-agent
sudo systemctl start pr-review-agent
```

### Nginx 리버스 프록시 설정
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6. 보안 권장사항

1. **API 키 관리**
   - `.env` 파일을 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인
   - 프로덕션 환경에서는 환경변수 관리 도구 사용 (AWS Secrets Manager, HashiCorp Vault 등)

2. **Webhook Secret**
   - 강력한 랜덤 문자열 사용 (최소 32자)
   - 정기적으로 변경

3. **HTTPS 사용**
   - 프로덕션 환경에서는 반드시 HTTPS 사용
   - Let's Encrypt로 무료 SSL 인증서 발급

4. **접근 제한**
   - 필요한 경우 IP 화이트리스트 설정
   - GitHub Webhook에서만 접근 가능하도록 제한
