from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
import sys

from communication import http_client


class ChangePasswordDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change Password")

        # 用户名输入框
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()

        # 旧密码输入框
        self.old_password_label = QLabel("Old Password:")
        self.old_password_input = QLineEdit()
        self.old_password_input.setEchoMode(QLineEdit.Password)

        # 新密码输入框
        self.new_password_label = QLabel("New Password:")
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)

        # 确认新密码输入框
        self.confirm_password_label = QLabel("Confirm New Password:")
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        # 确定按钮
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.change_password)

        # 取消按钮
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # 关闭对话框

        # 设置固定标签宽度
        label_width = 120  # 设置标签的宽度为 120（根据需要调整）

        # 设置标签宽度并右对齐
        self.username_label.setFixedWidth(label_width)
        self.username_label.setAlignment(Qt.AlignRight)

        self.old_password_label.setFixedWidth(label_width)
        self.old_password_label.setAlignment(Qt.AlignRight)

        self.new_password_label.setFixedWidth(label_width)
        self.new_password_label.setAlignment(Qt.AlignRight)

        self.confirm_password_label.setFixedWidth(label_width)
        self.confirm_password_label.setAlignment(Qt.AlignRight)

        # 布局设置
        layout = QVBoxLayout()

        # 用户名输入：标签和输入框放在同一行
        username_layout = QHBoxLayout()
        username_layout.addWidget(self.username_label)
        username_layout.addWidget(self.username_input)

        # 旧密码输入：标签和输入框放在同一行
        old_password_layout = QHBoxLayout()
        old_password_layout.addWidget(self.old_password_label)
        old_password_layout.addWidget(self.old_password_input)

        # 新密码输入：标签和输入框放在同一行
        new_password_layout = QHBoxLayout()
        new_password_layout.addWidget(self.new_password_label)
        new_password_layout.addWidget(self.new_password_input)

        # 确认密码输入：标签和输入框放在同一行
        confirm_password_layout = QHBoxLayout()
        confirm_password_layout.addWidget(self.confirm_password_label)
        confirm_password_layout.addWidget(self.confirm_password_input)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)

        # 将每个水平布局添加到垂直布局中
        layout.addLayout(username_layout)
        layout.addLayout(old_password_layout)
        layout.addLayout(new_password_layout)
        layout.addLayout(confirm_password_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def change_password(self):
        username = self.username_input.text()
        old_password = self.old_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        # 检查是否填写了所有字段
        if not username or not old_password or not new_password or not confirm_password:
            QMessageBox.critical(self, "Error", "Please fill in all fields!")
            return

        # 检查密码输入是否匹配
        if new_password != confirm_password:
            QMessageBox.critical(self, "Error", "The new passwords do not match!")
            return

        token = http_client.get_token(username, old_password, '1')  # 假设返回 None 表示登录失败

        if token:
            response_status_code = http_client.change_password(token, username, new_password)
            if response_status_code == 200:
                QMessageBox.information(self, "result", "Password changed successfully！")
                self.accept()
            else:
                QMessageBox.information(self, "Error", "Password change failed")
        else:
            QMessageBox.information(self, "Error",
                                    "The username and password are incorrect, please enter the correct ones!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ChangePasswordDialog()
    dialog.exec_()
