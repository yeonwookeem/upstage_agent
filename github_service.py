"""
GitHub API 연동 서비스
"""
import requests
from typing import Dict, List, Optional
from utils.config import Config


class GitHubService:
    """GitHub API 연동 클래스"""
    
    def __init__(self):
        self.api_url = Config.GITHUB_API_URL
        self.token = Config.GITHUB_TOKEN
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_pr_diff(self, repo_full_name: str, pr_number: int) -> Optional[str]:
        """
        PR의 diff 가져오기
        
        Args:
            repo_full_name: 저장소 전체 이름 (예: 'owner/repo')
            pr_number: PR 번호
            
        Returns:
            str: PR diff 내용 (unified diff 형식)
        """
        url = f"{self.api_url}/repos/{repo_full_name}/pulls/{pr_number}"
        headers = {
            **self.headers,
            'Accept': 'application/vnd.github.v3.diff'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ PR diff 가져오기 실패: {e}")
            return None
    
    def get_pr_files(self, repo_full_name: str, pr_number: int) -> List[Dict]:
        """
        PR의 변경된 파일 목록 가져오기
        
        Args:
            repo_full_name: 저장소 전체 이름
            pr_number: PR 번호
            
        Returns:
            List[Dict]: 변경된 파일 정보 리스트
        """
        url = f"{self.api_url}/repos/{repo_full_name}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ PR 파일 목록 가져오기 실패: {e}")
            return []
    
    def get_pr_details(self, repo_full_name: str, pr_number: int) -> Optional[Dict]:
        """
        PR 상세 정보 가져오기
        
        Args:
            repo_full_name: 저장소 전체 이름
            pr_number: PR 번호
            
        Returns:
            Dict: PR 상세 정보
        """
        url = f"{self.api_url}/repos/{repo_full_name}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ PR 정보 가져오기 실패: {e}")
            return None
    
    def post_pr_comment(self, repo_full_name: str, pr_number: int, comment: str) -> bool:
        """
        PR에 코멘트 작성 (선택 사항)
        
        Args:
            repo_full_name: 저장소 전체 이름
            pr_number: PR 번호
            comment: 코멘트 내용
            
        Returns:
            bool: 성공 여부
        """
        url = f"{self.api_url}/repos/{repo_full_name}/issues/{pr_number}/comments"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={'body': comment},
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ PR 코멘트 작성 실패: {e}")
            return False
    
    def format_diff_for_analysis(self, diff_text: str, max_lines: int = 500) -> str:
        """
        diff 텍스트를 분석용으로 포맷팅
        
        Args:
            diff_text: 원본 diff 텍스트
            max_lines: 최대 라인 수 (토큰 제한 고려)
            
        Returns:
            str: 포맷팅된 diff
        """
        if not diff_text:
            return ""
        
        lines = diff_text.split('\n')
        
        # 너무 긴 경우 잘라내기
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append(f"\n... (총 {len(diff_text.split(chr(10)))}줄 중 {max_lines}줄만 표시)")
        
        return '\n'.join(lines)
