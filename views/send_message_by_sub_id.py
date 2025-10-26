import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QCheckBox,
    QAbstractItemView, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

from utils import db

from views.send_zc414 import SendZC414
from views.send_zcx02 import SendZCX02
from views.send_zcx08 import SendZCX08
from views.send_zc446 import SendZC446
from views.send_zcx66 import SendZCX66


class SendMessageBySubID(QDialog):
    def __init__(self, username, token, selected_option, selected_ids):
        super().__init__()
        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids
        self.setWindowTitle("Send " + selected_option)
        self.setFixedSize(670, 400)

        self.data = None
        self.df = None

        # 主布局
        main_layout = QVBoxLayout(self)

        # 显示选择的选项
        option_label = QLabel(f"Currently selected option: {self.selected_option}")
        main_layout.addWidget(option_label)

        # 添加全选和全不选按钮的水平布局
        select_layout = QHBoxLayout()
        self.select_all_checkbox = QCheckBox("Select All")
        self.deselect_all_checkbox = QCheckBox("Deselect All")

        select_layout.addWidget(self.select_all_checkbox)
        select_layout.addWidget(self.deselect_all_checkbox)
        main_layout.addLayout(select_layout)

        # 表格
        self.table = QTableWidget(0, 3)  # 10行4列的表格
        self.table.setHorizontalHeaderLabels(["Select", "IOSS", "TrackingNumber"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)

        self.data = []
        # 生成数据
        self.create_data()

        # 动态调整表格行数
        row_count = len(self.data[0])
        self.table.setRowCount(row_count)
        # 填充表格
        for row in range(self.df.shape[0]):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)
            self.table.setItem(row, 1, QTableWidgetItem(self.df.iloc[row]['IOSS']))
            self.table.setItem(row, 2, QTableWidgetItem(self.df.iloc[row]['TrackingNumber']))

        main_layout.addWidget(self.table)

        # 设置列宽自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 自适应列宽
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 横向滚动条

        # 底部的确认和取消按钮
        bottom_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)  # 设置为默认按钮
        self.cancel_btn = QPushButton("Cancel")
        bottom_layout.addWidget(self.ok_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        # 连接按钮事件
        self.ok_btn.clicked.connect(self.on_confirm)  # 确认操作
        self.cancel_btn.clicked.connect(self.reject)  # 取消操作

        # 连接全选和全不选复选框的状态变化
        self.select_all_checkbox.stateChanged.connect(self.select_all)
        self.deselect_all_checkbox.stateChanged.connect(self.deselect_all)

    def create_data(self):
        self.data = db.get_id_ioss_tracking_number_by_main_id(self.selected_ids)
        self.df = pd.DataFrame({
            "IOSS": self.data[1],  # 示例数据
            "TrackingNumber": self.data[2]  # 示例数据
        })

    def on_confirm(self):
        """获取所有选中的ID列数据，作为整型列表返回"""
        selected_ids = []

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_ids.append(self.data[0][row])

        if len(selected_ids) == 0:
            QMessageBox.warning(self, "Warning", 'Please select at least one.')
            return  # 返回发送界面，保持对话框打开

        print("选中的ID列表:", selected_ids)

        if self.selected_option == "zc414":
            dialog = SendZC414(self.username, self.token, self.selected_option, selected_ids)
            # 如果第二个对话框被接受，继续关闭第一个对话框
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        elif self.selected_option == "zcx02":
            dialog = SendZCX02(self.username, self.token, self.selected_option, selected_ids)
            # 如果第二个对话框被接受，继续关闭第一个对话框
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        elif self.selected_option == "zcx08":
            dialog = SendZCX08(self.username, self.token, self.selected_option, selected_ids)
            # 如果第二个对话框被接受，继续关闭第一个对话框
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        elif self.selected_option == 'zc446':
            dialog = SendZC446(self.username, self.token, self.selected_option, selected_ids)
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        elif self.selected_option == 'zcx66':
            dialog = SendZCX66(self.username, self.token, self.selected_option, selected_ids)
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")

    def select_all(self, state):
        """全选复选框"""
        if state == Qt.Checked:
            self.deselect_all_checkbox.setChecked(False)  # 取消全不选
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)

    def deselect_all(self, state):
        """全不选复选框"""
        if state == Qt.Checked:
            self.select_all_checkbox.setChecked(False)  # 取消全选
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(False)
