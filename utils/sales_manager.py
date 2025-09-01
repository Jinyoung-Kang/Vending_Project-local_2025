import os
import datetime
import json
from utils.encryption import encrypt_data, decrypt_data, generate_key

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_today_filename():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join(DATA_DIR, f"sales_{today}.enc")

def get_month_filename():
    month = datetime.date.today().strftime("%Y-%m")
    return os.path.join(DATA_DIR, f"sales_month_{month}.enc")

def read_encrypted_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "rb") as f:
        encrypted = f.read()
        try:
            decrypted = decrypt_data(encrypted)
            return json.loads(decrypted)
        except Exception:
            return {}

def write_encrypted_json(file_path, data):
    encrypted = encrypt_data(json.dumps(data, ensure_ascii=False, indent=2))
    with open(file_path, "wb") as f:
        f.write(encrypted)

generate_key()  # 프로그램 시작 시 한 번만 호출 (한번만 유지)
def record_sale(beverage_name, price):
    today_file = get_today_filename()
    sales = read_encrypted_json(today_file)

    if beverage_name in sales:
        sales[beverage_name]['count'] += 1
        sales[beverage_name]['total'] += price
    else:
        sales[beverage_name] = {'count': 1, 'total': price}

    write_encrypted_json(today_file, sales)

    # 월별 매출도 동시에 기록
    month_file = get_month_filename()
    monthly_sales = read_encrypted_json(month_file)

    if beverage_name in monthly_sales:
        monthly_sales[beverage_name]['count'] += 1
        monthly_sales[beverage_name]['total'] += price
    else:
        monthly_sales[beverage_name] = {'count': 1, 'total': price}

    write_encrypted_json(month_file, monthly_sales)