import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QAbstractItemView,
    QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

from utils import db

from views.save_pdf_or_xml import SavePDFOrXML
from views.generate_pdf_and_xml_by_sub_id import GeneratePDFAndXMLBySubID


class ClearData(QDialog):
    def __init__(self, username, token):
        super().__init__()
        self.username = username
        self.token = token

        self.setWindowTitle("Clear Data")
        self.setFixedSize(500, 400)

        self.data = None

        # 主布局
        main_layout = QVBoxLayout(self)

        # 下拉菜单
        control_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItems(["UPD", "UPD-signed", "zc429", "zcx03", "zcx64", "zcx65", "zc410", "zc460"])
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
        self.update_table_data(self.combo_box.currentText())

    def update_table_data(self, selected_option):
        print(selected_option)
        """根据下拉框选项更新表格数据和结构"""
        if selected_option in ["UPD"]:
            # 获取 upd 数据
            new_data = db.get_receive_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            self.update_list(new_data)
        elif selected_option in ["UPD-signed"]:
            # 获取 upd 数据
            new_data = db.get_send_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            self.update_list(new_data)
        elif selected_option in ['zc429', "zcx03", "zcx64", "zcx65", "zc410", "zc460"]:
            # 这里是选择出了upd意外的针对账户的数据
            new_data = db.get_xml_data_by_type(self.username, [selected_option])
            self.update_list(new_data)

    def update_list(self, new_data):
        new_data = [
            [t[1] for t in new_data],  # 第1个元素列表 main_id
            [t[5] for t in new_data],  # 第5个元素列表 event_time
            [t[0] for t in new_data],  # 第0个元素列表 id
            [t[10] for t in new_data],  # 第10个元素列表 id
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
            self.table.setItem(row, 1, QTableWidgetItem(new_data[0][row]))  # main_id
            self.table.setItem(row, 2, QTableWidgetItem(new_data[3][row]))  # message_id
            self.table.setItem(row, 3, QTableWidgetItem(new_data[1][row]))  # Time

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
        print(selected_option)
        if len(selected_ids) == 0:
            QMessageBox.warning(self, "Warning", 'Please select at least one.')
            return  # 返回发送界面，保持对话框打开

        main_id_list = selected_ids
        local_id_list = []
        for select_id in selected_ids:
            for i in range(len(self.data[0])):
                if select_id == self.data[0][i]:
                    local_id_list.append(self.data[2][i])
        id_list = {
            'main_id_list': main_id_list,
            'local_id_list': local_id_list
        }
        if self.token:
            print(id_list)
            dialog = SavePDFOrXML(self.username, selected_option, id_list, self.token)
            if dialog.exec_() == QDialog.Accepted:
                self.accept()  # 关闭原对话框
            else:
                print("已取消操作，返回到第一个对话框。")
        else:
            QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect')
            return  # 返回发送界面，保持对话框打开

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
