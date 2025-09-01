# money_handler.py
class MoneyUnit:
    def __init__(self, value):
        self.value = value
        self.next = None

class MoneyList:
    def __init__(self):
        self.head = None

    def insert(self, value):
        new_node = MoneyUnit(value)
        new_node.next = self.head
        self.head = new_node

    def total(self):
        current = self.head
        total = 0
        while current:
            total += current.value
            current = current.next
        return total

    def clear(self):
        self.head = None  # 동적 해제 개념

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result