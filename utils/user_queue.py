from collections import deque

class UserQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, user_id):
        self.queue.append(user_id)

    def dequeue(self):
        return self.queue.popleft() if self.queue else None

    def peek(self):
        return self.queue[0] if self.queue else None

    def is_empty(self):
        return len(self.queue) == 0