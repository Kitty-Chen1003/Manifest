import sys
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QLabel, QFileDialog, QDialogButtonBox, QFormLayout, \
    QLineEdit, QWidget, QVBoxLayout, QScrollArea
from PyQt5.QtCore import Qt
from views.input_sad_information import InputSADInformationDialog

temp_input_information = {
    'customs office referenceNumber': '',
    'LRN': '',
    'additional declaration type': '',
    'declarant name': '',
    'declarant identification number': '',
    'declarant street and number': '',
    'declarant postcode': '',
    'declarant city': '',
    'declarant country': '',
    'contact person': [],
    'representative identification number': '',
    'representative status': '',
    'representative contact person': [],
    'customs office reference number': '',
    'type of location': '',
    'qualifier of identification': '',
    'unLocode': '',
    'authorisation number': '',
    'additional identifier': '',
    'latitude': '',
    'longitude': '',
    'EORI Number': '',
    'address street and number': '',
    'address postcode': '',
    'address city': '',
    'address country': '',
    'postcode address postcode': '',
    'postcode address house number': '',
    'postcode address country': '',
    'goodshipment referenceNumberUCR': '',
    'goodshipment previous document': [],
    'goodshipment additional information': [],
    'goodshipment supporting document': [],
    'goodshipment additional reference': [],
    'goodshipment transport document': [],
    'goodshipment additional fiscal reference': [],
    'goodshipment transport costs to destination currency': '',
    'goodshipment transport costs to destination amount': '',
    'goodsitem additional procedure': [],
    'goodsitem previous document': [],
    'goodsitem additional information': [],
    'goodsitem supporting document': [],
    'goodsitem additional reference': [],
    'goodsitem transport document': []
}

keys_input_information = [
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

# text_all_line_edits = ["", "A", "PL443020", "", "PL521398303500000", "", "", "", "",
#                        [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
#                          'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}], "", "3",
#                        [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
#                          'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
#                        "", "B", "Y",
#                        "", "PLTST441000200001", "", "", "", "", "", "", "", "",
#                        "", "", "", "",
#                        [{'reference number': '12345', 'type(CL214)': 'N271', 'goodsItem identifier': '643'}], [],
#                        [{'reference number': '98765', 'type(CL213)': 'N380'}], [],
#                        [{'reference number': '111-12345678', 'type(CL754)': 'N741'}],
#                        [{'role': 'FR5'}], "", "",
#                        [{'additional procedure(CL457)': 'C07'}, {'additional procedure(CL457)': 'F48'}], [], [], [], [],
#                        []]

text_all_line_edits = ["PL443020", "523026291", "A", "", "PL521398303500000", "", "", "", "",
                       [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
                         'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}], "", "3",
                       [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
                         'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
                       "", "B", "Y",
                       "", "PLTST441000200001", "", "", "", "", "", "", "", "",
                       "", "", "", "",
                       [{'reference number': '1', 'type(CL214)': 'N337', 'goodsItem identifier': '2'}], [],
                       [{'reference number': '1', 'type(CL213)': 'N380'}], [],
                       [{'reference number': '1', 'type(CL754)': 'N740'}, {'reference number': '2', 'type(CL754)': 'N703'}],
                       [{'role(CL149)': 'FR5'}], "", "",
                       [{'additional procedure(CL457)': 'C07'}, {'additional procedure(CL457)': 'F48'}], [], [], [], [],
                       []]

# text_all_line_edits = ["PL443020", "523026291", "A", "", "PL521398303500000", "", "", "", "",
#                        [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
#                          'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}], "", "3",
#                        [{'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094',
#                          'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
#                        "", "B", "Y",
#                        "", "PLTST441000200001", "", "", "", "", "", "", "", "",
#                        "", "", "", "",
#                        [{'reference number': '12345', 'type(CL214)': 'N271', 'goodsItem identifier': '643'}], [],
#                        [{'reference number': '98765', 'type(CL213)': 'N380'}], [],
#                        [{'reference number': '111-12345678', 'type(CL754)': 'N741'}],
#                        [{'role(CL149)': 'FR5'}], "", "",
#                        [{'additional procedure(CL457)': 'C07'}, {'additional procedure(CL457)': 'F48'}], [], [], [], [],
#                        []]


class CreateSADs(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.selected_files = []  # 初始化 selected_files 为空列表
        self.input_information = temp_input_information
        # self.temp_input_information = temp_input_information

        self.input_information = dict(zip(keys_input_information, text_all_line_edits))
        # self.temp_input_information = dict(zip(keys_input_information, temp_text_all_line_edits))

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Resizable Scrollable Dialog')
        self.resize(1000, 800)
        # 设置对话框的初始大小
        self.setMinimumSize(300, 300)  # 设置最小大小，防止过小
        self.setMaximumSize(1000, 800)

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

        # 将所有控件添加到 main_widget 上
        self.btn_select_folder = QPushButton('Select Excel Files', self.main_widget)
        self.btn_select_folder.setGeometry(50, 50, 200, 40)
        self.btn_select_folder.clicked.connect(self.select_files)

        # 创建 QLabel 并放入 QScrollArea 中
        self.label_status = QLabel('No file selected', self.main_widget)
        self.label_status.setWordWrap(True)
        self.scroll_area_label = QScrollArea(self.main_widget)
        self.scroll_area_label.setWidgetResizable(True)
        self.scroll_area_label.setGeometry(50, 100, 300, 100)
        self.scroll_area_label.setWidget(self.label_status)

        self.btn_enter_info = QPushButton('Edit Info', self.main_widget)
        self.btn_enter_info.setGeometry(50, 210, 200, 40)
        self.btn_enter_info.setEnabled(False)
        self.btn_enter_info.clicked.connect(self.enter_info)

        # 显示信息的 QLabel 和 QScrollArea
        temp_input_information = self.output_of_input_information()
        text = "\n".join([f"{key}: {value}" for key, value in temp_input_information.items()])

        self.info_label = QLabel(text, self.main_widget)
        self.info_label.setStyleSheet("border: 1px solid #222; border-radius: 10px; padding-left: 10px;")
        self.info_label.setWordWrap(False)
        self.info_label.setFixedHeight(750)
        self.info_label.setGeometry(460, 25, 400, 750)

        self.scroll_area_info = QScrollArea(self.main_widget)
        self.scroll_area_info.setGeometry(460, 25, 400, 750)
        self.scroll_area_info.setWidget(self.info_label)
        self.scroll_area_info.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area_info.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area_info.setWidgetResizable(True)

        # 表单布局部分
        self.container_widget = QWidget(self.main_widget)
        self.container_widget.setGeometry(50, 240, 300, 450)

        # Create a form layout
        form_layout = QFormLayout(self.container_widget)
        # self.list_key = ['InvoiceNumber', 'GoodsItemNumber', 'HSCode', 'Total Price', 'GrossMassKg',
        #                  'AmountPackages', 'TrackingNumber', 'ConsignorName', 'InvoiceCurrency', 'DescriptionGoods',
        #                  'ConsignorStreetAndNr', 'ConsignorCity', 'ConsignorPostcode', 'ConsignorCountry',
        #                  'ConsigneeName', 'ConsigneeStreetAndNr', 'ConsigneePostcode', 'ConsigneeCity',
        #                  'ConsigneeCountryCode', 'AirWayBill', 'IOSS', 'CountryOriginCode',
        #                  'ConsigneeNameID']
        self.list_key = ['InvoiceNumber', 'GoodsItemNumber', 'HSCode', 'Total Price', 'GrossMassKg',
                         'AmountPackages', 'TrackingNumber', 'ConsignorName', 'InvoiceCurrency', 'DescriptionGoods',
                         'ConsignorStreetAndNr', 'ConsignorCity', 'ConsignorPostcode', 'ConsignorCountry',
                         'ConsigneeName', 'ConsigneeStreetAndNr', 'ConsigneePostcode', 'ConsigneeCity',
                         'ConsigneeCountryCode', 'AirWayBill', 'IOSS', 'CountryOriginCode',
                         'ConsigneeNameID', 'Box Number', 'Dsk']
        self.list_label = []
        self.list_editor = []

        for k in self.list_key:
            label = QLabel(k + ": ")
            editor = QLineEdit()
            editor.setMaximumWidth(200)
            form_layout.addRow(label, editor)
            self.list_label.append(label)
            self.list_editor.append(editor)

        self.container_widget.setLayout(form_layout)

        # Create a scroll area
        self.scroll_area_form = QScrollArea(self.main_widget)
        self.scroll_area_form.setGeometry(50, 260, 400, 450)
        self.scroll_area_form.setWidgetResizable(True)
        self.scroll_area_form.setWidget(self.container_widget)

        # 确认和取消按钮
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self.main_widget)
        self.buttons.setGeometry(50, 730, 300, 40)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)

    # def select_folder(self):
    #     folder_dialog = QFileDialog(self)
    #     folder_dialog.setWindowTitle('Select Folder')
    #     folder_dialog.setFileMode(QFileDialog.Directory)
    #     if folder_dialog.exec_():
    #         self.selected_folder = folder_dialog.selectedFiles()[0]
    #         self.label_status.setText(f'Selected folder: {self.selected_folder}')
    #         self.btn_enter_info.setEnabled(True)  # Enable after folder is selected

    def select_files(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle('Select Excel Files')
        file_dialog.setFileMode(QFileDialog.ExistingFiles)  # 允许选择多个文件
        file_dialog.setNameFilter("Excel Files (*.xls *.xlsx)")  # 仅显示Excel文件
        file_dialog.setViewMode(QFileDialog.List)  # 以列表模式显示文件

        if file_dialog.exec_():
            # 更新 self.selected_files 列表为用户选择的文件路径
            self.selected_files = file_dialog.selectedFiles()
            self.label_status.setText("\n".join(self.selected_files))  # 每个文件路径换行显示
            self.btn_enter_info.setEnabled(True)  # 选择文件后启用按钮

    def enter_info(self):
        info_dialog = InputSADInformationDialog(0, self.input_information, self.username, self)
        # info_dialog = InputSADInformationDialog(0, self.input_information, self.temp_input_information, self)
        if info_dialog.exec_() == QDialog.Accepted:
            print("success!")
            # self.input_information, self.temp_input_information = info_dialog.get_input_information()
            self.input_information = info_dialog.get_input_information()
            print(self.input_information)
            self.update_info_label()

    def update_info_label(self):
        if self.input_information:
            temp_input_information = self.output_of_input_information()
            text = "\n".join([f"{key}: {value}" for key, value in temp_input_information.items()])
            self.info_label.setText(text)
            self.buttons.button(QDialogButtonBox.Ok).setEnabled(True)
            # self.buttons.button(QDialogButtonBox.Ok).setStyleSheet("color: #fff;")

    def output_of_input_information(self):
        my_dict = self.input_information.copy()
        for key, value in my_dict.items():
            if isinstance(value, list):  # 检查值是否是列表
                if len(value) > 0:  # 如果列表中有元素
                    result = ";".join(
                        ",".join(str(value) for value in dictionary.values())
                        for dictionary in value
                    )
                    my_dict[key] = result
                else:  # 如果列表为空
                    my_dict[key] = ''
        return my_dict

    def get_selected_files(self):
        # 返回所选文件路径的列表
        return self.selected_files

    def get_data_keys(self):
        data_keys = []
        for label, editor in zip(self.list_key, self.list_editor):
            if editor.text() == '':
                data_keys.append(label)
            else:
                data_keys.append(editor.text())
        return data_keys

    def get_input_information(self):
        return self.input_information


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CreateSADs()
    window.show()
    sys.exit(app.exec_())
