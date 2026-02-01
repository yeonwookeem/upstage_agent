"""
Slack 메시지 전송 서비스
"""
import requests
from typing import Dict, List
from utils.config import Config


class SlackService:
    """Slack API 연동 클래스"""
    
    def __init__(self):
        self.webhook_url = Config.SLACK_WEBHOOK_URL
        self.bot_token = Config.SLACK_BOT_TOKEN
    
    def send_pr_review(
        self,
        pr_info: Dict,
        analysis: Dict,
        pr_url: str
    ) -> bool:
        """
        PR 리뷰 결과를 Slack으로 전송
        
        Args:
            pr_info: PR 정보 딕셔너리
            analysis: LLM 분석 결과
            pr_url: PR URL
            
        Returns:
            bool: 전송 성공 여부
        """
        message = self.format_review_message(pr_info, analysis, pr_url)
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            print("✅ Slack 메시지 전송 완료!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Slack 메시지 전송 실패: {e}")
            return False
    
    def format_review_message(
        self,
        pr_info: Dict,
        analysis: Dict,
        pr_url: str
    ) -> Dict:
        """
        Slack 메시지 포맷팅 (Block Kit 사용)
        
        Args:
            pr_info: PR 정보
            analysis: 분석 결과
            pr_url: PR URL
            
        Returns:
            Dict: Slack 메시지 페이로드
        """
        # 위험도별 이모지
        severity_emoji = {
            "높음": "🔴",
            "중간": "🟡",
            "낮음": "🟢"
        }
        
        # 우선순위별 이모지
        priority_emoji = {
            "필수": "‼️",
            "권장": "💡",
            "선택": "💭"
        }
        
        blocks = [
            # 헤더
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔍 PR 리뷰 분석 결과",
                    "emoji": True
                }
            },
            {"type": "divider"},
            
            # PR 정보
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*📋 제목:*\n{pr_info.get('title', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*👤 작성자:*\n@{pr_info.get('author', 'unknown')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*🌿 브랜치:*\n`{pr_info.get('head_branch', '?')}` → `{pr_info.get('base_branch', '?')}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*⭐ 평가:*\n{analysis.get('overall_rating', 'N/A')}/10"
                    }
                ]
            },
            {"type": "divider"},
            
            # 요약
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📊 요약*\n{analysis.get('summary', '분석 결과 없음')}"
                }
            }
        ]
        
        # 위험 요소
        risks = analysis.get('risks', [])
        if risks:
            risk_text = "*⚠️ 위험 요소*\n"
            for i, risk in enumerate(risks, 1):
                emoji = severity_emoji.get(risk.get('severity', '낮음'), '⚪')
                severity = risk.get('severity', '알 수 없음')
                category = risk.get('category', '기타')
                description = risk.get('description', '')
                location = risk.get('location', '')
                
                risk_text += f"{emoji} *[{severity} - {category}]* {description}"
                if location and location != "N/A":
                    risk_text += f" `({location})`"
                risk_text += "\n"
            
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": risk_text
                }
            })
        
        # 개선 제안
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            suggestion_text = "*💡 리뷰 제안*\n"
            for i, suggestion in enumerate(suggestions, 1):
                emoji = priority_emoji.get(suggestion.get('priority', '선택'), '•')
                priority = suggestion.get('priority', '선택')
                description = suggestion.get('description', '')
                
                suggestion_text += f"{emoji} *[{priority}]* {description}\n"
            
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": suggestion_text
                }
            })
        
        # 긍정적인 점
        positive_points = analysis.get('positive_points', [])
        if positive_points:
            positive_text = "*✨ 잘한 점*\n"
            for point in positive_points:
                positive_text += f"• {point}\n"
            
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": positive_text
                }
            })
        
        # PR 링크 버튼
        blocks.append({"type": "divider"})
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔗 PR 보기",
                        "emoji": True
                    },
                    "url": pr_url,
                    "style": "primary"
                }
            ]
        })
        
        return {
            "blocks": blocks,
            "text": f"PR 리뷰: {pr_info.get('title', 'N/A')}"  # 알림용 fallback 텍스트
        }
    
    def send_error_notification(self, error_message: str, pr_url: str = None) -> bool:
        """
        에러 알림 전송
        
        Args:
            error_message: 에러 메시지
            pr_url: PR URL (선택사항)
            
        Returns:
            bool: 전송 성공 여부
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚠️ PR 분석 오류",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{error_message}```"
                }
            }
        ]
        
        if pr_url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "PR 확인",
                            "emoji": True
                        },
                        "url": pr_url
                    }
                ]
            })
        
        message = {
            "blocks": blocks,
            "text": "PR 분석 중 오류 발생"
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ 에러 알림 전송 실패: {e}")
            return False
