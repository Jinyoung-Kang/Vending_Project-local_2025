from collections import deque
import time

class VendingSimulator:
    def __init__(self):
        self.queue = deque()

    def add_user_request(self, user_id, drink):
        self.queue.append((user_id, drink))
        print(f"{user_id}님이 {drink} 구매 요청을 추가했습니다.")

    def process_requests(self):
        while self.queue:
            user_id, drink = self.queue.popleft()
            print(f"{user_id}님의 {drink} 구매 요청 처리 중...")
            time.sleep(1)
            print(f"{drink} 배출 완료!\n")

# 실행 예시
if __name__ == "__main__":
    sim = VendingSimulator()
    sim.add_user_request("User1", "물")
    sim.add_user_request("User2", "탄산 음료")
    sim.add_user_request("User3", "고급 믹스 커피")
    sim.process_requests()