from PyQt5.QtWidgets import QApplication, QWidget, QLabel

def launch_vending_ui():
    import sys
    app = QApplication(sys.argv)
    win = QWidget()
    win.setWindowTitle("자판기 관리 프로그램")
    win.setGeometry(300, 300, 800, 600)
    label = QLabel("자판기 GUI 준비 중", win)
    label.move(100, 100)
    win.show()
    sys.exit(app.exec_())
