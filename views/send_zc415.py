from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QComboBox, QCheckBox, QPushButton, QAbstractItemView,
    QMessageBox, QHeaderView, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
import pandas as pd
from utils import db
from communication import http_client
from views.signature_interface import SignatureDialog
from views.input_signature_info import InputSignatureInfo


class SendZC415(QDialog):
    def __init__(self, username, token):
        super().__init__()
        self.username = username
        self.token = token

        self.setWindowTitle("Send ZC415")
        self.setFixedSize(500, 400)

        self.data = None

        # 主布局
        main_layout = QVBoxLayout(self)

        # 创建选项按钮组
        radio_button_layout = QHBoxLayout()
        self.goods_shipment_radio = QRadioButton("GrossMass-GoodsShipment")
        self.goods_item_radio = QRadioButton("GrossMass-GoodsItem")
        self.radio_group = QButtonGroup(self)  # 创建按钮组
        self.radio_group.addButton(self.goods_shipment_radio)
        self.radio_group.addButton(self.goods_item_radio)

        # 添加到布局
        radio_button_layout.addWidget(self.goods_shipment_radio)
        radio_button_layout.addWidget(self.goods_item_radio)
        main_layout.addLayout(radio_button_layout)

        # 下拉菜单
        control_layout = QHBoxLayout()
        self.combo_box = QComboBox()
        self.combo_box.addItems(["zc415"])
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
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 生成示例数据并填充表格
        self.create_data()
        main_layout.addWidget(self.table)

        # 底部的确认和取消按钮
        bottom_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        self.cancel_btn = QPushButton("Cancel")
        bottom_layout.addWidget(self.ok_btn)
        bottom_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(bottom_layout)

        # 连接按钮事件
        self.ok_btn.clicked.connect(self.on_confirm)
        self.cancel_btn.clicked.connect(self.reject)
        self.select_all_checkbox.stateChanged.connect(self.select_all)
        self.deselect_all_checkbox.stateChanged.connect(self.deselect_all)

    def create_data(self):
        self.data = db.get_id_and_airwaybill_from_main_table_by_state_not_sent(self.username)
        """生成示例数据并填充到表格中"""
        pd_data = {
            "AirWayBill": self.data[1]  # 示例AirWayBill
        }
        df = pd.DataFrame(pd_data)

        row_count = len(self.data[0])
        self.table.setRowCount(row_count)

        # 填充表格
        for row in range(df.shape[0]):
            checkbox = QCheckBox()
            self.table.setCellWidget(row, 0, checkbox)
            self.table.setItem(row, 1, QTableWidgetItem(df.iloc[row]['AirWayBill']))

    def on_confirm(self):
        """获取所有选中的ID列数据，作为整型列表返回"""
        selected_ids = []

        # 检查选项按钮组的状态
        if not self.goods_shipment_radio.isChecked() and not self.goods_item_radio.isChecked():
            QMessageBox.warning(self, "Warning", "Please select either GoodsShipment or GoodsItem.")
            return  # 返回发送界面，保持对话框打开

        # 获取选中的选项按钮的值
        selected_radio_value = "GoodsShipment" if self.goods_shipment_radio.isChecked() else "GoodsItem"

        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_ids.append(self.data[0][row])

        # 获取当前下拉菜单的内容
        selected_option = self.combo_box.currentText()

        if len(selected_ids) == 0:
            QMessageBox.warning(self, "Warning", 'Please select at least one.')
            return  # 返回发送界面，保持对话框打开

        if selected_option == "zc415":
            dialog = InputSignatureInfo(selected_option)
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
                    for main_id in selected_ids:
                        data = {
                            'username': self.username,
                            'generation_method': selected_radio_value
                        }
                        main_table_data = db.fetch_zc415_data_by_main_id(main_id)
                        data.update(main_table_data)
                        three_table_data = db.fetch_data_of_send_zc415(main_id, self.username)
                        data.update(three_table_data)
                        response_status_code, datas_subid_lrn = http_client.upload_excel_data(
                            self.token,
                            data,
                            file_path,
                            password,
                            signature_information
                        )
                        if response_status_code == 200:
                            db.update_state_to_sent(main_id)
                            for data_subid_lrn in datas_subid_lrn:
                                db.update_sub_table(data_subid_lrn[0], new_lrn=data_subid_lrn[1])
                        else:
                            QMessageBox.warning(self, "Error",
                                                f'Sending {main_id} failed (Maybe the signature password is wrong!), please try again.')
                            return
                        QMessageBox.information(self, "Result", 'Send zc415 successfully!')
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

    def select_all(self, state):
        """全选复选框"""
        if state == Qt.Checked:
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(True)
            self.deselect_all_checkbox.setChecked(False)

    def deselect_all(self, state):
        """取消全选复选框"""
        if state == Qt.Checked:
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                if checkbox:
                    checkbox.setChecked(False)
            self.select_all_checkbox.setChecked(False)
