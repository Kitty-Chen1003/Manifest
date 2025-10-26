import re

import pytz
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt

from communication import http_client
from utils import db
from views.signature_interface import SignatureDialog


class InputSignatureInfo(QDialog):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle("Input " + title + " Signature Info")
        self.setFixedSize(300, 200)

        self.signature_information = {}

        # 主布局
        main_layout = QVBoxLayout()

        # 创建表单布局
        self.name_label = QLabel("Name:")
        self.name_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.name_label.setFixedWidth(100)
        self.name_input = QLineEdit('Tomasz Zabrocki')

        self.phone_label = QLabel("Phone Number:")
        self.phone_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.phone_label.setFixedWidth(100)
        self.phone_input = QLineEdit('+48698156094')

        self.email_label = QLabel("Email Address:")
        self.email_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.email_label.setFixedWidth(100)
        self.email_input = QLineEdit('Tomasz.Zabrocki@gmail.com')

        # 创建每行的布局
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.name_input)

        phone_layout = QHBoxLayout()
        phone_layout.addWidget(self.phone_label)
        phone_layout.addWidget(self.phone_input)

        email_layout = QHBoxLayout()
        email_layout.addWidget(self.email_label)
        email_layout.addWidget(self.email_input)

        # 添加到主布局
        main_layout.addLayout(name_layout)
        main_layout.addLayout(phone_layout)
        main_layout.addLayout(email_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 按钮事件绑定
        self.cancel_button.clicked.connect(self.reject)
        self.send_button.clicked.connect(self.validate_inputs)

    def validate_inputs(self):
        # 获取输入框内容
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # 验证是否为空
        if not name or not phone or not email:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
        elif not re.match(EMAIL_REGEX, email):
            QMessageBox.warning(self, "Input Error", "Invalid email format!")
        else:
            poland_tz = pytz.timezone('Europe/Warsaw')  # 设置波兰时区
            poland_time = datetime.now(poland_tz)  # 获取当前波兰时间
            # 将波兰时间转换为 UTC 时间
            utc_time = poland_time.astimezone(pytz.utc)
            self.signature_information = {
                'name': name,
                'phoneNumber': phone,
                'eMailAddress': email,
                'signingTime': utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        self.accept()

    def get_signature_info(self):
        return self.signature_information
