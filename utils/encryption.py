from cryptography.fernet import Fernet
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

KEY_FILE = os.path.join(DATA_DIR, "secret.key")

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_data(data: str) -> bytes:
    return Fernet(load_key()).encrypt(data.encode())

def decrypt_data(token: bytes):
    return Fernet(load_key()).decrypt(token).decode()

def delete_sales_files():
    folder = "data"
    for file in os.listdir(folder):
        if file.endswith(".enc") and file.startswith("sales"):
            os.remove(os.path.join(folder, file))