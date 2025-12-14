from datetime import datetime, timedelta

import pandas as pd
import pytz
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QAbstractItemView,
    QMessageBox, QHeaderView, QLabel, QDateTimeEdit
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
        self.is_upd_mode = None
        self.full_upd_data = None

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

        self.today_btn = QPushButton("Today")
        self.time_filter_layout.addWidget(self.today_btn)
        self.today_btn.clicked.connect(self.filter_today)

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

    def filter_by_time(self, today_only=False):
        if not self.is_upd_mode or self.full_upd_data is None:
            return

        if today_only:

            pl_tz = pytz.timezone("Europe/Warsaw")
            pl_now = datetime.now(pl_tz)
            start_dt = pl_now.replace(hour=0, minute=0, second=0, microsecond=0)

        else:
            """根据选择的时间范围刷新表格"""
            start_dt = pd.to_datetime(
                self.start_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            )

        end_dt = pd.to_datetime(
            self.end_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        )
        filtered = [[], [], [], []]

        for i, t in enumerate(self.full_upd_data[1]):

            if not t:
                continue

            try:
                event_time = pd.to_datetime(t)
            except Exception:
                continue

            if start_dt <= event_time <= end_dt:
                for col in range(4):
                    filtered[col].append(self.full_upd_data[col][i])

        self.update_upd_table(filtered)

    def filter_today(self):
        if not self.is_upd_mode or self.full_upd_data is None:
            return

        pl_tz = pytz.timezone("Europe/Warsaw")
        pl_now = datetime.now(pl_tz)
        one_week_ago = pl_now - timedelta(days=7)

        self.start_time_edit.setDateTime(one_week_ago)
        self.end_time_edit.setDateTime(pl_now)

        pl_tz = pytz.timezone("Europe/Warsaw")
        now = datetime.now(pl_tz)

        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        self.start_time_edit.setDateTime(start_of_day)
        self.end_time_edit.setDateTime(end_of_day)

        # 复用原有时间筛选逻辑
        self.filter_by_time()

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

    def update_upd_table(self, data):
        """data 格式: [main_ids, event_times, ids, message_ids]"""
        self.data = data  # ⭐ 当前显示数据

        # 更新表格结构为 4 列
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Select", "ID", "message_id", "Event Time"])

        # 填充表格数据
        self.table.setRowCount(len(data[0]))
        for row in range(len(data[0])):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            self.table.setItem(row, 1, QTableWidgetItem(str(data[0][row])))  # ID
            self.table.setItem(row, 2, QTableWidgetItem(str(data[3][row])))  # ID
            self.table.setItem(row, 3, QTableWidgetItem(data[1][row]))  # Time

    def update_table_data(self, selected_option):
        """根据下拉框选项更新表格数据和结构"""
        if selected_option == "upd":
            self.is_upd_mode = True

            for i in range(self.time_filter_layout.count()):
                self.time_filter_layout.itemAt(i).widget().show()

            pl_tz = pytz.timezone("Europe/Warsaw")
            pl_now = datetime.now(pl_tz)
            one_week_ago = pl_now - timedelta(days=7)

            self.start_time_edit.setDateTime(one_week_ago)
            self.end_time_edit.setDateTime(pl_now)

            # 获取 upd 数据
            new_data = db.get_receive_upd(self.username, flag=1)  # 返回类似 ([IDs], [AirWayBills], [Times]) 的格式
            self.full_upd_data = [
                [t[1] for t in new_data],  # 第0个元素列表 main_id
                [t[5] for t in new_data],  # 第5个元素列表 event_time
                [t[0] for t in new_data],  # 第1个元素列表 ID
                [t[10] for t in new_data],  # 第10个元素列表 main_id
            ]

            # 初始显示：不加时间过滤
            self.update_upd_table(self.full_upd_data)
            # self.data = new_data
            #
            # # 更新表格结构为 4 列
            # self.table.setColumnCount(4)
            # self.table.setHorizontalHeaderLabels(["Select", "ID", "message_id", "Event Time"])
            #
            # # 填充表格数据
            # self.table.setRowCount(len(new_data[0]))
            # for row in range(len(new_data[0])):
            #     checkbox = QCheckBox()
            #     self.table.setCellWidget(row, 0, checkbox)  # 设置复选框
            #     self.table.setItem(row, 1, QTableWidgetItem(str(new_data[0][row])))  # ID
            #     self.table.setItem(row, 2, QTableWidgetItem(str(new_data[3][row])))  # ID
            #     self.table.setItem(row, 3, QTableWidgetItem(new_data[1][row]))  # Time

        else:
            self.is_upd_mode = False
            self.full_upd_data = None

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
