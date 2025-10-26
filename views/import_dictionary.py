import csv
import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QFileDialog, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
import xml.etree.ElementTree as ET
import pandas as pd

from utils.path import get_resource_path


class DictionarySelectorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Dictionary")
        self.resize(400, 200)

        # Create main layout
        main_layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Create combo box (dropdown menu)
        self.combo_box = QComboBox(self)
        self.combo_box.addItems([
            "CL034AIS", "CL042AIS", "CL094AIS", "CL141AIS", "CL149AIS",
            "CL190AIS", "CL199AIS", "CL213AIS", "CL214AIS", "CL239AIS",
            "CL244AIS", "CL326AIS", "CL347AIS", "CL352AIS", "CL380AIS",
            "CL457AIS", "CL754AIS", "611"
        ])
        form_layout.addWidget(QLabel("Select Dictionary:"))
        form_layout.addWidget(self.combo_box)

        # File selection button and text box
        self.file_path_edit = QTextEdit(self)
        self.file_path_edit.setFixedHeight(40)
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Enable scrolling for the text box
        self.file_path_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.file_path_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)

        # File selection layout
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.file_path_edit)

        # Create OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_dialog)
        self.ok_button.setDefault(True)  # Set OK button as default for Enter key
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # Add to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(file_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Initialize selected file path
        self.selected_file_path = None

    def select_file(self):
        # Open file selection dialog with XML file filter
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Dictionary File", "", "XML Files (*.xml)"
        )
        if file_path:
            # Store and display the selected file path
            self.selected_file_path = file_path
            self.file_path_edit.setText(file_path)

    def accept_dialog(self):
        # Check if a file has been selected
        if not self.selected_file_path:
            QMessageBox.warning(self, "Warning", "Please select a file before clicking OK.")
            return

        # Get the selected file path
        selected_file_path = self.selected_file_path
        selected_dict_name = self.combo_box.currentText()
        # 调用 xml_to_json 方法
        try:
            self.xml_to_json(selected_file_path, selected_dict_name)
            QMessageBox.information(self, "Success", f"Data has been saved successfully.")
            self.accept()  # Close the dialog
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save data to JSON: {str(e)}")
            return

    def xml_to_json(self, file_path, dict_name):
        # 使用选项框中的字典名称作为文件名，例如 'CL042AIS'
        file_prefix = dict_name  # 从外部传入的字典名

        # 解析 XML 文件
        tree = ET.parse(file_path)
        root = tree.getroot()

        if dict_name == '611':  # 新增对 '611' 字典的处理
            namespace = {'ns': 'http://www.mf.gov.pl/schematy/PDR/refdata/611.xsd'}
            node = 'ns:C611'

            # 提取 goodsNomenId 的前 6 位
            goods_nomen_ids = []
            for c611 in root.findall(node, namespace):
                goodsNomenId = c611.attrib.get('goodsNomenId', '')
                if goodsNomenId:
                    goods_nomen_ids.append(goodsNomenId[:6])  # 取前 6 位

            # 将提取的 goodsNomenIds 保存到 CSV 文件，逗号分隔
            output_csv_path = f'config/hs_negative.csv'
            output_csv_path = get_resource_path(output_csv_path)
            with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_NONE)  # 不使用引号
                writer.writerow(goods_nomen_ids)  # 直接写入所有 ID，不加双引号

            print("GoodsNomenIds saved to hs_negative.csv")
            return  # 处理完 '611' 后直接返回

        # 定义命名空间
        namespace = {'ns': f'http://www.mf.gov.pl/schematy/PDR/refdata/{file_prefix}.xsd'}
        # 提取数据
        data = []
        node = f'ns:SCL{file_prefix[2:5]}AIS'  # 构造节点名称，例如 'SCL042AIS'
        if dict_name == 'CL034AIS':
            namespace = {'ns': 'http://www.mf.gov.pl/schematy/PDR/refdata/034.xsd'}
            node = 'ns:S034'
        elif dict_name == 'CL141AIS' or dict_name == 'CL244AIS':
            node = f'ns:CCL{file_prefix[2:5]}AIS'
        for scl in root.findall(node, namespace):
            if dict_name == 'CL141AIS':
                referenceNumber = scl.get('referenceNumber')
                id = scl.get('id')
                countryCode = scl.get('countryCode')
                unLocodeId = scl.get('unLocodeId')
                postalCode = scl.get('postalCode')
                phoneNumber = scl.get('phoneNumber')

                # 获取第一个 Cusofflsd 的 cusOffUsuName
                first_cusofflsd = scl.find('ns:Cusofflsd', namespace)
                cusOffUsuName = first_cusofflsd.get('cusOffUsuName') if first_cusofflsd is not None else None

                # 将提取到的数据存入字典
                data.append({
                    'referenceNumber': referenceNumber,
                    'id': id,
                    'countryCode': countryCode,
                    'unLocodeId': unLocodeId,
                    'postalCode': postalCode,
                    'phoneNumber': phoneNumber,
                    'cusOffUsuName': cusOffUsuName
                })
            elif dict_name == 'CL244AIS':
                unLocodeExtendedCode = scl.get('unLocodeExtendedCode')
                id = scl.get('id')
                name = scl.get('name')
                function = scl.get('function')
                status = scl.get('status')
                date = scl.get('date')
                coordinates = scl.get('coordinates')
                comment = scl.get('comment')
                validFrom = scl.get('validFrom')

                # 将提取到的数据存入字典
                data.append({
                    'unLocodeExtendedCode': unLocodeExtendedCode,
                    'id': id,
                    'name': name,
                    'function': function,
                    'status': status,
                    'date': date,
                    'coordinates': coordinates,
                    'comment': comment,
                    'validFrom': validFrom
                })
            else:
                code = scl.get('code')
                description = scl.get('description')
                descriptionEng = scl.get('descriptionEng')
                data.append({'code': code, 'description': description, 'descriptionEng': descriptionEng})

        # 创建 DataFrame 并保存为 JSON 文件
        df = pd.DataFrame(data)
        output_json_path = f'config/customs_dictionary/{file_prefix}.json'
        output_json_path = get_resource_path(output_json_path)
        df.to_json(output_json_path, orient='records', lines=True)

        print(f"Data has been saved to {output_json_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DictionarySelectorDialog()
    if dialog.exec_() == QDialog.Accepted:
        print("Dialog accepted.")
    sys.exit(app.exec_())
