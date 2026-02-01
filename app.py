"""
PR 자동 분석 AI Agent - 메인 애플리케이션
"""
from flask import Flask, request, jsonify
import logging
from datetime import datetime

from utils.config import Config
from utils.webhook_validator import verify_github_signature
from services.github_service import GitHubService
from services.llm_service import LLMService
from services.slack_service import SlackService

# Flask 앱 초기화
app = Flask(__name__)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
github_service = GitHubService()
llm_service = LLMService()
slack_service = SlackService()


@app.route('/', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'service': 'PR Review Agent',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """
    GitHub Webhook 핸들러
    PR이 생성되면 자동으로 분석 실행
    """
    # 서명 검증
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_github_signature(
        request.data,
        signature,
        Config.GITHUB_WEBHOOK_SECRET
    ):
        logger.warning("⚠️ Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # 이벤트 타입 확인
    event_type = request.headers.get('X-GitHub-Event')
    
    if event_type != 'pull_request':
        logger.info(f"ℹ️ Ignoring event type: {event_type}")
        return jsonify({'message': 'Event type not supported'}), 200
    
    # 페이로드 파싱
    payload = request.json
    action = payload.get('action')
    
    # PR이 새로 생성된 경우에만 처리
    if action not in ['opened', 'synchronize', 'reopened']:
        logger.info(f"ℹ️ Ignoring PR action: {action}")
        return jsonify({'message': f'Action {action} not processed'}), 200
    
    try:
        # PR 정보 추출
        pr = payload['pull_request']
        pr_number = pr['number']
        repo_full_name = payload['repository']['full_name']
        pr_url = pr['html_url']
        
        pr_info = {
            'number': pr_number,
            'title': pr['title'],
            'author': pr['user']['login'],
            'base_branch': pr['base']['ref'],
            'head_branch': pr['head']['ref'],
            'description': pr.get('body', ''),
            'url': pr_url,
            'repo': repo_full_name
        }
        
        logger.info(f"🔔 새 PR 감지: {repo_full_name}#{pr_number}")
        
        # 백그라운드에서 처리 (실제 프로덕션에서는 큐 사용 권장)
        process_pr_review(pr_info)
        
        return jsonify({
            'message': 'PR review started',
            'pr_number': pr_number
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook 처리 중 오류: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def process_pr_review(pr_info: dict):
    """
    PR 리뷰 프로세스 실행
    
    Args:
        pr_info: PR 정보 딕셔너리
    """
    try:
        logger.info(f"🚀 PR 분석 시작: {pr_info['repo']}#{pr_info['number']}")
        
        # 1. GitHub에서 diff 가져오기
        logger.info("📥 Diff 가져오는 중...")
        diff = github_service.get_pr_diff(
            pr_info['repo'],
            pr_info['number']
        )
        
        if not diff:
            error_msg = "Failed to fetch PR diff"
            logger.error(f"❌ {error_msg}")
            slack_service.send_error_notification(error_msg, pr_info['url'])
            return
        
        # Diff 크기 확인 (너무 크면 잘라내기)
        formatted_diff = github_service.format_diff_for_analysis(diff, max_lines=500)
        logger.info(f"✅ Diff 가져오기 완료 ({len(diff.split(chr(10)))} 라인)")
        
        # 2. LLM으로 분석
        logger.info("🤖 LLM 분석 중...")
        analysis = llm_service.analyze_pr(
            title=pr_info['title'],
            author=pr_info['author'],
            base_branch=pr_info['base_branch'],
            head_branch=pr_info['head_branch'],
            description=pr_info['description'],
            diff=formatted_diff
        )
        
        if not analysis:
            logger.warning("⚠️ LLM 분석 실패, fallback 사용")
            analysis = llm_service.create_fallback_analysis(
                "LLM API 응답 실패"
            )
        
        logger.info("✅ 분석 완료")
        
        # 3. Slack으로 결과 전송
        logger.info("📤 Slack 전송 중...")
        success = slack_service.send_pr_review(
            pr_info=pr_info,
            analysis=analysis,
            pr_url=pr_info['url']
        )
        
        if success:
            logger.info(f"✅ PR 리뷰 완료: {pr_info['repo']}#{pr_info['number']}")
        else:
            logger.error(f"❌ Slack 전송 실패: {pr_info['repo']}#{pr_info['number']}")
        
        # 4. (선택사항) GitHub PR에도 코멘트 남기기
        # github_service.post_pr_comment(
        #     pr_info['repo'],
        #     pr_info['number'],
        #     "🤖 AI 코드 리뷰가 Slack으로 전송되었습니다!"
        # )
        
    except Exception as e:
        logger.error(f"❌ PR 리뷰 처리 중 오류: {e}", exc_info=True)
        slack_service.send_error_notification(
            f"PR 분석 중 오류 발생: {str(e)}",
            pr_info.get('url')
        )


@app.route('/test/analyze', methods=['POST'])
def test_analyze():
    """
    테스트용 수동 분석 엔드포인트
    
    Request Body:
    {
        "repo": "owner/repo",
        "pr_number": 123
    }
    """
    data = request.json
    
    if not data or 'repo' not in data or 'pr_number' not in data:
        return jsonify({
            'error': 'Missing required fields: repo, pr_number'
        }), 400
    
    try:
        repo = data['repo']
        pr_number = data['pr_number']
        
        # PR 정보 가져오기
        pr_details = github_service.get_pr_details(repo, pr_number)
        
        if not pr_details:
            return jsonify({'error': 'PR not found'}), 404
        
        pr_info = {
            'number': pr_number,
            'title': pr_details['title'],
            'author': pr_details['user']['login'],
            'base_branch': pr_details['base']['ref'],
            'head_branch': pr_details['head']['ref'],
            'description': pr_details.get('body', ''),
            'url': pr_details['html_url'],
            'repo': repo
        }
        
        # 분석 실행
        process_pr_review(pr_info)
        
        return jsonify({
            'message': 'Analysis started',
            'pr_info': pr_info
        }), 200
        
    except Exception as e:
        logger.error(f"❌ 수동 분석 중 오류: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 환경변수 검증
    try:
        Config.validate()
        logger.info("✅ 환경변수 검증 완료")
    except ValueError as e:
        logger.error(f"❌ 환경변수 검증 실패: {e}")
        exit(1)
    
    logger.info(f"🚀 PR Review Agent 시작...")
    logger.info(f"   Host: {Config.HOST}")
    logger.info(f"   Port: {Config.PORT}")
    logger.info(f"   Debug: {Config.DEBUG}")
    
    # Flask 앱 실행
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
