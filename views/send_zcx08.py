from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

from communication import http_client
from views.input_signature_info import InputSignatureInfo
from views.signature_interface import SignatureDialog


class SendZCX08(QDialog):
    def __init__(self, username, token, selected_option, selected_ids):
        super().__init__()
        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids

        self.setWindowTitle("Send ZCX08")
        self.setFixedSize(400, 300)

        # 主布局
        main_layout = QVBoxLayout(self)

        # 添加 "invalidationReason（Uzasadnienie wniosku o unieważnienie）" 标签
        self.invalidation_label = QLabel("withdrawalReason \nPowód wycofania")
        main_layout.addWidget(self.invalidation_label)

        # 创建输入框，设置为固定大小
        self.input_field = QTextEdit(self)
        self.input_field.setFixedSize(350, 150)  # 固定大小
        self.input_field.setPlaceholderText("Enter up to 512 characters...")
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 当内容超过范围时显示滚动条
        self.input_field.textChanged.connect(self.limit_text_length)  # 监控文本长度变化
        main_layout.addWidget(self.input_field)

        # 按钮布局
        button_layout = QHBoxLayout()

        # 发送按钮
        self.send_button = QPushButton("Send")
        # self.send_button.setStyleSheet("color: #fff;")
        self.send_button.setAutoDefault(True)  # 默认按钮
        self.send_button.setDefault(True)
        self.send_button.clicked.connect(self.send_message)  # 连接发送函数

        # 取消按钮
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # 取消操作

        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

    def limit_text_length(self):
        """限制输入框内容长度为1024字符"""
        text = self.input_field.toPlainText()
        if len(text) > 512:
            self.input_field.setPlainText(text[:512])  # 截取前1024字符
            # 将光标移动到文本末尾
            cursor = self.input_field.textCursor()
            cursor.movePosition(cursor.End)
            self.input_field.setTextCursor(cursor)

    def send_message(self):
        message = self.input_field.toPlainText()
        if message == '':
            QMessageBox.warning(self, "Warning", f'withdrawalReason cannot be empty.')
            return
        print("发送zcx08内容:", message)

        dialog = InputSignatureInfo(self.selected_option)
        signature_information = {}
        if dialog.exec_() == QDialog.Accepted:
            signature_information = dialog.get_signature_info()
            print(signature_information)
        else:
            return

        file_path = None
        password = None
        dialog = SignatureDialog()
        if dialog.exec_() == QDialog.Accepted:
            file_path, password = dialog.get_results()
            print("Selected file path:", file_path)
            print("Entered password:", password)
            if self.token and file_path and password:
                # 获取输入内容
                data = {
                    'username': self.username,
                    'type': self.selected_option,
                    'sub_id_list': self.selected_ids,
                    'replay_data': message
                }
                response_status_code = http_client.upload_reply_message(
                    self.token,
                    data,
                    file_path,
                    password,
                    signature_information
                )
                if response_status_code == 200:
                    QMessageBox.information(self, "Result", 'Send zcx08 successfully!')
                    self.accept()  # 关闭对话框
                else:
                    if response_status_code == 'error':
                        QMessageBox.warning(self, "Error", f'Signature error, please try again.')
                        return
                    else:
                        QMessageBox.warning(self, "Error", f'Send zcx08 failed, please try again.')
                        return
            else:
                if not self.token:
                    QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect.')
                    return
                else:
                    QMessageBox.warning(self, "Error", 'Wrong file path and password.')
                    return

        else:
            print("Operation cancelled")

