from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
import sys

from communication import http_client

from views.change_password import ChangePasswordDialog
from views.login_admin import AdminLoginDialog


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User login interface")

        # 用户登录界面标签，居中显示
        self.title_label = QLabel("User Login Interface")
        self.title_label.setAlignment(Qt.AlignCenter)  # 居中对齐
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        # 用户名输入框
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit('chenxi')

        # 密码输入框
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit('12345678')
        self.password_input.setEchoMode(QLineEdit.Password)

        # 登录按钮
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)

        # 修改密码按钮
        self.change_password_button = QPushButton("Change Password")
        self.change_password_button.clicked.connect(self.change_password)  # 连接修改密码方法

        # 打开管理员界面按钮
        self.admin_button = QPushButton("Open Admin Interface")
        self.admin_button.clicked.connect(self.open_admin_interface)  # 连接打开管理员界面的方法

        # 布局设置
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.username_label)
        top_layout.addWidget(self.username_input)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        login_layout = QHBoxLayout()
        login_layout.addWidget(self.login_button)
        login_layout.addWidget(self.change_password_button)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addLayout(top_layout)
        layout.addLayout(password_layout)
        layout.addLayout(login_layout)
        layout.addWidget(self.admin_button)

        self.setLayout(layout)

        self.username = None
        self.token = None

    def check_login(self):
        # 获取输入的用户名和密码
        username = self.username_input.text()
        password = self.password_input.text()

        # 调用 http_client 获取 token（示例）
        token = http_client.get_token(username, password, '1')  # 假设返回 None 表示登录失败

        if token:
            self.username = username
            self.token = token
            # 弹出登录成功的提示框
            QMessageBox.information(self, "Login Successful", "You have successfully logged in!")
            self.accept()  # 关闭对话框，表示登录成功
        else:
            # 弹出登录失败的提示框
            QMessageBox.critical(self, "Login Failed",
                                 "The account password is incorrect or the server connection failed, please try again!")
            # 清除输入
            self.username_input.clear()
            self.password_input.clear()

    def change_password(self):
        dialog = ChangePasswordDialog()
        dialog.exec_()

    def open_admin_interface(self):
        # 这里你可以添加打开管理员界面的逻辑
        dialog = AdminLoginDialog()
        dialog.exec_()
