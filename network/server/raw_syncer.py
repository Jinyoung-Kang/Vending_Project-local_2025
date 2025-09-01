import socket
import struct
import json
import threading

BROADCAST_IP = "192.168.50.239"

def get_local_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        if s:
            s.close()
    return ip

def create_ip_header(src_ip, dst_ip, data_len):

    version = 4; ihl = 5; tos = 0
    total_length = 20 + 8 + data_len
    packet_id = 54321; frag_offset = 0
    ttl = 255; protocol = socket.IPPROTO_UDP; checksum = 0
    source_ip = socket.inet_aton(src_ip)
    destination_ip = socket.inet_aton(dst_ip)
    version_ihl = (version << 4) + ihl
    ip_header = struct.pack('!BBHHHBBH4s4s', version_ihl, tos, total_length, packet_id, frag_offset, ttl, protocol, checksum, source_ip, destination_ip)
    return ip_header

def create_udp_header(src_port, dst_port, data_len):

    udp_length = 8 + data_len
    checksum = 0
    udp_header = struct.pack('!HHHH', src_port, dst_port, udp_length, checksum)
    return udp_header

def sync_worker(q):
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        raw_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        raw_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception as e:
        print(f"[오류] Raw 소켓 생성 실패: {e}. 관리자 권한으로 실행해야 합니다.")
        return

    print("[동기화 스레드] 시작")
    my_ip = get_local_ip()
    print(f"[동기화 스레드] 감지된 로컬 IP: {my_ip}")

    while True:
        message = q.get()
        try:
            payload = json.dumps(message).encode('utf-8')

            dest_ip = BROADCAST_IP
            src_ip = my_ip

            ip_header = create_ip_header(src_ip, dest_ip, len(payload))
            udp_header = create_udp_header(12345, 9005, len(payload))
            packet = ip_header + udp_header + payload

            raw_socket.sendto(packet, (dest_ip, 0)) # 한 번만 전송
            print(f"[동기화] {dest_ip}로 브로드캐스트 전송 완료: {message['machine_id']}")

        except Exception as e:
            print(f"[동기화 에러] 전송 실패: {e}")

def start_sync_thread(q):
    thread = threading.Thread(target=sync_worker, args=(q,))
    thread.daemon = True
    thread.start()