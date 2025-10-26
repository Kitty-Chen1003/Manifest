import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QDialog, QVBoxLayout, QLineEdit, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QDialogButtonBox,
                             QCheckBox, QAbstractItemView, QMessageBox, QHeaderView)

from utils.path import get_resource_path
from views.selection_dialog import SelectionDialog


class GoodsitemManualInputMultipleElements(QDialog):
    def __init__(self, title, index, list_dict_detail, username, parent=None):
        super().__init__(parent)
        self.username = username

        self.setWindowTitle(title)
        self.index = index
        print(self.index)
        self.list_dict_detail = list_dict_detail
        self.setFixedSize(500, 500)

        self.nav_button_sheetstyle = """
            QPushButton {
                background-color: #3393FF;  /* 设置背景颜色 */
                color: white;               /* 设置文本颜色 */
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;  /* 鼠标悬停时的背景颜色 */
            }
            QPushButton:pressed {
                background-color: #3d8649;  /* 按下按钮时的背景颜色 */
            }
        """

        num_key = 5
        start_idx = 0
        self.list_key_name = [[]] * num_key
        self.list_key_name[start_idx] = ['reference number', 'type(CL214)', 'goodsItem identifier']
        self.list_key_name[start_idx + 1] = ['code(CL239)', 'text']
        self.list_key_name[start_idx + 2] = ['reference number', 'type(CL213)']
        self.list_key_name[start_idx + 3] = ['reference number', 'type(CL380)']
        self.list_key_name[start_idx + 4] = ['reference number', 'type(CL754)']

        self.label_key_name_width = [150] * num_key

        self.list_file_name = [[]] * num_key
        self.list_file_name[start_idx] = ['', 'CL214AIS', '']
        self.list_file_name[start_idx + 1] = ['CL239AIS', '']
        self.list_file_name[start_idx + 2] = ['', 'CL213AIS']
        self.list_file_name[start_idx + 3] = ['', 'CL380AIS']
        self.list_file_name[start_idx + 4] = ['', 'CL754AIS']

        self.list_key_name_is_must_fill = [[]] * num_key
        self.list_key_name_is_must_fill[start_idx] = [1, 1, 0]
        self.list_key_name_is_must_fill[start_idx + 1] = [1, 0]
        self.list_key_name_is_must_fill[start_idx + 2] = [1, 1]
        self.list_key_name_is_must_fill[start_idx + 3] = [1, 1]
        self.list_key_name_is_must_fill[start_idx + 4] = [1, 1]

        self.num_key = len(self.list_key_name[self.index])

        self.list_le = []
        self.list_btn = []

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Creating input fields and select buttons
        for i in range(len(self.list_key_name[self.index])):
            upper_layout = QHBoxLayout()

            label = QLabel(self)
            label.setText(self.list_key_name[self.index][i] + ':')
            label.setFixedWidth(self.label_key_name_width[self.index])
            upper_layout.addWidget(label)

            input_line_edit = QLineEdit(self)
            input_line_edit.setMinimumWidth(180)
            upper_layout.addWidget(input_line_edit)
            self.list_le.append(input_line_edit)

            select_button = QPushButton("Select", self)
            select_button.setStyleSheet(self.nav_button_sheetstyle)
            select_button.clicked.connect(
                lambda checked, idx=i, le=input_line_edit,
                       fn=self.list_file_name[self.index][i]: self.open_selection_dialog(
                    idx, le, fn))
            upper_layout.addWidget(select_button)
            self.list_btn.append(select_button)

            layout.addLayout(upper_layout)

        # Add button
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_to_table)
        self.add_button.setStyleSheet(self.nav_button_sheetstyle)
        layout.addWidget(self.add_button)

        # Table to show added items
        self.table_widget = QTableWidget(self)
        self.table_widget.setFixedHeight(120)  # Adjust the height as needed
        self.table_widget.setColumnCount(self.num_key)
        self.table_widget.setHorizontalHeaderLabels(self.list_key_name[self.index])
        values_list = [list(d.values()) for d in self.list_dict_detail]
        # print(values_list)

        for i in range(len(values_list)):
            row_data = values_list[i]
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                self.table_widget.setItem(row_position, col, item)

        # Set column and row resizing
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table non-editable
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # Select whole row
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)  # Only one row can be selected

        self.table_widget.itemSelectionChanged.connect(self.update_button_state)

        layout.addWidget(self.table_widget)

        # Delete button
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_selected_row)
        layout.addWidget(self.delete_button)

        # Checkbox for "Add to All"
        # self.checkbox = QCheckBox("Add to All", self)
        # layout.addWidget(self.checkbox)

        # OK and Cancel buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def update_button_state(self):
        # 检查是否有选中的行
        selected_items = self.table_widget.selectedItems()
        if selected_items:
            self.delete_button.setEnabled(True)  # 有选中行，启用按钮
        else:
            self.delete_button.setEnabled(False)  # 无选中行，禁用按钮

    def open_selection_dialog(self, index, line_edit, files_name):
        if files_name != "":
            json_file_path = "config/customs_dictionary/" + files_name + ".json"
            json_file_path = get_resource_path(json_file_path)
            title = files_name + " code"
        else:
            json_file_path = ''  # Replace with the actual path
            title = "cache"
        height = 1275
        width = 820
        input_id = (self.index + 1) * 1000 + index
        dialog = SelectionDialog(input_id, json_file_path, title, height, width, self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            row_data, columns = dialog.getSelectedRowData()
            if row_data:
                line_edit.setText(row_data[0])

    def add_to_table(self):
        """ Add a new row to the table with the current input field values """
        # 获取当前索引需要填写的字段和输入框
        current_key_names = self.list_key_name[self.index]  # 当前组的所有字段名
        current_inputs = self.list_le  # 当前组的所有输入框
        current_must_fill_flags = self.list_key_name_is_must_fill[self.index]  # 当前组的字段是否必填标记

        # 遍历当前需要填写的字段和输入框
        for i, (key_name, input_field, must_fill) in enumerate(
                zip(current_key_names, current_inputs, current_must_fill_flags)):
            # 如果该字段是必填并且输入框为空，则弹出警告框
            if must_fill == 1 and not input_field.text().strip():
                QMessageBox.warning(self, "Input Error", f"Please fill {key_name}.")
                return  # 退出函数，不继续执行后面的操作

        if self.index in [0]:
            if self.table_widget.rowCount() == 99:
                QMessageBox.warning(self, "Input Error", f"The number of {self.title} must be no more than 99.")
                return
            if not len(current_inputs[0].text()) <= 70:
                QMessageBox.warning(self, "Input Error", f"{current_key_names[0]} must be no more than 70 digits.")
                return
            if not len(current_inputs[1].text()) == 4:
                QMessageBox.warning(self, "Input Error", f"{current_key_names[1]} must be 4 digits.")
                return
            if len(current_inputs[2].text()) > 0:
                if current_inputs[2].text().isdigit():
                    if not len(current_inputs[2].text()) <= 5:
                        QMessageBox.warning(self, "Input Error", f"{current_key_names[2]} must be no more than 5 digits.")
                        return
                else:
                    QMessageBox.warning(self, "Input Error", f"{current_key_names[2]} must be an integer.")
                    return
        elif self.index in [1]:
            if self.table_widget.rowCount() == 99:
                QMessageBox.warning(self, "Input Error", f"The number of {self.title} must be no more than 99.")
                return
            if not len(current_inputs[0].text()) == 5:
                QMessageBox.warning(self, "Input Error", f"{current_key_names[0]} must be 5 digits.")
                return
            if len(current_inputs[1].text()) > 0:
                if not len(current_inputs[1].text()) <= 512:
                    QMessageBox.warning(self, "Input Error", f"{current_key_names[1]} must be no more than 512 digits.")
                    return
        elif self.index in [2, 3, 4]:
            if self.table_widget.rowCount() == 99:
                QMessageBox.warning(self, "Input Error", f"The number of {self.title} must be no more than 99.")
                return
            if not len(current_inputs[0].text()) <= 70:
                QMessageBox.warning(self, "Input Error", f"{current_key_names[0]} must be no more than 70 digits.")
                return
            if not len(current_inputs[1].text()) == 4:
                QMessageBox.warning(self, "Input Error", f"{current_key_names[1]} must be 4 digits.")
                return

        # 获取输入框数据
        row_data = [le.text().strip() for le in current_inputs]  # 获取输入框的值，并去除空格
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        for col, value in enumerate(row_data):
            item = QTableWidgetItem(value)
            self.table_widget.setItem(row_position, col, item)

        # Clear input fields after adding the row
        for le in self.list_le:
            le.clear()

    def delete_selected_row(self):
        """ Delete the selected row from the table """
        selected_rows = self.table_widget.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No row selected to delete.")
            return

        # Delete rows in reverse order to avoid indexing issues
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            self.table_widget.removeRow(row)

    def get_table_data(self):
        """ Convert table data to a list of dictionaries """
        table_data = []
        headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]

        for row in range(self.table_widget.rowCount()):
            row_data = {}
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                row_data[headers[col]] = item.text() if item else ""
            table_data.append(row_data)
        # print('list_dict_detail:', self.list_dict_detail)
        # print('table_data:', table_data)
        update_cache_dict = {}
        all_values = {key: [d[key] for d in table_data if key in d] for key in self.list_key_name[self.index]}

        for key, values in all_values.items():
            cache_id = (self.index + 1) * 1000 + self.list_key_name[self.index].index(key)
            update_cache_dict[cache_id] = values
        # print('update_cache_dict:', update_cache_dict)

        return table_data, update_cache_dict


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoodsitemManualInputMultipleElements("Test Dialog", [], 0)
    window.show()
    sys.exit(app.exec_())
