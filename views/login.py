from datetime import datetime, timedelta

import pytz
from PyQt5.QtCore import Qt, QDateTime, QTimeZone
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, \
    QMessageBox, QCheckBox, QDateTimeEdit

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

        # ===============================
        # 同步时间范围选择
        # ===============================
        self.limit_sync_checkbox = QCheckBox("Limit Synchronize Time Range")

        # 波兰时区
        poland_tz = pytz.timezone("Europe/Warsaw")

        # 当前波兰时间
        now_poland = datetime.now(poland_tz)

        # 7天前
        start_poland = now_poland - timedelta(days=7)

        # 转成 Qt QDateTime（只用于显示）
        qt_start = QDateTime(
            start_poland.year,
            start_poland.month,
            start_poland.day,
            start_poland.hour,
            start_poland.minute,
            start_poland.second
        )

        qt_end = QDateTime(
            now_poland.year,
            now_poland.month,
            now_poland.day,
            now_poland.hour,
            now_poland.minute,
            now_poland.second
        )

        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setCalendarPopup(True)
        self.start_datetime.setDateTime(qt_start)

        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setCalendarPopup(True)
        self.end_datetime.setDateTime(qt_end)

        # 默认禁用
        self.start_datetime.setEnabled(False)
        self.end_datetime.setEnabled(False)

        # 勾选后启用
        self.limit_sync_checkbox.stateChanged.connect(
            lambda state: (
                self.start_datetime.setEnabled(state),
                self.end_datetime.setEnabled(state)
            )
        )

        # 时间布局
        time_layout = QVBoxLayout()
        time_layout.addWidget(self.limit_sync_checkbox)

        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Time:"))
        start_layout.addWidget(self.start_datetime)

        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Time:"))
        end_layout.addWidget(self.end_datetime)

        time_layout.addLayout(start_layout)
        time_layout.addLayout(end_layout)

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
        layout.addLayout(time_layout)
        layout.addWidget(self.admin_button)

        self.setLayout(layout)

        self.username = None
        self.token = None

        self.sync_start = None
        self.sync_end = None
        self.sync_limit_enabled = False

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

            # ===============================
            # 记录同步时间范围
            # ===============================
            self.sync_limit_enabled = self.limit_sync_checkbox.isChecked()

            if self.sync_limit_enabled:
                self.sync_start = self.start_datetime.dateTime().toPyDateTime()
                self.sync_end = self.end_datetime.dateTime().toPyDateTime()
            else:
                self.sync_start = None
                self.sync_end = None

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
