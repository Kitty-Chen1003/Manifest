import pandas as pd
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QCheckBox,
    QAbstractItemView, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

from utils import db

from views.goodshipment_cl380_manual_change import GoodshiomentCL380ManualChange


class ChangeCL380BySubID(QDialog):
    def __init__(self, username, token, selected_option, selected_ids):
        super().__init__()
        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids
        self.setWindowTitle("Change CL380 of sub table-goodsshipment")
        self.setFixedSize(670, 400)

        self.data = None
        self.df = None

        self.update_cache_dict = {}

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

        # 生成数据
        self.create_data()
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

        if self.selected_option == 'CL380':
            dialog = GoodshiomentCL380ManualChange(self.username)
            if dialog.exec_() == QDialog.Accepted:
                input_data, update_cache_dict = dialog.get_table_data()
                self.update_cache_dict.update(update_cache_dict)

                for sub_id in selected_ids:
                    db.update_sub_table(sub_id, new_sub_table_data=input_data)

                self.update_cache()

                QMessageBox.information(self, "Result", 'Change CL380 successfully!')

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
