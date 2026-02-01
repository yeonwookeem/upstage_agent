"""
환경변수 관리 모듈
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Config:
    """환경변수 설정 클래스"""
    
    # Upstage API
    UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')
    UPSTAGE_API_URL = 'https://api.upstage.ai/v1/solar/chat/completions'
    
    # GitHub
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
    GITHUB_API_URL = 'https://api.github.com'
    
    # Slack
    SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    
    # Server
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """필수 환경변수 검증"""
        required_vars = [
            'UPSTAGE_API_KEY',
            'GITHUB_TOKEN',
            'GITHUB_WEBHOOK_SECRET',
            'SLACK_WEBHOOK_URL'
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(
                f"다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}\n"
                f".env 파일을 확인해주세요."
            )
        
        return True


# 설정 검증
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  경고: {e}")
