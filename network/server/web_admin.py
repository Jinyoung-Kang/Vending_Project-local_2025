import http.server
import socketserver
import json
import os
from network.server import db_manager

WEB_PORT = 8000
# HTML 파일이 위치한 경로
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

class AdminHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=TEMPLATE_DIR, **kwargs)
    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            super().do_GET()
    def handle_api_request(self):
        try:
            response_data, status_code = {}, 200
            if self.path == '/api/sales':
                response_data = db_manager.fetch_total_sales()
            elif self.path == '/api/inventory':
                response_data = db_manager.fetch_all_inventory()
            else:
                status_code, response_data = 404, {'error': 'Not Found'}
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def start_web_admin_server(host="127.0.0.1", port=8000):
    """웹 관리자 서버를 별도 스레드에서 시작하는 함수"""
    try:
        handler = AdminHttpRequestHandler
        with socketserver.TCPServer((host, port), handler) as httpd:
            print(f"[웹 관리자 서버 시작] http://{host}:{port}/admin.html 에서 접속 가능")
            httpd.serve_forever()
    except Exception as e:
        print(f"[웹 서버 에러] 포트 {port}를 열 수 없습니다: {e}")
