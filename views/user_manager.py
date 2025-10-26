from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, \
    QVBoxLayout, QHBoxLayout, QHeaderView, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
import sys

from communication import http_client


class UserManagerDialog(QDialog):
    def __init__(self, token, username):
        super().__init__()
        self.token = token
        self.username = username

        self.setWindowTitle("User Management")

        # 获取用户数据
        users_list, response_status_code = http_client.get_all_user(token)
        if response_status_code == 200:
            # 如果请求成功，设置self.users
            self.users = [(user['username'], user['remark']) for user in users_list]
        else:
            self.users = []  # 如果请求失败，初始化为空列表
            QMessageBox.warning(self, "Error", "Failed to fetch user data.")

        # 创建表格控件
        self.table = QTableWidget(self)
        self.table.setRowCount(len(self.users))  # 设置行数
        self.table.setColumnCount(2)  # 两列：用户名，备注
        self.table.setHorizontalHeaderLabels(["Username", "Remark"])
        # 设置表格不可编辑
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        # 列宽根据内容自动调整
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # "Username"列根据内容自适应
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # "Remark"列根据内容自适应
        # 启用水平滚动条，当表格内容超出时可以左右滚动
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 设置选择整行
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 选择整行

        # 填充表格数据
        self.load_data_to_table()

        # 输入框和按钮
        self.username_input = QLineEdit(self)
        self.remark_input = QLineEdit(self)
        self.add_button = QPushButton("Add User", self)
        self.delete_button = QPushButton("Delete User", self)
        self.logout_button = QPushButton(f"Exit {self.username}", self)  # 退出登录按钮

        # RabbitMQ 配置输入框和按钮
        self.rabbitmq_host_input = QLineEdit(self)
        self.rabbitmq_port_input = QLineEdit(self)
        self.rabbitmq_vhost_input = QLineEdit(self)
        self.rabbitmq_username_input = QLineEdit(self)
        self.rabbitmq_password_input = QLineEdit(self)

        self.save_rabbitmq_button = QPushButton("Save RabbitMQ Settings", self)

        # 设置输入框宽度为100
        self.rabbitmq_host_input.setFixedWidth(100)
        self.rabbitmq_port_input.setFixedWidth(100)
        self.rabbitmq_vhost_input.setFixedWidth(100)
        self.rabbitmq_username_input.setFixedWidth(100)
        self.rabbitmq_password_input.setFixedWidth(100)

        # 设置标签宽度和右对齐
        self.rabbitmq_host_label = QLabel("Host:", self)
        self.rabbitmq_port_label = QLabel("Port:", self)
        self.rabbitmq_vhost_label = QLabel("Virtual Host:", self)
        self.rabbitmq_username_label = QLabel("Username:", self)
        self.rabbitmq_password_label = QLabel("Password:", self)

        for label in [self.rabbitmq_host_label, self.rabbitmq_port_label, self.rabbitmq_vhost_label,
                      self.rabbitmq_username_label, self.rabbitmq_password_label]:
            label.setFixedWidth(80)  # 设置标签固定宽度
            label.setAlignment(Qt.AlignRight)  # 设置文本右对齐

        # 连接按钮事件
        self.add_button.clicked.connect(self.add_user)
        self.delete_button.clicked.connect(self.delete_user)
        self.logout_button.clicked.connect(self.logout)  # 退出登录按钮的点击事件
        self.save_rabbitmq_button.clicked.connect(self.save_rabbitmq_settings)

        # 布局设置
        layout = QVBoxLayout()

        # 创建网格布局，放置退出按钮在左上角
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.logout_button, 0, 0)

        # 用户信息输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Username:"))
        input_layout.addWidget(self.username_input)
        input_layout.addWidget(QLabel("Remark:"))
        input_layout.addWidget(self.remark_input)
        input_layout.addWidget(self.add_button)

        layout.addLayout(grid_layout)  # 放置退出按钮
        layout.addLayout(input_layout)

        # 添加表格和删除按钮
        layout.addWidget(self.table)
        layout.addWidget(self.delete_button)

        # 添加 RabbitMQ 配置部分
        rabbitmq_layout = QGridLayout()
        rabbitmq_layout.addWidget(QLabel("RabbitMQ Configuration"), 0, 0, 1, 2)  # 配置部分标题，跨两列

        # Host
        rabbitmq_layout.addWidget(self.rabbitmq_host_label, 1, 0)
        rabbitmq_layout.addWidget(self.rabbitmq_host_input, 1, 1)

        # Port
        rabbitmq_layout.addWidget(self.rabbitmq_port_label, 2, 0)
        rabbitmq_layout.addWidget(self.rabbitmq_port_input, 2, 1)

        # Virtual Host
        rabbitmq_layout.addWidget(self.rabbitmq_vhost_label, 3, 0)
        rabbitmq_layout.addWidget(self.rabbitmq_vhost_input, 3, 1)

        # Username
        rabbitmq_layout.addWidget(self.rabbitmq_username_label, 4, 0)
        rabbitmq_layout.addWidget(self.rabbitmq_username_input, 4, 1)

        # Password
        rabbitmq_layout.addWidget(self.rabbitmq_password_label, 5, 0)
        self.rabbitmq_password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        rabbitmq_layout.addWidget(self.rabbitmq_password_input, 5, 1)

        # Save RabbitMQ settings button
        rabbitmq_layout.addWidget(self.save_rabbitmq_button, 6, 0, 1, 2)  # 跨两列

        layout.addLayout(rabbitmq_layout)

        self.setLayout(layout)

    def load_data_to_table(self):
        """将用户数据加载到表格"""
        for row, (username, remark) in enumerate(self.users):
            self.table.setItem(row, 0, QTableWidgetItem(username))
            self.table.setItem(row, 1, QTableWidgetItem(remark))

    def add_user(self):
        """添加用户到表格"""
        username = self.username_input.text()
        remark = self.remark_input.text()

        if not username:
            QMessageBox.warning(self, "Input Error", "Please fill in the username.")
            return

        response_status_code = http_client.add_user(self.token, username, remark)
        if response_status_code == 200:
            # 添加到表格
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(username))
            self.table.setItem(row_position, 1, QTableWidgetItem(remark))  # 允许备注为空

            # 更新用户列表
            self.users.append((username, remark))

            # 清空输入框
            self.username_input.clear()
            self.remark_input.clear()

            QMessageBox.information(self, "Success", "User added successfully.")
        else:
            QMessageBox.information(self, "Error", "Username is duplicated, please re-enter.")

    def delete_user(self):
        """删除选中的用户"""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a user to delete.")
            return

        username = self.table.item(selected_row, 0).text()

        response_status_code = http_client.delete_user(self.token, username)
        if response_status_code == 200:
            # 删除成功
            self.table.removeRow(selected_row)
            # 更新用户列表
            self.users = [user for user in self.users if user[0] != username]

            QMessageBox.information(self, "Success", f"User '{username}' deleted successfully.")
        else:
            QMessageBox.warning(self, "Failed", "Failed to delete the user.")

    def save_rabbitmq_settings(self):
        """保存 RabbitMQ 配置信息"""
        host = self.rabbitmq_host_input.text()
        port = self.rabbitmq_port_input.text()
        vhost = self.rabbitmq_vhost_input.text()
        username = self.rabbitmq_username_input.text()
        password = self.rabbitmq_password_input.text()

        # 验证配置是否完整
        if not host or not port or not vhost or not username or not password:
            QMessageBox.warning(self, "Input Error", "All RabbitMQ fields must be filled in.")
            return

        data = {
            'host': host,
            'port': port,
            'vhost': vhost,
            'username': username,
            'password': password
        }

        response_status_code = http_client.change_rabbitmq_settings(self.token, data)
        if response_status_code == 200:
            QMessageBox.information(self, "Success", "RabbitMQ settings changed successfully!")
        else:
            QMessageBox.information(self, "Error", "RabbitMQ settings change failed!")

    def logout(self):
        """处理退出登录的操作"""
        reply = QMessageBox.question(self, "Logout", "Are you sure you want to log out?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.accept()  # 关闭窗口，表示退出登录
            # 这里可以添加其他的退出登录操作，例如清除token，返回到登录界面等
