"""
GitHub Webhook 서명 검증 모듈
"""
import hmac
import hashlib


def verify_github_signature(payload_body: bytes, signature_header: str, secret: str) -> bool:
    """
    GitHub Webhook 서명 검증
    
    Args:
        payload_body: 요청 본문 (bytes)
        signature_header: X-Hub-Signature-256 헤더 값
        secret: Webhook Secret
        
    Returns:
        bool: 서명이 유효한지 여부
    """
    if not signature_header:
        return False
    
    # "sha256=" 접두사 제거
    hash_algorithm, github_signature = signature_header.split('=')
    
    if hash_algorithm != 'sha256':
        return False
    
    # HMAC SHA256 계산
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = mac.hexdigest()
    
    # 타이밍 공격 방지를 위한 안전한 비교
    return hmac.compare_digest(expected_signature, github_signature)
