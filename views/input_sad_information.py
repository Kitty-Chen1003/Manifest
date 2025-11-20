import json
import re

from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QDialog, QDialogButtonBox, QVBoxLayout, QMessageBox, \
    QScrollArea, QWidget

from utils.path import get_resource_path
from views.selection_dialog import SelectionDialog
from views.input_multiple_elements import InputMultipleElements

from utils import db


class InputSADInformationDialog(QDialog):
    # def __init__(self, index, input_information, temp_input_information, parent=None):
    def __init__(self, index, input_information, username, parent=None):
        super().__init__(parent)
        self.username = username

        self.setWindowTitle("Input SAD Information Dialog")
        self.resize(1000, 800)
        self.setMaximumSize(1000, 800)
        self.setMinimumSize(300, 300)

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

        self.keys_input_information = [
            'customs office referenceNumber',
            'LRN',
            'additional declaration type',
            'declarant name',
            'declarant identification number',
            'declarant street and number',
            'declarant postcode',
            'declarant city',
            'declarant country',
            'contact person',
            'representative identification number',
            'representative status',
            'representative contact person',
            'customs office reference number',
            'type of location',
            'qualifier of identification',
            'unLocode',
            'authorisation number',
            'additional identifier',
            'latitude',
            'longitude',
            'EORI Number',
            'address street and number',
            'address postcode',
            'address city',
            'address country',
            'postcode address postcode',
            'postcode address house number',
            'postcode address country',
            'goodshipment referenceNumberUCR',
            'goodshipment previous document',
            'goodshipment additional information',
            'goodshipment supporting document',
            'goodshipment additional reference',
            'goodshipment transport document',
            'goodshipment additional fiscal reference',
            'goodshipment transport costs to destination currency',
            'goodshipment transport costs to destination amount',
            'goodsitem additional procedure',
            'goodsitem previous document',
            'goodsitem additional information',
            'goodsitem supporting document',
            'goodsitem additional reference',
            'goodsitem transport document'
        ]

        self.keys_input_information_print = [
            'customs office referenceNumber(CL141)',
            'LRN',
            'additional declaration type(CL042)',
            'declarant name(company)',
            'declarant identification number(EORI)',
            'declarant street and number',
            'declarant postcode',
            'declarant city',
            'declarant country(CL199)',
            'contact person',
            'representative identification number',
            'representative status(CL094)',
            'representative contact person',
            'customs office reference number(CL141)',
            'type of location(CL347)',
            'qualifier of identification(CL326)',
            'unLocode(CL244)',
            'authorisation number',
            'additional identifier',
            'latitude',
            'longitude',
            'EORI Number',
            'address street and number',
            'address postcode',
            'address city',
            'address country(CL199)',
            'postcode address postcode',
            'postcode address house number',
            'postcode address country(CL190)',
            'goodshipment referenceNumberUCR',
            'goodshipment previous document',
            'goodshipment additional information',
            'goodshipment supporting document',
            'goodshipment additional reference',
            'goodshipment transport document',
            'goodshipment additional fiscal reference',
            'goodshipment transport costs to destination currency(CL352)',
            'goodshipment transport costs to destination amount',
            'goodsitem additional procedure',
            'goodsitem previous document',
            'goodsitem additional information',
            'goodsitem supporting document',
            'goodsitem additional reference',
            'goodsitem transport document'
        ]

        self.is_must_fill = [1, 1, 1,   # 0-2
                             1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 3-12
                             1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,    # 13-28
                             0, 0, 0, 0, 0, 1, 1, 0, 0,     # 29-37
                             1, 0, 0, 0, 0, 0]      # 38-43

        self.update_cache_dict = {}

        self.input_information = input_information.copy()
        self.temp_input_information = input_information.copy()
        # self.temp_input_information = temp_input_information

        num_key = 44
        self.files_name = [''] * num_key
        self.files_name[0] = "CL141AIS"
        self.files_name[2] = "CL042AIS"
        self.files_name[8] = "CL199AIS"
        self.files_name[11] = "CL094AIS"
        self.files_name[13] = "CL141AIS"
        self.files_name[14] = "CL347AIS"
        self.files_name[15] = "CL326AIS"
        self.files_name[16] = "CL244AIS"
        self.files_name[25] = "CL199AIS"
        self.files_name[28] = "CL190AIS"
        self.files_name[36] = "CL352AIS"

        self.le_read_only = [0] * num_key
        self.le_read_only[9] = 1
        self.le_read_only[12] = 1
        for i in range(30, 36):
            self.le_read_only[i] = 1
        for i in range(38, 44):
            self.le_read_only[i] = 1

        # 创建QScrollArea，用来显示超出部分
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)  # 内容会根据对话框大小调整

        # 创建一个QWidget来承载大的控件（模拟500x500的控件）
        content_widget = QWidget(scroll_area)
        content_layout = QVBoxLayout(content_widget)

        # 新增容器控件，与 QDialog 大小一致
        self.main_widget = QWidget(content_widget)
        self.main_widget.setFixedSize(900, 800)  # 设置大小与 QDialog 一致

        content_layout.addWidget(self.main_widget)

        # 设置内容到滚动区域
        scroll_area.setWidget(content_widget)

        # 创建对话框的主布局
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)

        # Layout for the dialog
        main_layout = QVBoxLayout(self.main_widget)
        self.setLayout(main_layout)

        # # Create menu bar
        # menu_bar = QMenuBar(self)
        # main_layout.setMenuBar(menu_bar)
        #
        # # Add menus
        # file_menu = menu_bar.addMenu("文件")
        # edit_menu = menu_bar.addMenu("编辑")
        # view_menu = menu_bar.addMenu("视图")
        # help_menu = menu_bar.addMenu("帮助")
        #
        # # Add actions to menus
        # file_menu.addAction(QAction("新建", self))
        # file_menu.addAction(QAction("打开", self))
        # file_menu.addAction(QAction("保存", self))
        # file_menu.addAction(QAction("退出", self, triggered=self.close))
        #
        # edit_menu.addAction(QAction("撤销", self))
        # edit_menu.addAction(QAction("重做", self))
        #
        # view_menu.addAction(QAction("放大", self))
        # view_menu.addAction(QAction("缩小", self))
        #
        # help_menu.addAction(QAction("关于", self))

        # Absolute positioning
        button_widths = [115, 80, 120, 110, 80]
        button_height = 30
        input_width = 200
        input_height = 30

        x_position = 50  # 初始的X位置

        button_names = ["CustomsOffice", "Declarant", "LocationOfGoods", "GoodsShipment", "GoodsItem"]

        # Create buttons with absolute positioning
        self.buttons = []
        for i, name in enumerate(button_names):
            button = QPushButton(name, self.main_widget)
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
                QLabel("customs office referenceNumber(CL141)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget)
            ],
            1: [
                QLabel("LRN(first 9 digits only)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("additional declaration type(CL042)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant name(company)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant identification number(EORI)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant street and number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant postcode", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant city", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("declarant country(CL199)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("contact person", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("representative identification number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("representative status(CL094)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("representative contact person", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget)
            ],
            2: [
                QLabel("customs office reference number(CL141)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("type of location(CL347)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("qualifier of identification(CL326)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("unLocode(CL244)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("authorisation number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("additional identifier", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("latitude", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("longitude", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("EORI Number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("address street and number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("address postcode", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("address city", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("address country(CL199)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("postcode address postcode", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("postcode address house number", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("postcode address country(CL190)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget)
            ],
            3: [
                QLabel("referenceNumberUCR", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("previous document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("additional information", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("supporting document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("additional reference", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("transport document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("additional fiscal reference", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("transport costs to destination currency(CL352)", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget),
                QLabel("transport costs to destination amount", self.main_widget), QLineEdit(self.main_widget), QPushButton("Select", self.main_widget)
            ],
            4: [
                QLabel("additional procedure", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("previous document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("additional information", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("supporting document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("additional reference", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget),
                QLabel("transport document", self.main_widget), QLineEdit(self.main_widget), QPushButton("Details", self.main_widget)
            ]
        }

        self.all_line_edits = []
        self.all_select_buttons = []
        # Set geometry for widgets and connect buttons to dialog
        lable_width = [300, 300, 300, 300, 290]
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

        self.adding_constraints()

        i = 0
        # for value in self.temp_input_information.values():
        # print(self.input_information)
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

        # Show the initial set for "pole 1"
        self.update_input_fields(index)
        self.buttons[index].setStyleSheet(self.nav_button_sheetstyle_active)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self.main_widget)
        dialog_buttons.setGeometry(50, 750, 200, 30)

        # 连接按钮的信号到槽函数
        dialog_buttons.accepted.connect(self.on_accepted)
        dialog_buttons.rejected.connect(self.reject)

    def adding_constraints(self):
        self.all_line_edits[11].textChanged.connect(self.representative_status_changed)
        self.all_line_edits[14].textChanged.connect(self.type_of_location_changed)
        self.all_line_edits[15].textChanged.connect(self.qualifier_of_identification_changed)

        self.prohibit_select(29)

        for i in range(30, 35):
            self.all_line_edits[i].textChanged.connect(
                lambda text, idx=i: self.goodshipment_document_changed(text, idx))
        for i in range(39, 44):
            self.all_line_edits[i].textChanged.connect(
                lambda text, idx=i: self.goodsitem_document_changed(text, idx))

        # self.all_line_edits[22].textChanged.connect(self.additional_identifier_changed)
        for i in range(3, 14):
            self.prohibit_select(i)
        self.restore_select(11)
        for i in range(16, 29):
            self.prohibit_select(i)

    def representative_status_changed(self):
        if self.all_line_edits[11].text() == '2':
            self.restore_select(10)
            # for i in range(12, 13):
            self.restore_select(12)
        elif self.all_line_edits[11].text() == '3':
            for i in range(3, 13):
                self.restore_select(i)
            self.prohibit_select(3)
            for i in range(5, 9):
                self.prohibit_select(i)
            self.prohibit_select(10)
        elif self.all_line_edits[11].text() == '1':
            for i in range(3, 13):
                self.restore_select(i)
        else:
            for i in range(3, 13):
                self.prohibit_select(i)
            self.restore_select(11)
            for i in range(3, 13):
                self.all_line_edits[i].setText('')
            self.input_information['contact person'] = []
            self.input_information['representative contact person'] = []
        # self.all_line_edits[9].setReadOnly(True)
        # self.all_line_edits[12].setReadOnly(True)

    def type_of_location_changed(self):
        # print(self.all_line_edits[14].text())
        if self.all_line_edits[14].text() == 'B' or self.all_line_edits[14].text() == 'C':
            self.all_line_edits[15].setText('Y')
            self.prohibit_select(15)
            self.restore_select(17)
        else:
            self.restore_select(15)
            if self.all_line_edits[15].text() == 'Y':
                self.restore_select(17)
            if self.all_line_edits[14].text() != 'A' and self.all_line_edits[14].text() != 'D':
                self.all_line_edits[14].setText('')
        self.all_line_edits[13].setText('')
        for i in range(16, 29):
            self.all_line_edits[i].setText('')

    def qualifier_of_identification_changed(self):
        self.all_line_edits[13].setText('')
        self.prohibit_select(13)
        for i in range(16, 29):
            self.all_line_edits[i].setText('')
            self.prohibit_select(i)
        if self.all_line_edits[15].text() == 'T':
            for i in range(26, 29):
                self.restore_select(i)
        elif self.all_line_edits[15].text() == 'U':
            self.restore_select(16)
        elif self.all_line_edits[15].text() == 'V':
            self.restore_select(13)
        elif self.all_line_edits[15].text() == 'W':
            self.restore_select(19)
            self.restore_select(20)
        elif self.all_line_edits[15].text() == 'X':
            self.restore_select(21)
        elif self.all_line_edits[15].text() == 'Y':
            self.restore_select(17)
        elif self.all_line_edits[15].text() == 'Z':
            for i in range(22, 26):
                self.restore_select(i)
        else:
            self.prohibit_select(13)
            for i in range(16, 29):
                self.prohibit_select(i)

    def goodshipment_document_changed(self, text, index):
        if text != '':
            self.prohibit_detail(index + 9)
        else:
            self.restore_detail(index + 9)

    def goodsitem_document_changed(self, text, index):
        if text != '':
            self.prohibit_detail(index - 9)
        else:
            self.restore_detail(index - 9)

    def prohibit_select(self, index):
        self.all_line_edits[index].setReadOnly(True)
        self.all_select_buttons[index].setEnabled(False)
        self.all_select_buttons[index].setStyleSheet(self.button_color_disabled)

    def restore_select(self, index):
        self.all_line_edits[index].setReadOnly(False)
        self.all_select_buttons[index].setEnabled(True)
        # self.all_select_buttons[index].setStyleSheet(self.button_color_enabled)
        self.all_select_buttons[index].setStyleSheet(self.nav_button_sheetstyle)

    def prohibit_detail(self, index):
        self.all_select_buttons[index].setEnabled(False)
        self.all_select_buttons[index].setStyleSheet(self.button_color_disabled)

    def restore_detail(self, index):
        self.all_select_buttons[index].setEnabled(True)
        # self.all_select_buttons[index].setStyleSheet(self.button_color_enabled)
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

    def show_selection_dialog(self, line_edit, index):
        # print(index)
        if self.files_name[index] != "":
            json_file_path = "config/customs_dictionary/" + self.files_name[index] + ".json"
            json_file_path = get_resource_path(json_file_path)
            title = self.files_name[index] + " code"
        else:
            json_file_path = ""  # 请替换为实际的Excel文件路径
            title = "cache"
        height = 1275
        width = 820
        input_id = index * 10
        dialog = SelectionDialog(input_id, json_file_path, title, height, width, self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            row_data, columns = dialog.getSelectedRowData()
            if row_data:
                line_edit.setText(row_data[0])
                self.input_information[self.keys_input_information[index]] = row_data[0]

                # self.temp_input_information[self.keys_input_information[index]] = input_data

    def show_multiple_input_dialog(self, line_edit, index):
        dialog = InputMultipleElements(self.keys_input_information[index], index,
                                       self.input_information[self.keys_input_information[index]], self.username)
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

        for key in self.input_information:
            new_value = self.input_information[key]
            old_value = self.temp_input_information[key]

            # 如果新旧字典的值不相同，则添加到 diff_dict
            if not isinstance(new_value, list):
                if new_value != old_value:
                    cache_id = self.keys_input_information.index(key) * 10
                    self.update_cache_dict[cache_id] = new_value
        # print(self.update_cache_dict)
        self.update_cache()

        # print(self.update_cache_dict)
        return self.input_information

    # 假设这是你的类的一部分
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

    def validate_input(self):
        """ Validate the inputs of the active fields """
        # 遍历所有按钮和输入框
        for key, button, line_edit, must_fill in zip(self.keys_input_information_print, self.all_select_buttons,
                                                     self.all_line_edits, self.is_must_fill):
            # 如果按钮启用且输入框是启用状态
            if button.isEnabled():
                input_text = line_edit.text().strip()  # 获取输入框的内容并去除前后空格

                # 如果是必须填写的字段且为空或者为"Not entered"
                if must_fill == 1 and (input_text == "Not entered" or not input_text):
                    QMessageBox.warning(self, "Input Error", f"Please fill {key}.")
                    return False  # 返回 False 表示输入不符合要求

                if key == 'LRN':
                    if not len(input_text) == 9 and input_text.isdigit():
                        QMessageBox.warning(self, "Input Error", f"LRN must be first 9 digits only.")
                        return False  # 返回 False 表示输入不符合要求

        # 检查这两个字段是否成对输入
        key_currency = "goodshipment transport costs to destination currency(CL352)"
        key_amount = "goodshipment transport costs to destination amount"

        index_currency = None
        index_amount = None

        # 找到这两个字段在 keys_input_information_print 中的索引
        for idx, key in enumerate(self.keys_input_information_print):
            if key == key_currency:
                index_currency = idx
            elif key == key_amount:
                index_amount = idx

        # 如果这两个字段都存在
        if index_currency is not None and index_amount is not None:
            line_edit_currency = self.all_line_edits[index_currency]
            line_edit_amount = self.all_line_edits[index_amount]

            input_currency = line_edit_currency.text().strip()
            input_amount = line_edit_amount.text().strip()

            # 检查是否同时填写或者同时为空
            if (input_currency and not input_amount) or (not input_currency and input_amount):
                QMessageBox.warning(self, "Input Error",
                                    "Please fill in both goodshipment transport costs to destination currency(CL352) and goodshipment transport costs to destination amount or leave them blank.")
                return False  # 返回 False 表示输入不符合要求

        if not len(self.all_line_edits[0].text()) == 8 and self.all_select_buttons[0].isEnabled() and self.is_must_fill[0]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[0]} must be 8 digits.")
            return False
        elif not len(self.all_line_edits[1].text()) == 9 and self.all_select_buttons[1].isEnabled() and self.is_must_fill[1]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[1]} must be 9 digits.")
            return False
        elif not len(self.all_line_edits[2].text()) == 1 and self.all_select_buttons[2].isEnabled() and self.is_must_fill[2]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[2]} must be 1 digit.")
            return False
        elif not len(self.all_line_edits[3].text()) <= 70 and self.all_select_buttons[3].isEnabled() and self.is_must_fill[3]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[3]} must be no more than 70 digits.")
            return False
        elif not len(self.all_line_edits[4].text()) <= 17 and self.all_select_buttons[4].isEnabled() and self.is_must_fill[4]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[4]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[5].text()) <= 70 and self.all_select_buttons[5].isEnabled() and self.is_must_fill[5]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[5]} must be no more than 70 digits.")
            return False
        elif not len(self.all_line_edits[6].text()) <= 17 and self.all_select_buttons[6].isEnabled() and self.is_must_fill[6]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[6]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[7].text()) <= 35 and self.all_select_buttons[7].isEnabled() and self.is_must_fill[7]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[7]} must be no more than 35 digits.")
            return False
        elif not len(self.all_line_edits[8].text()) == 2 and self.all_select_buttons[8].isEnabled() and self.is_must_fill[8]:
            print(self.is_must_fill[8])
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[8]} must be 2 digits.")
            return False
        elif not len(self.all_line_edits[10].text()) <= 17 and self.all_select_buttons[10].isEnabled() and self.is_must_fill[10]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[10]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[11].text()) == 1 and self.all_select_buttons[11].isEnabled() and self.is_must_fill[11]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[11]} must be 1 digit.")
            return False
        elif not len(self.all_line_edits[13].text()) == 8 and self.all_select_buttons[13].isEnabled() and self.is_must_fill[13]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[13]} must be 8 digits.")
            return False
        elif not len(self.all_line_edits[14].text()) == 1 and self.all_select_buttons[14].isEnabled() and self.is_must_fill[14]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[14]} must be 1 digit.")
            return False
        elif not len(self.all_line_edits[15].text()) == 1 and self.all_select_buttons[15].isEnabled() and self.is_must_fill[15]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[15]} must be 1 digit.")
            return False
        elif not len(self.all_line_edits[16].text()) <= 17 and self.all_select_buttons[16].isEnabled() and self.is_must_fill[16]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[16]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[17].text()) <= 35 and self.all_select_buttons[17].isEnabled() and self.is_must_fill[17]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[17]} must be no more than 35 digits.")
            return False
        elif not len(self.all_line_edits[18].text()) <= 4 and self.all_select_buttons[18].isEnabled() and self.is_must_fill[18]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[18]} must be no more than 4 digits.")
            return False
        elif not len(self.all_line_edits[19].text()) <= 17 and self.all_select_buttons[19].isEnabled() and self.is_must_fill[19]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[19]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[20].text()) <= 17 and self.all_select_buttons[20].isEnabled() and self.is_must_fill[20]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[20]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[21].text()) <= 17 and self.all_select_buttons[21].isEnabled() and self.is_must_fill[21]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[21]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[22].text()) <= 70 and self.all_select_buttons[22].isEnabled() and self.is_must_fill[22]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[22]} must be no more than 70 digits.")
            return False
        elif not len(self.all_line_edits[23].text()) <= 17 and self.all_select_buttons[23].isEnabled() and self.is_must_fill[23]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[23]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[24].text()) <= 35 and self.all_select_buttons[24].isEnabled() and self.is_must_fill[24]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[24]} must be no more than 35 digits.")
            return False
        elif not len(self.all_line_edits[25].text()) == 2 and self.all_select_buttons[25].isEnabled() and self.is_must_fill[25]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[25]} must be 2 digits.")
            return False
        elif not len(self.all_line_edits[26].text()) <= 17 and self.all_select_buttons[26].isEnabled() and self.is_must_fill[26]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[26]} must be no more than 17 digits.")
            return False
        elif not len(self.all_line_edits[27].text()) <= 35 and self.all_select_buttons[27].isEnabled() and self.is_must_fill[27]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[27]} must be no more than 35 digits.")
            return False
        elif not len(self.all_line_edits[28].text()) == 2 and self.all_select_buttons[28].isEnabled() and self.is_must_fill[28]:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[28]} must be 2 digits.")
            return False
        elif not len(self.all_line_edits[29].text()) <= 35 and self.all_select_buttons[29].isEnabled():
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[29]} must be no more than 35 digits.")
            return False
        elif len(self.all_line_edits[36].text()) > 0 and not len(self.all_line_edits[36].text()) == 3:
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[36]} must be 3 digits.")
            return False
        elif len(self.all_line_edits[37].text()) > 0 and not self.is_valid_number(self.all_line_edits[37].text()):
            QMessageBox.warning(self, "Input Error", f"{self.keys_input_information_print[37]}: The decimal part of the number can be up to 2 digits, and the total of the integer and decimal part can be up to 16 digits.")
            return False

        return True  # 如果所有必填项都满足条件，返回 True

    def is_valid_number(self, input_str):
        # 正则表达式匹配规则：
        # ^ : 开始
        # \d{1,14} : 整数部分1到14位数字
        # (\.\d{1,2})? : 小数部分，最多2位数字，? 表示小数部分是可选的
        # $ : 结束
        print(input_str)
        pattern = r'^\d{1,16}(\.\d{1,2})?$'
        print(re.match(pattern, input_str))
        # 使用正则表达式进行匹配
        if re.match(pattern, input_str):
            print("in")
            # 进一步检查整数和小数部分的总长度是否小于等于16
            total_length = len(input_str.replace('.', ''))  # 去掉小数点，计算总长度
            print(total_length)
            if total_length <= 16:
                return True
        print("False")
        return False

    def on_accepted(self):
        """ Called when the accepted signal is triggered """
        if self.validate_input():  # 判断输入是否正确
            self.accept()  # 如果输入正确，接受当前操作
        else:
            # 如果输入不正确，可以在这里做其他处理，比如不关闭对话框
            pass
