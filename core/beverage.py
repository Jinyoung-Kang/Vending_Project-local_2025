# 자판기 음료 재고 관리를 위한 Linked List 자료구조 구현

class BeverageNode:
    def __init__(self, name, price):
        self.name = name          # 음료 이름
        self.price = price        # 음료 가격
        self.stock = 10           # 초기 재고
        self.next = None          # 다음 음료

class BeverageLinkedList:
    def __init__(self):
        self.head = None

    def add_beverage(self, name, price):
        new_node = BeverageNode(name, price)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def get_beverage(self, name):
        current = self.head
        while current:
            if current.name == name:
                return current
            current = current.next
        return None

    def reduce_stock(self, name):
        bev = self.get_beverage(name)
        if bev and bev.stock > 0:
            bev.stock -= 1
            return True
        return False

    def restock(self, name, amount):
        bev = self.get_beverage(name)
        if bev:
            bev.stock += amount

    def is_sold_out(self, name):
        bev = self.get_beverage(name)
        if bev:
            return bev.stock <= 0
        return False

    def get_all_beverages(self):
        result = []
        current = self.head
        while current:
            result.append({
                'name': current.name,
                'price': current.price,
                'stock': current.stock
            })
            current = current.next
        return result

# 테스트용
if __name__ == "__main__":
    inventory = BeverageLinkedList()
    inventory.add_beverage("믹스 커피", 200)
    inventory.add_beverage("고급 믹스 커피", 300)
    inventory.add_beverage("물", 450)
    inventory.add_beverage("캔 커피", 500)
    inventory.add_beverage("이온음료", 550)
    inventory.add_beverage("고급 캔 커피", 700)
    inventory.add_beverage("탄산 음료", 750)
    inventory.add_beverage("특화 음료", 800)

    for b in inventory.get_all_beverages():
        print(b)