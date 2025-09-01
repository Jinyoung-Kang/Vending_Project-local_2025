import socket
import json
import threading
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from network.server import db_manager

# DB 경로를 Server2 전용으로 설정
db_manager.DB_PATH = os.path.join(os.path.dirname(__file__), "vending2.db")

def standard_udp_listener():
    # Server1/Backup으로부터 표준 UDP 패킷을 수신하여 동기화하는 스레드
    listen_port = 9005  # 송신측(raw_syncer)에서 설정한 UDP 목적지 포트와 동일
    try:
        # 소켓 타입을 SOCK_DGRAM (UDP)으로 변경
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 모든 인터페이스의 특정 포트로 들어오는 패킷을 수신하도록 바인딩
        s.bind(('', listen_port))
        print(f"[Server2] 표준 UDP 리스너 시작. Port {listen_port}에서 동기화 데이터 수신 대기 중...")
    except Exception as e:
        print(f"[오류] Server2 UDP 소켓 생성 또는 바인딩 실패: {e}")
        return

    while True:
        try:
            payload, addr = s.recvfrom(65535)

            message = json.loads(payload.decode('utf-8'))
            print(f"[Server2 동기화] {addr[0]}로부터 데이터 수신: {message['machine_id']}")

            # DB에 저장
            if "sales" in message:
                db_manager.save_sales_data(message["machine_id"], message["sales"])
            if "inventory" in message:
                db_manager.save_inventory_data(message["machine_id"], message["inventory"])
        except Exception as e:
            print(f"[오류] Server2 데이터 처리 중 오류: {e}")


def start_server2():
    db_manager.init_db()

    listener_thread = threading.Thread(target=standard_udp_listener)
    listener_thread.daemon = True
    listener_thread.start()

    print("[Server2] 시작 완료.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("[Server2] 종료합니다.")

if __name__ == "__main__":
    start_server2()
