from datetime import datetime, timedelta

import pandas as pd
import pytz
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QAbstractItemView,
    QMessageBox, QHeaderView, QLabel, QDateTimeEdit
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
        self.table = QTableWidget(0, 3)  # 10行3列的表格
        self.table.setHorizontalHeaderLabels(["Select", "AirWayBill", "Created Time"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)  # 自适应内容
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 横向滚动条
        # self.table.verticalHeader().setVisible(False)

        # 设置列宽自适应
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 生成示例数据并填充表格
        self.create_data()

        self.time_filter_layout = QHBoxLayout()

        start_label = QLabel("Start Time:")
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time_edit.setCalendarPopup(True)

        end_label = QLabel("End Time:")
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time_edit.setCalendarPopup(True)

        self.filter_btn = QPushButton("Filter Time")

        self.time_filter_layout.addWidget(start_label)
        self.time_filter_layout.addWidget(self.start_time_edit)
        self.time_filter_layout.addWidget(end_label)
        self.time_filter_layout.addWidget(self.end_time_edit)
        self.time_filter_layout.addWidget(self.filter_btn)

        # 初始隐藏
        for i in range(self.time_filter_layout.count()):
            self.time_filter_layout.itemAt(i).widget().hide()

        main_layout.addLayout(self.time_filter_layout)

        # 绑定按钮事件
        self.filter_btn.clicked.connect(self.filter_by_time)

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

    def filter_by_time(self):
        """根据选择的时间范围刷新表格"""
        start_time = self.start_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_time = self.end_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        if hasattr(self, 'full_data'):
            # **基于完整数据筛选，而不是 self.data**
            self.update_list(self.full_data, start_time=start_time, end_time=end_time)

        self.update_list(self.full_data, start_time=start_time, end_time=end_time)

    def create_data(self):
        # self.data = db.get_id_and_airwaybill_from_main_table_by_state_sent(self.username)
        self.data = db.get_id_airwaybill_time_from_main_table_by_state_sent(self.username)
        """生成示例数据并填充到表格中"""

        ids = self.data[0]
        airwaybills = self.data[1]
        created_times = self.data[2] if len(self.data) > 2 else [""] * len(ids)  # 如果没有返回，填空

        row_count = len(ids)
        self.table.setRowCount(row_count)

        # 填充表格
        for row in range(row_count):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            awb = airwaybills[row] if airwaybills[row] is not None else ""
            self.table.setItem(row, 1, QTableWidgetItem(awb))

            # created_time
            ctime = created_times[row] if created_times[row] is not None else ""
            self.table.setItem(row, 2, QTableWidgetItem(str(ctime)))

    def update_table_data(self, selected_option):
        time_filter_options = [
            "PDF-UPD", "XML-UPD",
            "PDF-UPD-signed", "XML-UPD-signed",
            "PDF-zcx03", "PDF-zcx64", "PDF-zcx65", "PDF-zc410",
            "XML-zcx03", "XML-zcx64", "XML-zcx65", "XML-zc410"
        ]

        if selected_option in time_filter_options:
            # 显示时间筛选控件
            for i in range(self.time_filter_layout.count()):
                self.time_filter_layout.itemAt(i).widget().show()

            pl_tz = pytz.timezone("Europe/Warsaw")
            pl_now = datetime.now(pl_tz)
            one_week_ago = pl_now - timedelta(days=7)

            self.start_time_edit.setDateTime(one_week_ago)
            self.end_time_edit.setDateTime(pl_now)

            if selected_option in ["PDF-UPD", "XML-UPD"]:
                # 获取 upd 数据
                new_data = db.get_receive_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            elif selected_option in ["PDF-UPD-signed", "XML-UPD-signed"]:
                # 获取 upd 数据
                new_data = db.get_send_upd(self.username)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            else:
                # 这里是选择出了upd意外的针对账户的数据
                xml_type = self.option_to_xml_type[selected_option]
                new_data = db.get_xml_data_by_type(self.username, [xml_type])

            self.full_data = new_data

            self.update_list(new_data)

        else:
            # 隐藏时间控件
            for i in range(self.time_filter_layout.count()):
                self.time_filter_layout.itemAt(i).widget().hide()

            # 获取默认数据
            # default_data = db.get_id_and_airwaybill_from_main_table_by_state_sent(self.username)
            default_data = db.get_id_airwaybill_time_from_main_table_by_state_sent(self.username)
            self.data = default_data

            ids = default_data[0]
            airwaybills = default_data[1]
            created_times = default_data[2] if len(default_data) > 2 else [""] * len(ids)

            # 更新表格结构为 2 列
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["Select", "AirWayBill", "Created Time"])

            # 填充表格数据
            # self.table.setRowCount(len(default_data[0]))
            row_count = len(ids)
            self.table.setRowCount(row_count)

            for row in range(row_count):
                checkbox = QCheckBox()
                self.table.setCellWidget(row, 0, checkbox)  # 设置复选框

                # AirWayBill
                awb = airwaybills[row] if airwaybills[row] is not None else ""
                self.table.setItem(row, 1, QTableWidgetItem(awb))

                # created_time
                ctime = created_times[row] if created_times[row] is not None else ""
                self.table.setItem(row, 2, QTableWidgetItem(str(ctime)))

    def update_list(self, new_data, start_time=None, end_time=None):

        # 重新组织数据结构
        main_ids = [t[1] for t in new_data]
        event_times = [t[5] for t in new_data]
        ids = [t[0] for t in new_data]
        message_ids = [t[10] for t in new_data]

        # 时间过滤
        filtered_indices = []
        for i, t in enumerate(event_times):
            if not t:
                continue
            t_dt = pd.to_datetime(t)  # 将字符串转为 datetime
            if start_time:
                start_dt = pd.to_datetime(start_time)
                if t_dt < start_dt:
                    continue
            if end_time:
                end_dt = pd.to_datetime(end_time)
                if t_dt > end_dt:
                    continue
            filtered_indices.append(i)

        # 筛选后的数据
        main_ids = [main_ids[i] for i in filtered_indices]
        event_times = [event_times[i] for i in filtered_indices]
        ids = [ids[i] for i in filtered_indices]
        message_ids = [message_ids[i] for i in filtered_indices]

        self.data = [main_ids, event_times, ids, message_ids]

        # 更新表格结构为 4 列
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "ID", "message_id", "Event Time"])

        # 填充表格数据
        # self.table.setRowCount(len(new_data[0]))
        self.table.setRowCount(len(main_ids))
        # for row in range(len(new_data[0])):
        for row in range(len(main_ids)):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            self.table.setItem(row, 1, QTableWidgetItem(main_ids[row]))  # main_id
            self.table.setItem(row, 2, QTableWidgetItem(message_ids[row]))  # message_id
            self.table.setItem(row, 3, QTableWidgetItem(str(event_times[row])))  # Time

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
        elif selected_option in ["PDF-UPD", "PDF-UPD-signed", "XML-UPD", "XML-UPD-signed",
                                 "PDF-zcx03", "PDF-zcx64", "PDF-zcx65", "PDF-zc410",
                                 "XML-zcx03", "XML-zcx64", "XML-zcx65", "XML-zc410"]:
            main_id_list = []
            if selected_option in ["PDF-UPD", "PDF-UPD-signed", "PDF-zcx03", "PDF-zcx64", "PDF-zcx65",
                                   "PDF-zc410"]:
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
        elif selected_option in ["PDF-zc428", "XML-zc428", "PDF-zcx16", "XML-zcx16",
                                 "PDF-zc429", "XML-zc429", "PDF-zc460", "XML-zc460"]:
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
