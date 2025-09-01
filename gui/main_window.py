import tkinter as tk
from tkinter import messagebox
from core.vending_machine import VendingMachine
from gui.login_window import LoginWindow
import core.network_thread

class VendingMachineGUI:
    def open_admin(self):
        LoginWindow(self.vm)

    def __init__(self, root):
        self.vm = VendingMachine("VM-001")
        self.root = root
        self.root.title("자판기 관리 프로그램")
        self.root.geometry("800x600")

        self.label_bill = None
        self.build_gui()


    def build_gui(self):
        # 현재 투입 금액 표시
        self.balance_label = tk.Label(self.root, text="현재 투입 금액: 0원", font=("Arial", 14))
        self.balance_label.pack(pady=10)

        # 지폐 금액 별도 표시
        self.label_bill = tk.Label(self.root, text="지폐 투입 금액: 0원", font=("Arial", 12))
        self.label_bill.pack()

        # 총 금액 표시
        self.label_total = tk.Label(self.root, text="총 투입 금액: 0원", font=("Arial", 12))
        self.label_total.pack()

        # 화폐 입력 버튼들
        frame_coins = tk.Frame(self.root)
        frame_coins.pack()
        for amount in [10, 50, 100, 500, 1000]:
            btn = tk.Button(frame_coins, text=f"{amount}원", width=10,
                            command=lambda a=amount: self.insert_money(a))
            btn.pack(side=tk.LEFT, padx=5, pady=10)

        # 음료 목록을 수동으로 새로고침하는 버튼
        tk.Button(self.root, text="🔄 음료 목록 새로고침", command=self.update_available_beverages).pack(pady=5)

        # 음료 버튼 영역
        self.drinks_frame = tk.Frame(self.root)
        self.drinks_frame.pack(pady=10)

        # 잔돈 반환 버튼
        tk.Button(self.root, text="잔돈 반환", bg="orange",
                  command=self.refund).pack(pady=10)

        # 최근 구매 취소 버튼
        tk.Button(self.root, text="최근 구매 취소", command=self.undo_purchase).pack(pady=5)

        # 관리자 로그인 버튼
        tk.Button(self.root, text="🔐 관리자 로그인", bg="lightgray",
                  command=self.open_admin).pack(pady=10)

        # 최초 버튼 표시
        self.update_available_beverages()


    def insert_money(self, amount):
        try:
            self.vm.insert_money(amount)
        except ValueError as e:
            messagebox.showwarning("입력 오류", str(e))
        self.update_all_labels()
        self.update_available_beverages()


    def refund(self):
        result = self.vm.cancel_transaction()
        messagebox.showinfo("잔돈 반환", result)
        self.update_all_labels()
        self.update_available_beverages()


    def update_available_beverages(self):
        for widget in self.drinks_frame.winfo_children():
            widget.destroy()

        total_money = self.vm.coins.get_total_inserted()
        for drink in self.vm.beverages.get_all_beverages():
            name, price, stock = drink['name'], drink['price'], drink['stock']
            text = f"{name} ({price}원 / {stock}개)"
            state = tk.NORMAL

            if stock == 0:
                state = tk.DISABLED
                text = f"{name} (품절)"
            elif price > total_money:
                state = tk.DISABLED

            tk.Button(self.drinks_frame, text=text, width=25, state=state,
                      command=lambda n=name: self.purchase(n)).pack(pady=3)


    def purchase(self, name):
        try:
            result = self.vm.purchase(name)
            messagebox.showinfo("구매 결과", result)
        except ValueError as e:
            messagebox.showwarning("경고", str(e))

        self.update_all_labels()
        self.update_available_beverages()


    def undo_purchase(self):
        result = self.vm.cancel_last_purchase()
        messagebox.showinfo("구매 취소", result)

        self.update_all_labels()
        self.update_available_beverages()


    def update_all_labels(self):
        # 모든 금액 관련 라벨의 텍스트를 현재 상태에 맞게 업데이트
        current_balance = self.vm.coins.get_total_inserted()
        bill_balance = self.vm.coins.get_total_bills()

        self.balance_label.config(text=f"현재 투입 금액: {current_balance}원")
        self.label_bill.config(text=f"지폐 투입 금액: {bill_balance}원")
        self.label_total.config(text=f"총 투입 금액: {current_balance}원")


if __name__ == "__main__":
    root = tk.Tk()
    app = VendingMachineGUI(root)
    root.mainloop()