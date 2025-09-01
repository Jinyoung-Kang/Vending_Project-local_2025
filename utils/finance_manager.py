import os
import datetime
import json

DATA_DIR = "data"
COLLECT_FILE = os.path.join(DATA_DIR, "coin_collection_log.json")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def log_coin_collection(total_collected, collected_detail):
    """수금 총액과 상세 내역을 받아 JSON 파일에 로그로 기록합니다."""
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(COLLECT_FILE):
        try:
            with open(COLLECT_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
    else:
        logs = []


    logs.append({
        "datetime": today,
        "total": total_collected,
        "details": collected_detail
    })

    with open(COLLECT_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)