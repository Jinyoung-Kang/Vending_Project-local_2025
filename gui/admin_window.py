import tkinter as tk
from tkinter import messagebox
from utils.sales_manager import get_today_filename, get_month_filename, read_encrypted_json
from utils.finance_manager import log_coin_collection
from utils import password_manager

def show_daily_sales(self):
    try:
        data = read_encrypted_json(get_today_filename())
        if not data: raise ValueError("empty")
        msg = "[일별 매출]\n"
        for name, info in data.items():
            msg += f"{name}: {info['count']}개, 총 {info['total']}원\n"
        messagebox.showinfo("일별 매출", msg)
    except:
        messagebox.showinfo("일별 매출", "오늘 매출 기록이 없습니다.")

def show_monthly_sales(self):
    try:
        data = read_encrypted_json(get_month_filename())
        if not data: raise ValueError("empty")
        msg = "[월별 매출]\n"
        for name, info in data.items():
            msg += f"{name}: {info['count']}개, 총 {info['total']}원\n"
        messagebox.showinfo("월별 매출", msg)
    except:
        messagebox.showinfo("월별 매출", "이번 달 매출 기록이 없습니다.")

def show_coin_inventory(self):
    inventory = self.vm.coins.get_coin_status()
    msg = "[현재 보유 중인 화폐 현황]\n"
    for coin, count in sorted(inventory.items()):
        msg += f"{coin}원: {count}개\n"
    messagebox.showinfo("화폐 현황", msg)

class AdminWindow:

    def __init__(self, vm):
        self.vm = vm
        self.root = tk.Toplevel()
        self.root.title("관리자 메뉴")
        self.root.geometry("400x500")

        self.show_daily_sales = show_daily_sales.__get__(self)
        self.show_monthly_sales = show_monthly_sales.__get__(self)
        self.show_coin_inventory = show_coin_inventory.__get__(self)

        tk.Label(self.root, text="🔒 관리자 전용 기능", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Button(self.root, text="현재 재고 보기", width=25, command=self.show_stock).pack(pady=5)
        tk.Button(self.root, text="재고 보충", width=25, command=self.restock).pack(pady=5)
        tk.Button(self.root, text="화폐 보유 현황", width=25, command=self.show_coin_inventory).pack(pady=5)
        tk.Button(self.root, text="수금하기", width=25, command=self.collect_money).pack(pady=5)
        tk.Button(self.root, text="가격/이름 수정", width=25, command=self.edit_beverage_info).pack(pady=5)
        tk.Button(self.root, text="일별 매출 보기", width=25, command=self.show_daily_sales).pack(pady=5)
        tk.Button(self.root, text="월별 매출 보기", width=25, command=self.show_monthly_sales).pack(pady=5)
        tk.Button(self.root, text="비밀번호 변경", width=25, command=self.change_password_ui).pack(pady=5)

    def show_stock(self):
        stock = self.vm.beverages.get_all_beverages()
        msg = "\n".join([f"{d['name']}: {d['stock']}개" for d in stock])
        messagebox.showinfo("재고 현황", msg)

    def restock(self):
        window = tk.Toplevel(self.root)
        window.title("재고 보충")
        window.geometry("350x250")
        tk.Label(window, text="음료 선택", font=("Arial", 12)).pack(pady=5)
        options = [b['name'] for b in self.vm.beverages.get_all_beverages()] + ["전체 보충"]
        var = tk.StringVar(window)
        var.set(options[0])
        tk.OptionMenu(window, var, *options).pack(pady=5)
        tk.Label(window, text="보충할 수량").pack()
        entry = tk.Entry(window)
        entry.insert(0, "10")
        entry.pack()
        def handle_restock():
            try:
                amount = int(entry.get())
                if amount <= 0: raise ValueError
            except:
                messagebox.showerror("입력 오류", "보충 수량은 1 이상 정수여야 합니다.")
                return
            selected = var.get()
            if selected == "전체 보충":
                current = self.vm.beverages.head
                while current:
                    current.stock += amount
                    current = current.next
            else:
                self.vm.beverages.restock(selected, amount)
            messagebox.showinfo("보충 완료", f"'{selected}' 보충이 완료되었습니다.")
            window.destroy()
        tk.Button(window, text="보충", command=handle_restock).pack(pady=10)

    def collect_money(self):
        try:
            total, detail = self.vm.coins.collect_money()
            msg = f"총 {total}원 수금했습니다.\n\n[수금 내역]\n"
            for coin, count in detail.items():
                if count > 0:
                    msg += f"{coin}원: {count}개\n"
            messagebox.showinfo("수금 완료", msg)
            log_coin_collection(total, detail)
        except Exception as e:
            messagebox.showwarning("수금 실패", str(e))

    def edit_beverage_info(self):
        editor = tk.Toplevel(self.root)
        editor.title("음료 정보 수정")
        tk.Label(editor, text="변경할 음료 선택:", font=("Arial", 12)).pack(pady=5)
        var = tk.StringVar(editor)
        names = [b['name'] for b in self.vm.beverages.get_all_beverages()]
        var.set(names[0])
        option = tk.OptionMenu(editor, var, *names)
        option.pack()
        tk.Label(editor, text="새 이름:").pack()
        entry_name = tk.Entry(editor)
        entry_name.pack()
        tk.Label(editor, text="새 가격:").pack()
        entry_price = tk.Entry(editor)
        entry_price.pack()
        def update_info():
            selected_name = var.get()
            new_name = entry_name.get().strip()
            new_price_str = entry_price.get().strip()
            if not new_name:
                messagebox.showerror("오류", "새 음료 이름을 입력해야 합니다.")
                return
            if new_name != selected_name and self.vm.beverages.get_beverage(new_name):
                messagebox.showerror("오류", "이미 존재하는 음료 이름입니다.")
                return
            try:
                new_price = int(new_price_str)
                if new_price < 10: raise ValueError
                node_to_edit = self.vm.beverages.get_beverage(selected_name)
                if node_to_edit:
                    node_to_edit.name = new_name
                    node_to_edit.price = new_price
                    messagebox.showinfo("성공", "음료 정보가 수정되었습니다.")
                    editor.destroy()
                else:
                    messagebox.showerror("오류", "해당 음료를 찾을 수 없습니다.")
            except ValueError:
                messagebox.showerror("오류", "가격은 10원 이상의 숫자여야 합니다.")
        tk.Button(editor, text="적용", command=update_info).pack(pady=10)

    def change_password_ui(self):
        window = tk.Toplevel(self.root)
        window.title("비밀번호 변경")
        window.geometry("300x220")
        tk.Label(window, text="현재 비밀번호").pack()
        current_entry = tk.Entry(window, show="*")
        current_entry.pack()
        current_entry.focus_set()
        tk.Label(window, text="새 비밀번호").pack()
        new_entry = tk.Entry(window, show="*")
        new_entry.pack()
        tk.Label(window, text="새 비밀번호 확인").pack()
        confirm_entry = tk.Entry(window, show="*")
        confirm_entry.pack()
        def handle_change():
            current = current_entry.get()
            new = new_entry.get()
            confirm = confirm_entry.get()
            if new != confirm:
                messagebox.showerror("오류", "새 비밀번호가 일치하지 않습니다.", parent=window)
                return
            try:
                password_manager.change_password(current, new)
                messagebox.showinfo("성공", "비밀번호가 변경되었습니다.", parent=window)
                window.destroy()
            except (ValueError, PermissionError) as e:
                messagebox.showerror("오류", str(e), parent=window)
        tk.Button(window, text="변경", command=handle_change).pack(pady=10)