import socket
import threading
import json
import os
import sys
import queue  # 동기화 큐

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

sys.path.append(PROJECT_ROOT)

from utils.encryption import decrypt_data
from network.server.db_manager import save_sales_data, save_inventory_data
from network.server.raw_syncer import start_sync_thread
from network.server.web_admin import start_web_admin_server

# 서버 설정
HOST = '127.0.0.1'
PORT = 9999

# 서버 간 동기화를 위한 큐
sync_queue = queue.Queue()

# 클라이언트 요청 처리 함수
def handle_client(conn, addr):
    print(f"[접속] 클라이언트: {addr}")
    try:
        data = conn.recv(4096)
        if not data:
            return

        decrypted_json = decrypt_data(data)
        message = json.loads(decrypted_json)
        print(f"[수신] 클라이언트 메시지: {message}")

        if "sales" in message:
            save_sales_data(message["machine_id"], message["sales"])
        if "inventory" in message:
            save_inventory_data(message["machine_id"], message["inventory"])

        # 처리 완료된 데이터를 동기화 큐에 넣기
        sync_queue.put(message)

        conn.sendall("데이터 수신 완료".encode())
    except Exception as e:
        print(f"[에러] 클라이언트 처리 중 오류: {e}")
        conn.sendall(f"오류 발생: {e}".encode())
    finally:
        conn.close()
        print(f"[종료] 클라이언트 연결 종료: {addr}")

HEARTBEAT_PORT = 9998

def heartbeat_listener():
    """Heartbeat 요청을 수신하고 연결을 즉시 닫는 스레드"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as hb_socket:
        hb_socket.bind(('', HEARTBEAT_PORT))
        hb_socket.listen()
        while True:
            conn, _ = hb_socket.accept()
            conn.close() # 접속만 확인하고 바로 닫음
def start_server():
    print(f"[Server1 시작] {HOST}:{PORT}")

    # Raw 소켓 동기화 스레드 시작
    sync_thread = threading.Thread(target=start_sync_thread, args=(sync_queue,))
    sync_thread.daemon = True
    sync_thread.start()

    # 웹 관리자 서버 스레드 시작
    web_thread = threading.Thread(target=start_web_admin_server)
    heartbeat_thread = threading.Thread(target=heartbeat_listener)
    heartbeat_thread.daemon = True
    heartbeat_thread.start()
    web_thread.daemon = True
    web_thread.start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print("[대기 중] 클라이언트 연결을 기다리는 중...")

        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()


if __name__ == "__main__":
    start_server()
