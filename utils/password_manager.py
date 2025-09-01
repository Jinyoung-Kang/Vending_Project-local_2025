import os
import hashlib
from .security import is_strong_password

# 비밀번호 해시를 저장할 단일 파일 경로 (
PWD_FILE = "data/admin_password.hash"
DEFAULT_PWD = "Admin@123"

def _hash_password(password: str) -> str:
    """비밀번호를 SHA256으로 해시하여 반환"""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_password():
    """비밀번호 파일이 없으면 기본값으로 생성"""
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PWD_FILE):
        with open(PWD_FILE, 'w') as f:
            f.write(_hash_password(DEFAULT_PWD))

def check_password(input_password: str) -> bool:
    """입력된 비밀번호가 저장된 해시와 일치하는지 확인"""
    # 파일이 없으면 기본값으로 먼저 생성
    initialize_password()

    with open(PWD_FILE, 'r') as f:
        saved_hash = f.read().strip()

    return _hash_password(input_password) == saved_hash

def change_password(current_password: str, new_password: str) -> bool:
    """현재 비밀번호를 확인하고 유효성 검사 후 새 비밀번호로 변경"""
    if not check_password(current_password):
        # 현재 비밀번호가 틀리면 변경 실패
        raise PermissionError("현재 비밀번호가 틀립니다.")

    if not is_strong_password(new_password):
        # 새 비밀번호의 유효성 검사
        raise ValueError("새 비밀번호는 숫자, 특수문자를 포함한 8자리 이상이어야 합니다.")

    # 모든 검증을 통과하면 새 비밀번호 해시를 저장
    with open(PWD_FILE, 'w') as f:
        f.write(_hash_password(new_password))
    return True

# 프로그램 시작 시 비밀번호 파일이 없으면 생성되도록 호출
initialize_password()