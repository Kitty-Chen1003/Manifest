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


class GeneratePDFAndXML(QDialog):
    def __init__(self, username, token):
        super().__init__()
        self.username = username
        self.token = token

        self.setWindowTitle("Generate PDF/XML file")
        self.setFixedSize(500, 400)

        self.option_to_xml_type = {
            'PDF-zc428': 'zc428',
            'PDF-zcx16': 'zcx16',
            'PDF-zc429': 'zc429',
            'PDF-zcx03': 'zcx03',
            'PDF-zcx64': 'zcx64',
            'PDF-zcx65': 'zcx65',
            'PDF-zc410': 'zc410',
            'PDF-zc460': 'zc460',
            'XML-zc428': 'zc428',
            'XML-zcx16': 'zcx16',
            'XML-zc429': 'zc429',
            'XML-zcx03': 'zcx03',
            'XML-zcx64': 'zcx64',
            'XML-zcx65': 'zcx65',
            'XML-zc410': 'zc410',
            'XML-zc460': 'zc460',
            'XML-UPD': 'upd',
            'XML-UPD-signed': 'signed_upd'
        }

        self.data = None

        # 主布局
        main_layout = QVBoxLayout(self)

        # 下拉菜单
        control_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItems(
            ["PDF", "PDF-zc428", "PDF-zcx16", "PDF-UPD", "PDF-UPD-signed", "PDF-zc429", "PDF-zcx03", "PDF-zcx64",
             "PDF-zcx65", "PDF-zc410", "PDF-zc460",
             "XML", "XML-zc428", "XML-zcx16", "XML-UPD", "XML-UPD-signed", "XML-zc429", "XML-zcx03", "XML-zcx64",
             "XML-zcx65", "XML-zc410", "XML-zc460"])
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
        if selected_option in ["PDF-UPD", "XML-UPD"]:
            # 获取 upd 数据
            new_data = db.get_receive_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            self.update_list(new_data)
        elif selected_option in ["PDF-UPD-signed", "XML-UPD-signed"]:
            # 获取 upd 数据
            new_data = db.get_send_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            self.update_list(new_data)
        elif selected_option in ['PDF-zc429', "PDF-zcx03", "PDF-zcx64", "PDF-zcx65", "PDF-zc410", "PDF-zc460",
                                 'XML-zc429', "XML-zcx03", "XML-zcx64", "XML-zcx65", "XML-zc410", "XML-zc460"]:
            # 这里是选择出了upd意外的针对账户的数据
            xml_type = self.option_to_xml_type[selected_option]
            new_data = db.get_xml_data_by_type(self.username, [xml_type])
            self.update_list(new_data)
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

        if selected_option in ['PDF', 'XML']:
            if len(selected_ids) == 0:
                QMessageBox.warning(self, "Warning", 'Please select at least one.')
                return  # 返回发送界面，保持对话框打开

            if self.token:
                dialog = GeneratePDFAndXMLBySubID(self.username, self.token, selected_option, selected_ids)
                if dialog.exec_() == QDialog.Accepted:
                    self.accept()  # 关闭原对话框
                else:
                    print("已取消操作，返回到第一个对话框。")
        elif selected_option in ["PDF-UPD", "PDF-UPD-signed", "XML-UPD", "XML-UPD-signed", "PDF-zc429", "XML-zc429",
                                 "PDF-zcx03", "PDF-zcx64", "PDF-zcx65", "PDF-zc410", "PDF-zc460",
                                 "XML-zcx03", "XML-zcx64", "XML-zcx65", "XML-zc410", "XML-zc460"]:
            main_id_list = []
            if selected_option in ["PDF-UPD", "PDF-UPD-signed", "PDF-zc429", "PDF-zcx03", "PDF-zcx64", "PDF-zcx65",
                                   "PDF-zc410", "PDF-zc460"]:
                for select_id in selected_ids:
                    for i in range(len(self.data[0])):
                        if select_id == self.data[0][i]:
                            main_id_list.append(self.data[2][i])
            else:
                main_id_list = selected_ids
            if self.token:
                dialog = SavePDFOrXML(self.username, selected_option, main_id_list, self.token)
                if dialog.exec_() == QDialog.Accepted:
                    self.accept()  # 关闭原对话框
                else:
                    print("已取消操作，返回到第一个对话框。")
            else:
                QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect')
                return  # 返回发送界面，保持对话框打开
        elif selected_option in ['PDF-zc428', 'XML-zc428', 'PDF-zcx16', 'XML-zcx16']:
            if self.token:
                dialog = SavePDFOrXML(self.username, selected_option, selected_ids, self.token)
                if dialog.exec_() == QDialog.Accepted:
                    self.accept()  # 关闭原对话框
                else:
                    print("已取消操作，返回到第一个对话框。")
            else:
                QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect')
                return  # 返回发送界面，保持对话框打开
            pass

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
