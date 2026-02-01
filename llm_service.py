"""
Upstage Solar Pro LLM 연동 서비스
"""
import requests
import json
from typing import Dict, Optional
from utils.config import Config


class LLMService:
    """Upstage Solar Pro 연동 클래스"""
    
    # 코드 리뷰 프롬프트
    REVIEW_PROMPT = """당신은 전문 코드 리뷰어입니다. 다음 Pull Request의 변경사항을 분석하고 상세한 리뷰를 제공해주세요.

# PR 정보
- 제목: {title}
- 작성자: {author}
- 브랜치: {base_branch} ← {head_branch}
- 설명: {description}

# 변경된 코드 (Diff)
```diff
{diff}
```

# 분석 요청사항

다음 항목들을 중심으로 코드를 분석해주세요:

## 1. 보안 검사
- API Key, 비밀번호, 토큰 등의 민감정보 노출 여부
- SQL Injection, XSS 등 보안 취약점
- 인증/인가 로직의 적절성
- 입력 검증 누락

## 2. 코드 품질
- 중복 코드 존재 여부
- 함수/변수 명명의 적절성
- 코드 복잡도 (너무 긴 함수, 깊은 중첩 등)
- 디자인 패턴 개선 가능성

## 3. 버그 가능성
- Null/Undefined 처리 누락
- 에러 핸들링 미비
- 경계 조건 처리
- 타입 불일치

## 4. 테스트
- 테스트 코드 존재 여부
- 테스트 커버리지 적절성
- Edge case 테스트 누락

## 5. 성능
- 불필요한 반복문이나 연산
- 메모리 누수 가능성
- 데이터베이스 쿼리 최적화 필요성

# 출력 형식

다음 JSON 형식으로 응답해주세요:

{{
  "summary": "전체적인 PR 요약 (2-3문장)",
  "risks": [
    {{
      "severity": "높음|중간|낮음",
      "category": "보안|품질|버그|테스트|성능",
      "description": "위험 요소 설명",
      "location": "파일명:라인번호 (가능한 경우)"
    }}
  ],
  "suggestions": [
    {{
      "priority": "필수|권장|선택",
      "description": "개선 제안 내용",
      "example": "개선 예시 코드 (선택사항)"
    }}
  ],
  "positive_points": [
    "칭찬할 만한 점들"
  ],
  "overall_rating": "1-10점 (10점 만점)"
}}

중요: 반드시 유효한 JSON 형식으로만 응답해주세요. 추가 설명이나 마크다운은 포함하지 마세요."""
    
    def __init__(self):
        self.api_key = Config.UPSTAGE_API_KEY
        self.api_url = Config.UPSTAGE_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def analyze_pr(
        self,
        title: str,
        author: str,
        base_branch: str,
        head_branch: str,
        description: str,
        diff: str
    ) -> Optional[Dict]:
        """
        PR 분석 실행
        
        Args:
            title: PR 제목
            author: 작성자
            base_branch: 베이스 브랜치
            head_branch: 헤드 브랜치
            description: PR 설명
            diff: 코드 변경사항
            
        Returns:
            Dict: 분석 결과
        """
        # 프롬프트 생성
        prompt = self.REVIEW_PROMPT.format(
            title=title,
            author=author,
            base_branch=base_branch,
            head_branch=head_branch,
            description=description or "설명 없음",
            diff=diff
        )
        
        # API 요청 페이로드
        payload = {
            "model": "solar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 코드 리뷰 전문가입니다. 보안, 품질, 성능을 중심으로 코드를 분석합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # 일관성 있는 분석을 위해 낮은 temperature
            "max_tokens": 2000
        }
        
        try:
            print("🤖 Upstage Solar Pro로 코드 분석 중...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 응답에서 content 추출
            content = result['choices'][0]['message']['content']
            
            # JSON 파싱
            # 가끔 ```json ... ``` 형태로 올 수 있으므로 처리
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            analysis_result = json.loads(content.strip())
            
            print("✅ 분석 완료!")
            return analysis_result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ LLM API 요청 실패: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            print(f"응답 내용: {content}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None
    
    def create_fallback_analysis(self, error_message: str = None) -> Dict:
        """
        LLM 분석 실패 시 대체 응답 생성
        
        Args:
            error_message: 오류 메시지
            
        Returns:
            Dict: 기본 분석 결과
        """
        return {
            "summary": "자동 분석 중 오류가 발생했습니다. 수동 리뷰를 권장합니다.",
            "risks": [
                {
                    "severity": "중간",
                    "category": "시스템",
                    "description": f"분석 오류: {error_message or '알 수 없는 오류'}",
                    "location": "N/A"
                }
            ],
            "suggestions": [
                {
                    "priority": "권장",
                    "description": "코드를 수동으로 리뷰해주세요.",
                    "example": ""
                }
            ],
            "positive_points": [],
            "overall_rating": "N/A"
        }
