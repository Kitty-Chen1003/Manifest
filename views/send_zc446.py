from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QTableWidget, \
    QTableWidgetItem, QMessageBox, QHeaderView

from utils.path import get_resource_path
from views.input_signature_info import InputSignatureInfo
from views.selection_dialog import SelectionDialog
from utils import db

from communication import http_client
from views.signature_interface import SignatureDialog

from datetime import datetime


class SendZC446(QDialog):
    def __init__(self, username, token, selected_option, selected_ids):
        super().__init__()
        self.setWindowTitle('Send ZC446')
        self.setFixedSize(500, 600)
        self.list_key_name = ['referenceNumber', 'type', 'issuingAuthorityName', 'dateOfValidity',
                              'documentLineItemNumber', 'eDocReferenceNumber']

        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids

        self.list_file_name = ['', 'CL034AIS', '', '', '', '']

        self.label_key_name_width = 150

        self.num_key = len(self.list_key_name)

        self.list_le = []
        self.list_btn = []

        self.update_cache_dict = {}

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建输入框和选择按钮
        for i in range(len(self.list_key_name)):
            upper_layout = QHBoxLayout()

            label = QLabel(self)
            label.setText(self.list_key_name[i] + ':')
            label.setFixedWidth(self.label_key_name_width)
            upper_layout.addWidget(label)

            input_line_edit = QLineEdit(self)
            input_line_edit.setMinimumWidth(180)
            upper_layout.addWidget(input_line_edit)
            self.list_le.append(input_line_edit)

            if i == 1:
                select_button = QPushButton("Select", self)
                nav_button_sheetstyle = """
                                            QPushButton {
                                                background-color: #3393FF;  /* 设置背景颜色 */
                                                color: white;               /* 设置文本颜色 */
                                                border-radius: 5px;
                                                padding: 5px;
                                            }
                                            QPushButton:hover {
                                                background-color: #2980b9;  /* 鼠标悬停时的背景颜色 */
                                            }
                                            QPushButton:pressed {
                                                background-color: #3d8649;  /* 按下按钮时的背景颜色 */
                                            }
                                        """
                select_button.setStyleSheet(nav_button_sheetstyle)
                select_button.clicked.connect(
                    lambda checked, le=input_line_edit, fn=self.list_file_name[1]: self.open_selection_dialog(le, fn))
                upper_layout.addWidget(select_button)
                self.list_btn.append(select_button)

            layout.addLayout(upper_layout)

        # 添加“Add”按钮
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_to_table)
        layout.addWidget(self.add_button)

        # 创建表格
        self.table_widget = QTableWidget(self)
        self.table_widget.setFixedHeight(120)
        self.table_widget.setColumnCount(self.num_key)
        self.table_widget.setHorizontalHeaderLabels(self.list_key_name)

        # 设置表格样式和选择模式
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)

        self.table_widget.itemSelectionChanged.connect(self.update_button_state)
        layout.addWidget(self.table_widget)

        # 删除按钮
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_selected_row)
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)

        # 发送和取消按钮
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("Send")
        # self.send_button.setStyleSheet("color: #fff;")
        self.send_button.setAutoDefault(True)  # 将按钮设为默认按钮
        self.send_button.setDefault(True)  # 在对话框中按回车键触发
        self.send_button.clicked.connect(self.send_message)  # 连接发送函数
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_labeled_input(self, label_text, layout):
        """创建带标签的输入框"""
        hbox = QHBoxLayout()
        label = QLabel(label_text, self)
        label.setFixedWidth(100)
        label.setAlignment(Qt.AlignRight)  # 设置文字靠右对齐
        input_field = QLineEdit(self)
        input_field.setFixedWidth(200)
        hbox.addWidget(label)
        hbox.addWidget(input_field)
        layout.addLayout(hbox)
        return input_field

    def update_button_state(self):
        # 检查是否有选中的行
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)

    def open_selection_dialog(self, line_edit, files_name):
        if files_name != "":
            json_file_path = "config/customs_dictionary/" + files_name + ".json"
            json_file_path = get_resource_path(json_file_path)
            title = files_name + " code"
        else:
            json_file_path = ""
            title = "cache"
        height = 1275
        width = 820
        input_id = 10000
        dialog = SelectionDialog(input_id, json_file_path, title, height, width, self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            row_data, columns = dialog.getSelectedRowData()
            if row_data:
                line_edit.setText(row_data[0])

    def add_to_table(self):
        if self.list_le[1].text() == '':
            QMessageBox.warning(self, "Warning", "Type must be entered!")
            return

        if self.table_widget.rowCount() == 99:
            QMessageBox.warning(self, "Input Error", f"The number of table rows must be no more than 99.")
            return

        if len(self.list_le[0].text()) > 0:
            if not len(self.list_le[0].text()) <= 70:
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[0]} must be no more than 70 digits.")
                return

        if not len(self.list_le[1].text()) == 4:
            QMessageBox.warning(self, "Input Error", f"{self.list_key_name[1]} must be 4 digits.")
            return

        if len(self.list_le[2].text()) > 0:
            if not len(self.list_le[2].text()) <= 70:
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[2]} must be no more than 70 digits.")
                return

        if len(self.list_le[3].text()) > 0:
            if not self.is_valid_date(self.list_le[3].text()):
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[3]} must be yyyy-mm-dd.")
                return

        if len(self.list_le[4].text()) > 0:
            if self.list_le[4].text().isdigit():
                if not len(self.list_le[4].text()) <= 5:
                    QMessageBox.warning(self, "Input Error", f"{self.list_key_name[4]} must be no more than 5 digits.")
                    return
            else:
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[4]} must be an integer.")
                return
        if len(self.list_le[5].text()) > 0:
            if not len(self.list_le[5].text()) <= 250:
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[5]} must be no more than 250 digits.")
                return

        """ 将当前输入字段值添加到表格 """
        row_data = [le.text() for le in self.list_le]
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        for col, value in enumerate(row_data):
            item = QTableWidgetItem(value)
            self.table_widget.setItem(row_position, col, item)

        # 清空输入字段
        for le in self.list_le:
            le.clear()

    def is_valid_date(self, date_str):
        try:
            # 尝试将字符串转换为日期对象
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')

            # 检查月份和日期是否为两位数
            if len(date_str.split('-')[1]) != 2 or len(date_str.split('-')[2]) != 2:
                return False

            return True  # 格式正确且符合要求
        except ValueError:
            return False  # 如果捕获到异常，说明格式不正确

    def delete_selected_row(self):
        """ 从表格中删除选中的行 """
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No row selected to delete.")
            return

        # 逆序删除行以避免索引问题
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            self.table_widget.removeRow(row)

    def send_message(self):

        # 检查表格中至少有一行数据
        if self.table_widget.rowCount() < 1:
            QMessageBox.warning(self, "Warning", "There must be at least one row of data in the table!")
            return

        table_data = self.get_table_data()

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
                data = {
                    'username': self.username,
                    'type': self.selected_option,
                    'sub_id_list': self.selected_ids,
                    'replay_data': table_data
                }
                response_status_code = http_client.upload_reply_message(
                    self.token,
                    data,
                    file_path,
                    password,
                    signature_information
                )
                if response_status_code == 200:
                    QMessageBox.information(self, "Result", 'Send zc446 successfully!')
                else:
                    if response_status_code == 'error':
                        QMessageBox.warning(self, "Error", f'Signature error, please try again.')
                        return
                    else:
                        QMessageBox.warning(self, "Error", f'Send zc446 failed, please try again.')
                        return
            else:
                if not self.token:
                    QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect.')
                    return
                else:
                    QMessageBox.warning(self, "Error", 'Wrong file path and password.')
                    return

            """ 发送按钮的功能逻辑 """
            if len(self.list_key_name) >= 2:
                # 只获取第二个键的值
                second_key = self.list_key_name[1]
                all_values = {second_key: [d[second_key] for d in table_data if second_key in d]}
                cache_id = 10000
                self.update_cache_dict[cache_id] = all_values[second_key]
            self.update_cache()
            self.accept()
        else:
            print("Operation cancelled")

    def get_table_data(self):
        """ 将表格数据转换为字典列表 """
        table_data = []
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

        for row in range(self.table_widget.rowCount()):
            row_data = {}
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            table_data.append(row_data)

        return table_data

    def update_cache(self):
        for key, values in self.update_cache_dict.items():
            # 查询缓存数据
            cache_data_list = db.get_input_cache_data(key, self.username)

            # 确保 cache_data_list 是一个列表
            if not isinstance(cache_data_list, list):
                cache_data_list = []

            len_cache_data_list = len(cache_data_list)

            # 确保 cache_data_list 中的每个元素都是字典并有一个 'cache value' 键
            existing_values = [d['cache value'] for d in cache_data_list if isinstance(d, dict) and 'cache value' in d]

            # 检查 values 是否为列表
            if isinstance(values, list):
                for value in values:
                    # 如果值不在已存在的值中，插入新字典到 cache_data_list
                    if value not in existing_values:
                        cache_data_list.insert(0, {'cache value': value})
                        # 如果 cache_data_list 的长度超过 100，删除最后一个元素
                        if len(cache_data_list) > 100:
                            cache_data_list.pop()
            else:
                # 如果值不是列表，直接进行比较
                if values not in existing_values:
                    cache_data_list.insert(0, {'cache value': values})
                    # 如果 cache_data_list 的长度超过 100，删除最后一个元素
                    if len(cache_data_list) > 100:
                        cache_data_list.pop()

            if len_cache_data_list == 0:
                db.insert_into_input_cache(key, cache_data_list, self.username)
            else:
                db.update_cache_data(key, cache_data_list)
