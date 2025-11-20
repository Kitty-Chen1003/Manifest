import sys

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QDialog, QDialogButtonBox, QVBoxLayout, QApplication
from views.goodsitem_manual_input_multiple_elements import GoodsitemManualInputMultipleElements

from utils import db


class GoodsitemManualInformation(QDialog):
    # def __init__(self, index, input_information, temp_input_information, parent=None):
    def __init__(self, index, goodsitem_information, goodshipment_information, username, parent=None):
        super().__init__(parent)

        self.username = username

        self.setWindowTitle("Goodsitem manual information")
        self.setGeometry(100, 100, 600, 500)

        self.nav_button_sheetstyle = """
            QPushButton {
                background-color: #3393FF;  /* 设置背景颜色 */
                color: white;               /* 设置文本颜色 */
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;  /* 鼠标悬停时的背景颜色 */
            }
            QPushButton:pressed {
                background-color: #3d8649;  /* 按下按钮时的背景颜色 */
            }
        """

        self.nav_button_sheetstyle_active = """
            QPushButton {
                background-color: #3d8649;  /* 设置背景颜色 */
                color: white;               /* 设置文本颜色 */
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;  /* 鼠标悬停时的背景颜色 */
            }
            QPushButton:pressed {
                background-color: #1abc9c;  /* 按下按钮时的背景颜色 */
            }
        """
        self.update_cache_dict = {}

        self.keys_input_information = [
            'goodsitem previous document',
            'goodsitem additional information',
            'goodsitem supporting document',
            'goodsitem additional reference',
            'goodsitem transport document'
        ]

        self.input_information = goodsitem_information
        # self.temp_input_information = goodsitem_information.copy()
        self.goodshipment_information = goodshipment_information

        num_key = 5

        self.le_read_only = [0] * num_key
        for i in range(0, 5):
            self.le_read_only[i] = 1

        # Layout for the dialog
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # Absolute positioning
        button_widths = [100]
        button_height = 30
        input_width = 200
        input_height = 30

        x_position = 50  # 初始的X位置

        button_names = ["GoodsItem"]

        # Create buttons with absolute positioning
        self.buttons = []
        for i, name in enumerate(button_names):
            button = QPushButton(name, self)
            button_width = button_widths[i]
            button.setGeometry(x_position, 50, button_width, button_height)
            # 更新下一个按钮的起始X位置
            x_position += button_width + 10  # 按钮宽度 + 间距

            button.setStyleSheet(self.nav_button_sheetstyle)
            button.clicked.connect(self.button_clicked)
            self.buttons.append(button)

        # Create a dictionary to hold different sets of widgets
        self.widget_sets = {
            0: [
                QLabel("previous document", self), QLineEdit(self), QPushButton("Details", self),
                QLabel("additional information", self), QLineEdit(self), QPushButton("Details", self),
                QLabel("supporting document", self), QLineEdit(self), QPushButton("Details", self),
                QLabel("additional reference", self), QLineEdit(self), QPushButton("Details", self),
                QLabel("transport document", self), QLineEdit(self), QPushButton("Details", self),
            ]
        }

        self.all_line_edits = []
        self.all_select_buttons = []
        # Set geometry for widgets and connect buttons to dialog
        lable_width = [200]
        button_width = 70
        QPushButton_index = 0
        for i, widgets in self.widget_sets.items():
            for j in range(0, len(widgets), 3):
                label, line_edit, button = widgets[j], widgets[j + 1], widgets[j + 2]
                label.setGeometry(50, 100 + j // 3 * (input_height + 10), lable_width[i], input_height)

                # if self.le_read_only[QPushButton_index]:
                #     line_edit.setReadOnly(True)

                line_edit.setGeometry(50 + lable_width[i], 100 + j // 3 * (input_height + 10), input_width,
                                      input_height)
                self.all_line_edits.append(line_edit)
                button.setGeometry(270 + lable_width[i], 100 + j // 3 * (input_height + 10), button_width, input_height)
                # Set button color to light blue
                # self.button_color_enabled = "background-color: #3393FF; border: none; color: #fff; border-radius: 8px;"
                self.button_color_disabled = "background-color: #222; border: none; color: #fff; border-radius: 8px;"
                button.setStyleSheet(self.nav_button_sheetstyle)
                if self.le_read_only[QPushButton_index]:
                    button.clicked.connect(
                        lambda checked, le=line_edit, index=QPushButton_index: self.show_multiple_input_dialog(le,
                                                                                                               index))
                else:
                    button.clicked.connect(
                        lambda checked, le=line_edit, index=QPushButton_index: self.show_selection_dialog(le, index))
                self.all_select_buttons.append(button)
                label.hide()
                line_edit.hide()
                button.hide()
                QPushButton_index += 1

        i = 0
        # for value in self.temp_input_information.values():
        for value in self.input_information.values():
            if isinstance(value, str):
                self.all_line_edits[i].setText(value)
            else:
                if len(value) == 0:
                    self.all_line_edits[i].setText('')
                else:
                    result = ";".join(
                        ",".join(str(value) for value in dictionary.values())
                        for dictionary in value
                    )
                    self.all_line_edits[i].setText(result)
            i += 1
        # for i in range(len(self.text_all_line_edits)):
        #     all_line_edits[i].setText(self.text_all_line_edits[i])

        i = 0
        for key, value in self.goodshipment_information.items():
            if value:
                self.prohibit_detail(i)
            i += 1

        # Show the initial set for "pole 1"
        self.update_input_fields(index)
        self.buttons[index].setStyleSheet(self.nav_button_sheetstyle_active)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        dialog_buttons.setGeometry(300, 350, 200, 30)

        # 连接按钮的信号到槽函数
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)

    def prohibit_detail(self, index):
        self.all_select_buttons[index].setEnabled(False)
        self.all_select_buttons[index].setStyleSheet(self.button_color_disabled)

    def restore_detail(self, index):
        self.all_select_buttons[index].setEnabled(True)
        self.all_select_buttons[index].setStyleSheet(self.nav_button_sheetstyle)

    def button_clicked(self):
        sender = self.sender()
        button_index = self.buttons.index(sender)
        for button in self.buttons:
            button.setStyleSheet(self.nav_button_sheetstyle)
        self.buttons[button_index].setStyleSheet(self.nav_button_sheetstyle_active)
        self.update_input_fields(button_index)

    def update_input_fields(self, index):
        # Hide all widgets
        for widgets in self.widget_sets.values():
            for j in range(0, len(widgets), 3):
                label, line_edit, button = widgets[j], widgets[j + 1], widgets[j + 2]
                label.hide()
                line_edit.hide()
                button.hide()

        # Show the widgets corresponding to the selected button
        for j in range(0, len(self.widget_sets[index]), 3):
            label, line_edit, button = self.widget_sets[index][j], self.widget_sets[index][j + 1], \
                self.widget_sets[index][j + 2]
            label.show()
            line_edit.show()
            button.show()

    def show_multiple_input_dialog(self, line_edit, index):
        # print(self.keys_input_information[index])
        # print(index)
        dialog = GoodsitemManualInputMultipleElements(self.keys_input_information[index], index,
                                                      self.input_information[self.keys_input_information[index]],
                                                      self.username)
        if dialog.exec_() == QDialog.Accepted:
            input_data, update_cache_dict = dialog.get_table_data()
            self.update_cache_dict.update(update_cache_dict)
            if len(input_data) > 0:
                result = ";".join(
                    ",".join(str(value) for value in dictionary.values())
                    for dictionary in input_data
                )
                line_edit.setText(result)
            else:
                line_edit.setText('')
            self.input_information[self.keys_input_information[index]] = input_data

    def get_input_information(self):
        for i in range(len(self.keys_input_information)):
            if not self.le_read_only[i]:
                self.input_information[self.keys_input_information[i]] = self.all_line_edits[i].text()

        # for key in self.input_information:
        #     new_value = self.input_information[key]
        #     old_value = self.temp_input_information[key]
        #
        #     # 如果新旧字典的值不相同，则添加到 diff_dict
        #     if not isinstance(new_value, list):
        #         if new_value != old_value:
        #             cache_id = self.keys_input_information.index(key) * 10
        #             self.update_cache_dict[cache_id] = new_value
        # print(self.update_cache_dict)
        self.update_cache()

        return self.input_information

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
            # print("update")

            # 这里可以选择保存更新后的 cache_data_list 到数据库
            # db.update_input_cache_data(key, cache_data_list)  # 示例保存函数


def main():
    app = QApplication(sys.argv)  # 创建应用程序对象
    index = 0  # 示例索引
    # goodshipment_information = {'goodshipment previous document': [
    #     {'reference number': '12345', 'type(CL214)': 'N271', 'goodsItem identifier': '643'}],
    #                             'goodshipment additional information': [],
    #                             'goodshipment supporting document': [
    #                                 {'reference number': '98765', 'type(CL213)': 'N380'}],
    #                             'goodshipment additional reference': [],
    #                             'goodshipment transport document': [
    #                                 {'reference number': '111-12345678', 'type(CL754)': 'N741'}]}
    goodshipment_information = {'goodshipment previous document': [
        {'reference number': '1', 'type(CL214)': 'N337', 'goodsItem identifier': '2'}
    ],
                                'goodshipment additional information': [],
                                'goodshipment supporting document': [
                                    {'reference number': '1', 'type(CL213)': 'N380'}
                                ],
                                'goodshipment additional reference': [],
                                'goodshipment transport document': [
                                    {'reference number': '1', 'type(CL754)': 'N740'}, {'reference number': '2', 'type(CL754)': 'N703'}]}
    # goodsitem_information = {'goodsitem previous document': [],
    #                          'goodsitem additional information': [{'code(CL239)': '00700', 'text': '123123'}],
    #                          'goodsitem supporting document': [],
    #                          'goodsitem additional reference': [{'reference number': '123123', 'type(CL380)': 'Y006'}],
    #                          'goodsitem transport document': []}  # 示例输入信息字典
    goodsitem_information = {'goodsitem previous document': [],
                             'goodsitem additional information': [{'code(CL239)': '00700', 'text': '123123'}],
                             'goodsitem supporting document': [],
                             'goodsitem additional reference': [{'reference number': '123123', 'type(CL380)': 'Y006'}],
                             'goodsitem transport document': []}  # 示例输入信息字典
    dialog = GoodsitemManualInformation(index, goodsitem_information, goodshipment_information)  # 创建对话框实例
    dialog.exec_()  # 显示对话框并进入事件循环


if __name__ == "__main__":
    main()  # 运行主函数
