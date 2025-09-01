import socket
import json
import queue
import threading
import time
from utils.encryption import encrypt_data

# 서버 주소 및 포트 설정
HOST, PORT = "127.0.0.1", 9999

# 외부에서 사용할 전송 대기 큐
NetworkQueue = queue.Queue()

# 전송 쓰레드 함수
def _sender():
    while True:
        try:
            # 큐에서 전송할 메시지 하나 꺼냄 (0.5초 타임아웃)
            payload = NetworkQueue.get(timeout=0.5)
        except queue.Empty:
            continue  # 큐가 비어있으면 다시 대기

        try:
            # JSON → 문자열 → 암호화
            json_data = json.dumps(payload)
            encrypted = encrypt_data(json_data)

            # 서버에 전송
            with socket.create_connection((HOST, PORT), timeout=3) as sock:
                sock.sendall(encrypted)
                response = sock.recv(1024).decode()
                print(f"[CLIENT] 서버 응답: {response}")

        except Exception as e:
            print(f"[CLIENT] 전송 실패 → 재시도 대기: {e}")
            NetworkQueue.put(payload)  # 재시도 위해 다시 큐에 추가
            time.sleep(2)

threading.Thread(target=_sender, daemon=True).start()