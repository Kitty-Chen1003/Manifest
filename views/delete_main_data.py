import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QCheckBox,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt

from utils import db
from communication import http_client


class DeleteMainDialog(QDialog):
    def __init__(self, username, token):
        super().__init__()

        self.username = username
        self.token = token
        self.data = None  # [main_ids, airwaybills, times]

        self.setWindowTitle("Delete Data By MainId")
        self.setFixedSize(500, 400)

        main_layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Select All")
        self.deselect_all_checkbox = QCheckBox("Deselect All")
        control_layout.addWidget(self.select_all_checkbox)
        control_layout.addWidget(self.deselect_all_checkbox)
        main_layout.addLayout(control_layout)

        # ===== 表格 =====
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Select", "AirWayBill", "Created Time"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)  # 自适应内容
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 横向滚动条

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.load_data()

        main_layout.addWidget(self.table)

        # 底部的确认和取消按钮
        bottom_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)  # 设置为默认按钮
        self.cancel_btn = QPushButton("Cancel")
        bottom_layout.addWidget(self.ok_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        # 连接按钮事件
        self.ok_btn.clicked.connect(self.on_confirm)  # 确定按钮：执行操作
        self.cancel_btn.clicked.connect(self.reject)  # 取消按钮：关闭对话框
        self.select_all_checkbox.stateChanged.connect(self.select_all)
        self.deselect_all_checkbox.stateChanged.connect(self.deselect_all)

    def load_data(self):
        self.data = db.get_id_airwaybill_time_from_main_table(self.username)

        pd_data = {
            "AirWayBill": self.data[1],  # 示例AirWayBill
            "Created Time": self.data[2]
        }
        df = pd.DataFrame(pd_data)
        row_count = len(self.data[0])
        self.table.setRowCount(row_count)

        for row in range(df.shape[0]):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            self.table.setItem(row, 1, QTableWidgetItem(df.iloc[row]['AirWayBill']))  # AirWayBill列
            self.table.setItem(row, 2, QTableWidgetItem(df.iloc[row]['Created Time']))

    def on_confirm(self):
        selected_ids = []

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_ids.append(self.data[0][row])  # main_id

        print(selected_ids)

        if len(selected_ids) == 0:
            QMessageBox.warning(self, "Warning", "Please select at least one.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(selected_ids)} main records and ALL related data?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        if self.token:
            # ===== 后端删除 =====
            payload = {
                "sequenceList": selected_ids
            }

            response_status_code = http_client.delete_data_by_main_ids(self.token, payload)

            if response_status_code != 200:
                QMessageBox.warning(self, "Error", "Backend delete failed.")
                return

            QMessageBox.information(self, "Success", 'Backend delete successfully!')


        else:
            QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect')
            return  # 返回发送界面，保持对话框打开

        # ===== 本地删除 =====
        success = db.delete_by_main_ids(selected_ids)
        if not success:
            QMessageBox.warning(self, "Error", "Local delete failed.")
            return

        QMessageBox.information(self, "Success", "Local delete successfully.")
        self.accept()


    def select_all(self, state):
        """全选复选框"""
        if state == Qt.Checked:
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)
            self.deselect_all_checkbox.setChecked(False)  # 取消“全部取消”的选中状态

    def deselect_all(self, state):
        """取消全选复选框"""
        if state == Qt.Checked:
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(False)
            self.select_all_checkbox.setChecked(False)  # 取消“全选”的选中状态
