import re

def is_strong_password(pw: str) -> bool:
    if len(pw) < 8:
        return False
    if not re.search(r"[0-9]", pw):
        return False
    if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\-]", pw):
        return False
    return True