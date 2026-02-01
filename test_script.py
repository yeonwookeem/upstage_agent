#!/usr/bin/env python3
"""
PR 분석 테스트 스크립트
"""
import requests
import json
import sys


def test_health_check(base_url: str):
    """헬스 체크 테스트"""
    print("🔍 헬스 체크 테스트...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        response.raise_for_status()
        print(f"✅ 헬스 체크 성공: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ 헬스 체크 실패: {e}")
        return False


def test_manual_analysis(base_url: str, repo: str, pr_number: int):
    """수동 분석 테스트"""
    print(f"\n🔍 PR 분석 테스트: {repo}#{pr_number}")
    try:
        response = requests.post(
            f"{base_url}/test/analyze",
            json={
                "repo": repo,
                "pr_number": pr_number
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        print(f"✅ 분석 시작 성공:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"응답: {e.response.text}")
        return False


def main():
    """메인 함수"""
    # 기본 설정
    base_url = "http://localhost:5000"
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python test_script.py health")
        print("  python test_script.py analyze <owner/repo> <pr_number>")
        print("\n예시:")
        print("  python test_script.py health")
        print("  python test_script.py analyze octocat/Hello-World 1")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "health":
        success = test_health_check(base_url)
        sys.exit(0 if success else 1)
    
    elif command == "analyze":
        if len(sys.argv) < 4:
            print("❌ 저장소와 PR 번호를 입력하세요")
            print("예시: python test_script.py analyze owner/repo 123")
            sys.exit(1)
        
        repo = sys.argv[2]
        try:
            pr_number = int(sys.argv[3])
        except ValueError:
            print("❌ PR 번호는 숫자여야 합니다")
            sys.exit(1)
        
        success = test_manual_analysis(base_url, repo, pr_number)
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")
        print("사용 가능한 명령: health, analyze")
        sys.exit(1)


if __name__ == "__main__":
    main()
