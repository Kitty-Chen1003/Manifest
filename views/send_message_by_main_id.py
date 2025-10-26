import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QAbstractItemView,
    QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from views.send_message_by_sub_id import SendMessageBySubID  # 导入子对话框

from utils import db
from views.send_upd import SendUPD


class SendMessageByMainID(QDialog):
    def __init__(self, username, token):
        super().__init__()
        self.username = username
        self.token = token

        self.setWindowTitle("Send message")
        self.setFixedSize(500, 400)

        self.data = None

        self.select_opt = None

        # 主布局
        main_layout = QVBoxLayout(self)

        # 下拉菜单
        control_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItems(["zc414", "zcx02", "zcx08", "zcx66", "zc446", "upd"])
        self.combo_box.currentTextChanged.connect(self.update_table_data)
        control_layout.addWidget(self.combo_box)

        # 全选和全部取消的复选框
        self.select_all_checkbox = QCheckBox("Select All")
        self.deselect_all_checkbox = QCheckBox("Deselect All")
        control_layout.addWidget(self.select_all_checkbox)
        control_layout.addWidget(self.deselect_all_checkbox)
        main_layout.addLayout(control_layout)

        # 表格
        self.table = QTableWidget(0, 2)  # 10行3列的表格
        self.table.setHorizontalHeaderLabels(["Select", "AirWayBill"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)  # 自适应内容
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 横向滚动条
        # self.table.verticalHeader().setVisible(False)

        # 设置列宽自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 生成示例数据并填充表格
        self.create_data()

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

    def create_data(self):
        self.data = db.get_id_and_airwaybill_from_main_table_by_state_sent(self.username)
        """生成示例数据并填充到表格中"""
        # 生成数据
        pd_data = {
            "AirWayBill": self.data[1]  # 示例AirWayBill
        }
        df = pd.DataFrame(pd_data)

        row_count = len(self.data[0])
        self.table.setRowCount(row_count)

        # 填充表格
        for row in range(df.shape[0]):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            self.table.setItem(row, 1, QTableWidgetItem(df.iloc[row]['AirWayBill']))  # AirWayBill列

    def update_table_data(self, selected_option):
        """根据下拉框选项更新表格数据和结构"""
        if selected_option == "upd":
            # 获取 upd 数据
            new_data = db.get_receive_upd(self.username, flag=1)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            new_data = [
                [t[1] for t in new_data],  # 第0个元素列表 main_id
                [t[5] for t in new_data],  # 第5个元素列表 event_time
                [t[0] for t in new_data],  # 第1个元素列表 ID
                [t[10] for t in new_data],  # 第10个元素列表 main_id
            ]
            self.data = new_data

            # 更新表格结构为 4 列
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Select", "ID", "message_id", "Event Time"])

            # 填充表格数据
            self.table.setRowCount(len(new_data[0]))
            for row in range(len(new_data[0])):
                checkbox = QCheckBox()
                self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
                self.table.setItem(row, 1, QTableWidgetItem(str(new_data[0][row])))  # ID
                self.table.setItem(row, 2, QTableWidgetItem(str(new_data[3][row])))  # ID
                self.table.setItem(row, 3, QTableWidgetItem(new_data[1][row]))  # Time

        else:
            # 获取默认数据
            default_data = db.get_id_and_airwaybill_from_main_table_by_state_sent(self.username)
            self.data = default_data

            # 更新表格结构为 2 列
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["Select", "AirWayBill"])

            # 填充表格数据
            self.table.setRowCount(len(default_data[0]))
            for row in range(len(default_data[0])):
                checkbox = QCheckBox()
                self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
                self.table.setItem(row, 1, QTableWidgetItem(default_data[1][row]))  # AirWayBill

    def on_confirm(self):
        """获取所有选中的ID列数据，作为整型列表返回"""
        selected_ids = []

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_ids.append(self.data[0][row])

        print(selected_ids)

        # 获取当前下拉菜单的内容
        selected_option = self.combo_box.currentText()
        self.select_opt = selected_option

        if len(selected_ids) == 0:
            QMessageBox.warning(self, "Warning", 'Please select at least one.')
            return  # 返回发送界面，保持对话框打开

        if selected_option == 'upd':
            dialog = SendUPD(self.username, self.token, selected_ids)
            # 如果第二个对话框被接受，继续关闭第一个对话框
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        else:
            # 创建并显示新的对话框
            data_dialog = SendMessageBySubID(self.username, self.token, selected_option, selected_ids)

            # 如果第二个对话框被接受，继续关闭第一个对话框
            if data_dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")

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

    def get_selection_opt(self):
        return self.select_opt
