# 빠른 시작 가이드 (Quick Start)

이 가이드를 따라하면 5분 안에 PR Review Agent를 실행할 수 있습니다.

## 사전 준비물

- Python 3.9 이상
- GitHub 계정
- Slack 워크스페이스
- Upstage 계정

## 1단계: 프로젝트 설정 (1분)

```bash
# 저장소 클론
git clone https://github.com/yourusername/pr-review-agent.git
cd pr-review-agent

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 2단계: 환경변수 설정 (2분)

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일을 열어서 다음 항목들을 입력하세요:

### 필수 입력 항목

1. **UPSTAGE_API_KEY**: [여기서 발급](https://console.upstage.ai/)
2. **GITHUB_TOKEN**: [여기서 발급](https://github.com/settings/tokens)
3. **GITHUB_WEBHOOK_SECRET**: 아래 명령어로 생성
   ```bash
   openssl rand -hex 32
   ```
4. **SLACK_WEBHOOK_URL**: [여기서 발급](https://api.slack.com/apps)

## 3단계: 애플리케이션 실행 (1분)

```bash
# 서버 시작
python app.py
```

성공 메시지가 나타나면 준비 완료!
```
✅ 환경변수 검증 완료
🚀 PR Review Agent 시작...
   Host: 0.0.0.0
   Port: 5000
   Debug: False
```

## 4단계: GitHub Webhook 연결 (1분)

### 로컬 테스트 (ngrok 사용)

다른 터미널에서:
```bash
# ngrok 설치 (macOS)
brew install ngrok

# ngrok 실행
ngrok http 5000
```

ngrok URL을 복사하고 (예: `https://abcd1234.ngrok.io`):

1. GitHub 저장소 → Settings → Webhooks → Add webhook
2. **Payload URL**: `https://abcd1234.ngrok.io/webhook/github`
3. **Content type**: `application/json`
4. **Secret**: `.env`의 `GITHUB_WEBHOOK_SECRET` 값
5. **Events**: Pull requests만 선택
6. Add webhook 클릭

## 5단계: 테스트 (30초)

1. GitHub에서 테스트 PR 생성
2. Slack 채널 확인 - 자동 리뷰 메시지가 도착합니다!

## 테스트 명령어

```bash
# 헬스 체크
curl http://localhost:5000/

# 수동 분석 테스트
python test_script.py analyze owner/repo PR번호
```

## 다음 단계

- [상세 설정 가이드](./SETUP_GUIDE.md) 읽기
- [README](./README.md)에서 고급 기능 확인
- 프로덕션 배포를 위한 Docker 사용

## 문제가 생겼나요?

1. **로그 확인**: `tail -f app.log`
2. **환경변수 확인**: `.env` 파일의 모든 키가 올바른지 확인
3. **Webhook 확인**: GitHub에서 Recent Deliveries 확인

더 많은 도움이 필요하면 [SETUP_GUIDE.md](./SETUP_GUIDE.md)를 참고하세요!
