from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QTableWidget, \
    QTableWidgetItem, QMessageBox, QHeaderView, QComboBox

from communication import http_client
from views.input_signature_info import InputSignatureInfo
from views.signature_interface import SignatureDialog


class SendZCX66(QDialog):
    def __init__(self, username, token, selected_option, selected_ids):
        super().__init__()
        self.setWindowTitle('Send ZCX66')
        self.setFixedSize(500, 600)
        self.list_key_name = ['correctionNumber', 'decision']

        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids

        self.label_key_name_width = 150
        self.num_key = len(self.list_key_name)

        self.list_le = []
        self.update_cache_dict = {}

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 创建 correctionNumber 的输入框
        upper_layout = QHBoxLayout()
        correction_label = QLabel("correctionNumber:")
        correction_label.setFixedWidth(self.label_key_name_width)
        upper_layout.addWidget(correction_label)

        correction_input = QLineEdit(self)
        correction_input.setMinimumWidth(180)
        upper_layout.addWidget(correction_input)
        self.list_le.append(correction_input)

        layout.addLayout(upper_layout)

        # 创建 decision 的 QComboBox 选择框
        upper_layout = QHBoxLayout()
        decision_label = QLabel("decision:")
        decision_label.setFixedWidth(self.label_key_name_width)
        upper_layout.addWidget(decision_label)

        self.decision_combo_box = QComboBox(self)
        self.decision_combo_box.addItem("0 - brak zgody na zaproponowaną korektę", 0)
        self.decision_combo_box.addItem("1 - zgoda na zaproponowaną korektę", 1)
        self.decision_combo_box.addItem(
            "2 - brak zgody na zaproponowaną korektę wraz z żądaniem zastosowania Art. 8 RD do UKC (decyzja administracyjna)",
            2)
        upper_layout.addWidget(self.decision_combo_box)
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
        self.send_button.setAutoDefault(True)
        self.send_button.setDefault(True)
        self.send_button.clicked.connect(self.send_message)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def update_button_state(self):
        selected_items = self.table_widget.selectedItems()
        self.delete_button.setEnabled(bool(selected_items))

    def add_to_table(self):
        if self.list_le[0].text() == '':
            QMessageBox.warning(self, "Warning", "correctionNumber must be entered!")
            return

        selected_decision_value = self.decision_combo_box.currentData()
        if selected_decision_value is None:
            QMessageBox.warning(self, "Warning", "decision must be entered!")
            return

        if self.table_widget.rowCount() == 9999:
            QMessageBox.warning(self, "Input Error", f"The number of table rows must be no more than 9999.")
            return

        if len(self.list_le[0].text()) > 0:
            if not len(self.list_le[0].text()) <= 5:
                QMessageBox.warning(self, "Input Error", f"{self.list_key_name[0]} must be no more than 5 digits.")
                return

        row_data = [self.list_le[0].text(), str(selected_decision_value)]
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        for col, value in enumerate(row_data):
            item = QTableWidgetItem(value)
            self.table_widget.setItem(row_position, col, item)

        self.list_le[0].clear()
        self.decision_combo_box.setCurrentIndex(-1)  # 重置 QComboBox 选择

    def delete_selected_row(self):
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No row selected to delete.")
            return

        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            self.table_widget.removeRow(row)

    def send_message(self):
        if self.table_widget.rowCount() < 1:
            QMessageBox.warning(self, "Warning", "There must be at least one row of data in the table!")
            return

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

            table_data = self.get_table_data()

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
                    QMessageBox.information(self, "Result", 'Send zcx66 successfully!')
                else:
                    if response_status_code == 'error':
                        QMessageBox.warning(self, "Error", f'Signature error, please try again.')
                        return
                    else:
                        QMessageBox.warning(self, "Error", f'Send zcx66 failed, please try again.')
                        return
            else:
                if not self.token:
                    QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect.')
                    return
                else:
                    QMessageBox.warning(self, "Error", 'Wrong file path and password.')
                    return
            self.accept()
        else:
            print("Operation cancelled")

    def get_table_data(self):
        table_data = []
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

        for row in range(self.table_widget.rowCount()):
            row_data = {}
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            table_data.append(row_data)

        return table_data
