class CoinManager:
    VALID_COINS = [10, 50, 100, 500, 1000]
    MAX_INPUT_TOTAL = 7000
    MAX_BILL_TOTAL = 5000

    def __init__(self):

        self.balance = 0
        self.bills_inserted = 0  # 투입된 지폐 총액 추적
        self.coin_inventory = {10: 10, 50: 10, 100: 10, 500: 10, 1000: 0}

    def insert_coin(self, amount):
        if amount not in self.VALID_COINS:
            raise ValueError("사용할 수 없는 화폐 단위입니다.")
        if self.balance + amount > self.MAX_INPUT_TOTAL:
            raise ValueError(f"최대 투입 가능 금액({self.MAX_INPUT_TOTAL}원)을 초과했습니다.")

        if amount == 1000:
            if self.bills_inserted + 1000 > self.MAX_BILL_TOTAL:
                raise ValueError(f"지폐는 최대 {self.MAX_BILL_TOTAL}원까지만 투입 가능합니다.")
            self.bills_inserted += 1000


        self.balance += amount

    def get_total_inserted(self):

        return self.balance


    def get_change_and_reset(self):
        """현재 잔액을 기준으로 거스름돈을 계산하고 잔액을 0으로 초기화"""
        change_needed = self.balance
        if change_needed == 0:
            return {}, 0

        change_to_return = {}
        temp_inventory = self.coin_inventory.copy()

        for coin_value in sorted(temp_inventory.keys(), reverse=True):
            if coin_value == 1000: continue # 지폐는 거슬러주지 않음

            can_give = temp_inventory[coin_value]
            will_give = min(change_needed // coin_value, can_give)

            if will_give > 0:
                change_to_return[coin_value] = will_give
                change_needed -= coin_value * will_give

        if change_needed != 0:
            # 거스름돈 부족으로 환불 불가
            raise ValueError("거스름돈이 부족하여 환불할 수 없습니다. 관리자에게 문의하세요.")

        # 거스름돈 지급이 확정되면 실제 재고에서 차감
        for coin, count in change_to_return.items():
            self.coin_inventory[coin] -= count

        total_refunded = self.balance
        self.balance = 0
        self.bills_inserted = 0
        return change_to_return, total_refunded


    def spend_money(self, price):
        """음료 가격만큼 잔액에서 차감"""
        if self.balance < price:
            raise ValueError("잔액이 부족합니다.")
        self.balance -= price
        # 지폐 사용액 추적 로직은 복잡하므로 여기서는 단순 차감만 구현

    def get_coin_status(self):
        return self.coin_inventory.copy()

    def get_total_bills(self):
        return self.bills_inserted


    def collect_money(self, minimum_coins=3):
        collected_total = 0
        collected_detail = {}
        for coin, count in self.coin_inventory.items():
            if count > minimum_coins:
                to_collect = count - minimum_coins
                self.coin_inventory[coin] -= to_collect
                collected_total += coin * to_collect
                collected_detail[coin] = to_collect
            else:
                collected_detail[coin] = 0
        return collected_total, collected_detail