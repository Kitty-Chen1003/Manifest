from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
import sys

from communication import http_client
from views.user_manager import UserManagerDialog


class AdminLoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login")

        # 中央标签
        self.title_label = QLabel("Admin Login")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # 用户名和密码输入框
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        # 登录按钮
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)

        # 取消按钮
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # 关闭对话框

        # 布局设置
        layout = QVBoxLayout()

        # 中央标签
        layout.addWidget(self.title_label)

        # 用户名输入框
        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码输入框
        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 登录和取消按钮
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_login(self):
        # 获取输入的用户名和密码
        username = self.username_input.text()
        password = self.password_input.text()

        # 调用 http_client 获取 token（示例）
        token = http_client.get_token(username, password, '2')  # 假设返回 None 表示登录失败

        if token:
            QMessageBox.information(self, "Login Successful", "You have successfully logged in!")
            # 弹出登录成功的提示框
            dialog = UserManagerDialog(token, username)
            dialog.exec_()
            self.username_input.clear()
            self.password_input.clear()
        else:
            # 弹出登录失败的提示框
            QMessageBox.critical(self, "Login Failed",
                                 "The account password is incorrect or the server connection failed, please try again!")
            # 清除输入
            self.username_input.clear()
            self.password_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = AdminLoginDialog()
    dialog.exec_()
