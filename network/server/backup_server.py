import socket
import threading
import time
import json
import os
import sys
import queue

# 프로젝트의 다른 모듈을 찾기 위한 경로 설정
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

# Failover 시에만 필요한 모듈들을 임포트
from utils.encryption import decrypt_data
from network.server import db_manager
from network.server import web_admin
from network.server import raw_syncer

db_manager.DB_PATH = os.path.join(os.path.dirname(__file__), "vending_backup.db")

MY_LAN_IP = "192.168.50.239"
PRIMARY_SERVERS = {
    "Server1": {"ip": MY_LAN_IP, "port": 9998}
}
CHECK_INTERVAL_SECONDS = 10

is_failover_mode = False
failover_lock = threading.Lock()


def health_checker():
    """10초마다 주 서버의 상태를 체크하는 스레드"""
    global is_failover_mode
    print("[Health Check] 주 서버 상태 감시 시작...")

    while not is_failover_mode:
        time.sleep(CHECK_INTERVAL_SECONDS)
        server_to_check = PRIMARY_SERVERS["Server1"]
        try:
            with socket.create_connection((server_to_check["ip"], server_to_check["port"]), timeout=2):
                print(f"[Health Check] {server_to_check['ip']} is alive.")
        except (socket.timeout, ConnectionRefusedError):
            print(f"[!!! CRITICAL !!!] {server_to_check['ip']} 응답 없음!")
            with failover_lock:
                if not is_failover_mode:
                    is_failover_mode = True
                    trigger_failover()
                    break # Failover가 시작되면 Health Check 스레드는 역할을 다했으므로 종료


failover_sync_queue = queue.Queue()

def handle_client_in_failover(conn, addr):
    """Failover 모드에서 클라이언트 요청을 처리하는 함수"""
    print(f"[FAILOVER-MODE 접속] 클라이언트: {addr}")
    try:
        data = conn.recv(4096)
        if not data: return
        message = json.loads(decrypt_data(data))
        print(f"[FAILOVER-MODE 수신] 클라이언트 메시지: {message}")
        if "sales" in message:
            db_manager.save_sales_data(message["machine_id"], message["sales"])
        if "inventory" in message:
            db_manager.save_inventory_data(message["machine_id"], message["inventory"])
        failover_sync_queue.put(message)
        conn.sendall("데이터 수신 완료".encode())
    except Exception as e:
        print(f"[에러] Failover 클라이언트 처리 중 오류: {e}")
    finally:
        conn.close()

def start_primary_services():
    """Failover 시 Server1의 모든 핵심 기능을 활성화하는 함수"""
    print("[FAILOVER] 주 서버 모드로 전환! 클라이언트 서비스 및 웹 관리자를 시작합니다.")

    # 웹 관리자 서버 스레드 시작 (포트 8001 사용)
    web_thread = threading.Thread(target=web_admin.start_web_admin_server, args=("127.0.0.1", 8001))
    web_thread.daemon = True
    web_thread.start()

    # 다른 서버(Server2)와 동기화를 위한 Raw 소켓 송신 스레드 시작
    sync_thread = threading.Thread(target=raw_syncer.start_sync_thread, args=(failover_sync_queue,))
    sync_thread.daemon = True
    sync_thread.start()

    # 클라이언트 요청을 처리하는 메인 TCP 서버 루프 시작
    client_listen_port = 9999
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('', client_listen_port))
        server_socket.listen()
        print(f"[FAILOVER] 클라이언트 접속 대기 시작 (Port: {client_listen_port})")
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client_in_failover, args=(conn, addr))
            thread.daemon = True
            thread.start()

def trigger_failover():
    """Failover를 실행하는 함수"""
    print("[FAILOVER] 백업 서버가 주 서버 역할을 시작합니다.")
    primary_service_thread = threading.Thread(target=start_primary_services)
    primary_service_thread.daemon = True
    primary_service_thread.start()

def start_backup_server():
    """Backup Server의 메인 실행 함수"""
    db_manager.init_db()

    health_thread = threading.Thread(target=health_checker)
    health_thread.daemon = True
    health_thread.start()

    print("[Backup Server] 시작 완료. 주 서버 장애 감시 모드로 동작합니다.")

    try:
        # Failover가 트리거되거나 프로그램이 종료될 때까지 대기
        while not is_failover_mode:
            time.sleep(1)
        print("[Backup Server] 활성 모드로 전환되어 메인 스레드 역할을 위임합니다.")
    except KeyboardInterrupt:
        print("\n[Backup Server] 종료합니다.")


if __name__ == "__main__":
    start_backup_server()
