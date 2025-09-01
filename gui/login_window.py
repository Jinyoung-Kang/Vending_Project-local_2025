import tkinter as tk
from tkinter import messagebox
from gui.admin_window import AdminWindow
from utils import password_manager

class LoginWindow:
    def __init__(self, vm):
        self.vm = vm
        self.window = tk.Toplevel()
        self.window.title("관리자 로그인")
        self.window.geometry("300x150")

        tk.Label(self.window, text="비밀번호 입력:").pack(pady=10)
        self.entry = tk.Entry(self.window, show="*")
        self.entry.pack()
        self.entry.focus_set()
        # 엔터 키로도 로그인이 되도록
        self.entry.bind("<Return>", self.login)

        tk.Button(self.window, text="로그인", command=self.login).pack(pady=10)


    def login(self, event=None):
        input_pw = self.entry.get()

        if password_manager.check_password(input_pw):
            messagebox.showinfo("성공", "로그인 성공!")
            self.window.destroy()
            AdminWindow(self.vm) # 관리자 메뉴 창 열기
        else:
            messagebox.showerror("실패", "비밀번호가 틀렸습니다.")