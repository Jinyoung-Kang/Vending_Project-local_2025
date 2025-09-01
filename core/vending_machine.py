from core.beverage import BeverageLinkedList
from core.coin_manager import CoinManager
from utils.sales_manager import record_sale
from network.client.client_sender import NetworkQueue
import datetime

class VendingMachine:

    def __init__(self, machine_id="VM-001"):
        self.machine_id = machine_id
        self.beverages = BeverageLinkedList()
        self.coins = CoinManager()
        self.init_beverages()
        self.purchase_stack = []

    def init_beverages(self):
        self.beverages.add_beverage("믹스 커피", 200)
        self.beverages.add_beverage("고급 믹스 커피", 300)
        self.beverages.add_beverage("물", 450)
        self.beverages.add_beverage("캔 커피", 500)
        self.beverages.add_beverage("이온음료", 550)
        self.beverages.add_beverage("고급 캔 커피", 700)
        self.beverages.add_beverage("탄산 음료", 750)
        self.beverages.add_beverage("특화 음료", 800)

    def insert_money(self, amount):
        try:
            self.coins.insert_coin(amount)
            return f"{amount}원이 성공적으로 투입되었습니다. 현재 금액: {self.coins.get_total_inserted()}원"
        except ValueError as e:
            return str(e)

    def cancel_transaction(self):
        try:
            change_detail, total_refunded = self.coins.get_change_and_reset()
            if total_refunded == 0:
                return "반환할 금액이 없습니다."

            change_str = ", ".join([f"{k}원x{v}" for k, v in change_detail.items()])
            return f"총 {total_refunded}원이 반환되었습니다.\n({change_str})"
        except ValueError as e:
            return str(e)

    def get_available_beverages(self):
        available = []
        total = self.coins.get_total_inserted()
        for item in self.beverages.get_all_beverages():
            if item['stock'] > 0 and item['price'] <= total:
                available.append(item)
        return available

    def purchase(self, name):
        drink = self.beverages.get_beverage(name)
        if not drink:
            raise ValueError("선택한 음료가 존재하지 않습니다.")
        if self.beverages.is_sold_out(name):
            raise ValueError(f"{name}은(는) 품절되었습니다.")
        if drink.price > self.coins.get_total_inserted():
            raise ValueError("투입 금액이 부족합니다.")

        self.purchase_stack.append((drink.name, drink.price))

        try:
            self.coins.spend_money(drink.price)
            self.beverages.reduce_stock(name)
            record_sale(drink.name, drink.price)
            NetworkQueue.put({
                "machine_id": self.machine_id,
                "sales": { drink.name: { "date": datetime.date.today().isoformat(), "count": 1, "total": drink.price }},
                "inventory": {d['name']: d['stock'] for d in self.beverages.get_all_beverages()}
            })
            return f"{name} 구매 완료!\n현재 잔액: {self.coins.get_total_inserted()}원"
        except ValueError as e:
            self.purchase_stack.pop()
            raise e


    def cancel_last_purchase(self):
        if not self.purchase_stack:
            return "되돌릴 구매 이력이 없습니다."

        # 1. 스택에서 이름과 '가격'을 모두 가져옴
        last_name, last_price = self.purchase_stack.pop()

        # 2. BeverageLinkedList의 올바른 restock 메소드 호출
        self.beverages.restock(last_name, 1)

        # 3. CoinManager의 잔액(balance)에 가격을 다시 더해줌
        self.coins.balance += last_price


        return f"가장 최근 구매한 '{last_name}'({last_price}원)을 취소하고 재고와 잔액을 복구했습니다."

    def get_status(self):
        return {
            "beverages": self.beverages.get_all_beverages(),
            "coins": self.coins.get_coin_status()
        }