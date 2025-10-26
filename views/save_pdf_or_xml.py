import json
import os
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt

from utils import pdf, db

from communication import http_client


class SavePDFOrXML(QDialog):
    def __init__(self, username, selected_option, selected_ids, token=None):
        super(SavePDFOrXML, self).__init__()

        self.username = username
        self.token = token
        self.selected_option = selected_option
        self.selected_ids = selected_ids

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
            'XML-UPD-signed': 'signed_upd',
            'UPD': 'upd',
            'UPD-signed': 'signed_upd',
            'PDF-UPD-signed': 'upd',
            'PDF-UPD': 'upd'
        }

        self.setWindowTitle(f"Save {selected_option}")

        # 路径选择部分
        self.path_label = QLabel("Save Path:")
        self.path_label.setFixedWidth(100)
        self.path_label.setAlignment(Qt.AlignRight)

        self.path_display = QTextEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setFixedHeight(30)

        self.select_path_button = QPushButton("Select the save path")
        self.select_path_button.clicked.connect(self.select_path)

        # 保存和取消按钮
        self.save_button = QPushButton("save")
        # self.save_button.setStyleSheet("color: #fff;")
        self.cancel_button = QPushButton("cancel")
        self.cancel_button.clicked.connect(self.reject)

        # 按钮使用系统默认样式
        self.save_button.setDefault(True)

        # 布局
        layout = QVBoxLayout()

        # 路径选择部分
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.select_path_button)
        layout.addLayout(path_layout)

        path_display_layout = QHBoxLayout()
        path_display_layout.addWidget(self.path_label)
        path_display_layout.addWidget(self.path_display)
        layout.addLayout(path_display_layout)

        # 按钮部分
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 将保存按钮的点击事件连接到 save_data 方法
        self.save_button.clicked.connect(self.save_data)

    def select_path(self):
        # 选择文件夹保存路径
        path = QFileDialog.getExistingDirectory(self, "Select the save path", "")
        if path:
            self.path_display.setPlainText(path)

    def save_data(self):
        save_path = self.path_display.toPlainText().strip()

        if not save_path:
            QMessageBox.warning(self, "Error", "Please select a save path.")
            return

        if self.selected_option == 'PDF':
            self.handle_pdf_by_sub_id(self.selected_ids, save_path)
            QMessageBox.information(self, "Success", 'PDF saved successfully!')
            self.accept()  # 关闭对话框
        elif self.selected_option in ['PDF-UPD', 'PDF-UPD-signed', 'PDF-zc429', "PDF-zcx03", "PDF-zcx64", "PDF-zcx65",
                                      "PDF-zc410", "PDF-zc460"]:
            self.handle_pdf_upd(self.selected_ids, save_path, self.selected_option)
            QMessageBox.information(self, "Success", 'PDF saved successfully!')
            self.accept()  # 关闭对话框
        elif self.selected_option in ['PDF-zc428', 'PDF-zcx16']:
            if self.token:
                self.handle_pdf_cr(self.selected_ids, save_path, self.selected_option)
                QMessageBox.information(self, "Success", 'XML saved successfully!')
                self.accept()  # 关闭对话框
        elif self.selected_option == 'XML':
            if self.token:
                data = {
                    'username': self.username,
                    'sub_id_list': self.selected_ids,
                    'type': 'zc415'
                }
                xml = http_client.get_xml(self.token, data)
                self.handle_xml(self.selected_ids, save_path, xml)
                QMessageBox.information(self, "Success", 'XML saved successfully!')
                self.accept()  # 关闭对话框
        elif self.selected_option in ['XML-UPD', 'XML-UPD-signed', 'XML-zc429', "XML-zcx03", "XML-zcx64", "XML-zcx65",
                                      "XML-zc410", "XML-zc460"]:
            if self.token:
                xml_type = self.option_to_xml_type[self.selected_option]
                data = {
                    'username': self.username,
                    'main_id_list': self.selected_ids,
                    'type': xml_type
                }
                xml = http_client.get_xml(self.token, data)
                self.handle_xml_udp(save_path, xml, self.selected_option)
                QMessageBox.information(self, "Success", 'XML saved successfully!')
                self.accept()  # 关闭对话框
        elif self.selected_option in ['XML-zc428', 'XML-zcx16']:
            if self.token:
                xml_type = self.option_to_xml_type[self.selected_option]
                data = {
                    'username': self.username,
                    'main_id_list': self.selected_ids,
                    'type': xml_type
                }
                xml = http_client.get_xml(self.token, data)
                self.handle_xml_cr(save_path, xml, self.selected_option)
                QMessageBox.information(self, "Success", 'XML saved successfully!')
                self.accept()  # 关闭对话框
        # elif self.selected_option in ['UPD', 'UPD-signed', 'zc429', 'zcx03', 'zcx64', 'zcx65', 'zc410', 'zc460']:
        #     main_id_list = self.selected_ids['main_id_list']
        #     local_id_list = self.selected_ids['local_id_list']
        #     data_type = 'PDF-' + self.selected_option
        #     self.handle_pdf_upd(local_id_list, save_path, data_type)
        #     if self.token:
        #         data_type = self.selected_option
        #         if self.selected_option in ['UPD', 'UPD-signed']:
        #             data_type = self.option_to_xml_type[self.selected_option]
        #         data = {
        #             'username': self.username,
        #             'main_id_list': main_id_list,
        #             'type': data_type
        #         }
        #         data_type = 'XML-' + self.selected_option
        #         xml = http_client.get_xml(self.token, data)
        #         if xml:
        #             self.handle_xml_udp(save_path, xml, data_type)
        #         else:
        #             QMessageBox.warning(self, "Error", 'XML data saved error, please try again.')
        #             return
        #
        #         main_ids = {
        #             'main_table_ids': [],
        #             'xml_table_ids': main_id_list
        #         }
        #         data = {
        #             'username': self.username,
        #             'main_ids': main_ids
        #         }
        #         response_status_code = http_client.delete_corresponding_data_by_main_ids(self.token, data)
        #
        #         if response_status_code == 200:
        #             if db.delete_data_from_related_tables(main_ids):
        #                 QMessageBox.information(self, "Success", 'Data clear successfully!')
        #                 self.accept()  # 关闭对话框
        #             else:
        #                 QMessageBox.warning(self, "Error", 'Data clear failed, please try again.')
        #                 return

    def handle_pdf_by_sub_id(self, sub_id_list, save_path):
        try:
            for sub_id in sub_id_list:

                # 获取 AirWayBill、IOSS 和 TrackingNumber
                airwaybill, ioss, trackingnumber, main_id = db.get_airwaybill_ioss_trackingnumber(sub_id)

                self.create_nested_folders(save_path, airwaybill, ioss, trackingnumber, 'pdf')

                # 创建嵌套文件夹结构
                airwaybill = f"pdf-{airwaybill}"

                # 获取与 sub_id 相关的数据
                datas = db.get_sub_xml_data_by_sub_table_id(sub_id, self.username)

                for data in datas:
                    # data[4] 中存储 XML 数据，解析为字典
                    xml_data = json.loads(data[4])
                    sub_id = data[2]
                    type_value = data[3]
                    direction = data[6]
                    username = data[8]
                    message_id = data[10]
                    representative_contact_person = json.loads(
                        db.get_signature_info_by_message_id_direction_and_username(
                            message_id,
                            direction,
                            username,
                            sub_id,
                            type_value
                        )
                    )

                    if direction == 'send':
                        flag = 0
                    else:
                        flag = 1
                        if type_value == 'upd':
                            flag = 2

                    # 定义 PDF 文件保存路径
                    file_name = f"{data[3]}_{data[6]}_{data[5]}.pdf"
                    file_name = file_name.replace(":", "-")
                    pdf_file_path = self.generate_file_path(save_path, [airwaybill, ioss, trackingnumber], file_name)

                    # 确保目录存在
                    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

                    # 保存 PDF
                    pdf.save_pdf(xml_data, pdf_file_path, representative_contact_person, flag=flag)
                    print(f"PDF 已保存到: {pdf_file_path}")
        except Exception as e:
            print(f"处理 PDF 数据时发生错误: {e}")

    def handle_pdf_cr(self, main_id_list, save_path, dir_name):
        try:
            new_path = self.create_folder(save_path, dir_name)
            for main_id in main_id_list:
                air_way_bill = db.get_cr_air_way_bill(self.username, main_id)
                self.create_folder(new_path, air_way_bill)

                xml_type = self.option_to_xml_type[dir_name]
                datas = db.get_cr_xml_json_data(self.username, main_id, xml_type)
                for data in datas:
                    xml_json_data = json.loads(data.get('xml_json_data'))
                    event_time = data.get('event_time')
                    message_id = data.get('messageID')
                    sub_id = data.get('sub_id')
                    direction = data.get('direction')
                    username = data.get('username')

                    # 定义 PDF 文件保存路径
                    file_name = f"{xml_type}-{message_id}-{event_time}.pdf"
                    file_name = file_name.replace(":", "-")
                    pdf_file_path = self.generate_file_path(new_path, [air_way_bill], file_name)

                    # 确保目录存在
                    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

                    signature_information = json.loads(
                        db.get_signature_info_by_message_id_direction_and_username(
                            message_id,
                            direction,
                            username,
                            sub_id,
                            xml_type
                        )
                    )

                    if direction == 'send':
                        flag = 0
                    else:
                        flag = 1
                        if xml_type == 'upd':
                            flag = 2

                    # 保存 PDF
                    pdf.save_pdf(xml_json_data, pdf_file_path, signature_information, flag=flag)
                    print(f"PDF 已保存到: {pdf_file_path}")
        except Exception as e:
            print(f"处理 PDF 数据时发生错误: {e}")

    def handle_pdf_upd(self, id_list, save_path, dir_name):
        try:
            # 创建目标文件夹
            self.create_folder(save_path, dir_name)
            datas = db.get_upd_by_id(self.username, id_list)
            xml_type = self.option_to_xml_type[dir_name]

            for data in datas:
                # 提取字典中的属性
                main_id = data.get("main_id")
                xml_data = json.loads(data.get("xml_data"))
                event_time = data.get("event_time")
                message_id = data.get("messageID")
                sub_id = data.get("sub_id")
                direction = data.get("direction")
                username = data.get("username")

                # 检查必须的字段是否存在
                if not main_id or not xml_data or not event_time or not message_id:
                    print(f"数据缺失，跳过: {data}")
                    continue

                # 生成文件名：main_id_event_time.xml
                # 替换 event_time 中不合法的文件名字符（如冒号）
                # sanitized_event_time = event_time.replace(":", "_").replace(" ", "_")
                file_name = f"{message_id}-{event_time}.pdf"
                file_name = file_name.replace(":", "-")
                pdf_file_path = self.generate_file_path(save_path, [dir_name], file_name)
                # 确保目录存在
                os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

                signature_information = json.loads(
                    db.get_signature_info_by_message_id_direction_and_username(
                        message_id,
                        direction,
                        username,
                        sub_id,
                        xml_type
                    )
                )

                if direction == 'send':
                    flag = 0
                else:
                    flag = 1
                    if xml_type == 'upd':
                        flag = 2

                # 保存 PDF
                pdf.save_pdf(xml_data, pdf_file_path, signature_information, flag=flag)
                print(f"PDF 已保存到: {pdf_file_path}")
        except Exception as e:
            print(f"处理 PDF 数据时发生错误: {e}")

    def handle_xml(self, sub_id_list, save_path, xml_data_list):
        try:
            for sub_id in sub_id_list:
                # 获取 AirWayBill、IOSS 和 TrackingNumber
                airwaybill, ioss, trackingnumber, _ = db.get_airwaybill_ioss_trackingnumber(sub_id)

                # 创建必要的文件夹
                self.create_nested_folders(save_path, airwaybill, ioss, trackingnumber, 'xml')

                # 获取与当前 sub_id 对应的所有 xml_data 项
                sub_id_datas = [item for item in xml_data_list if item['sub_id'] == sub_id]
                airwaybill = f"xml-{airwaybill}"
                for data in sub_id_datas:
                    # 获取文件名称，以 type_direction_event_time 格式命名
                    file_name = f"{data['type']}-{data['direction']}-{data['event_time']}.xml"

                    # 替换文件名中的冒号为破折号
                    file_name = file_name.replace(":", "-")
                    xml_file_path = self.generate_file_path(save_path, [airwaybill, ioss, trackingnumber], file_name)

                    # 确保目录存在
                    os.makedirs(os.path.dirname(xml_file_path), exist_ok=True)

                    # 检查 xml_data 是否为字符串类型
                    if isinstance(data['xml_data'], str):
                        # 将 XML 数据保存到文件
                        with open(xml_file_path, 'w', encoding='utf-8') as file:
                            file.write(data['xml_data'])  # 将 xml_data 字符串写入文件
                        print(f"XML data saved to {xml_file_path}")
                    else:
                        print(f"Error: xml_data for sub_id {sub_id} is not a valid string.")
        except Exception as e:
            print(f"处理 XML 数据时发生错误: {e}")

    def handle_xml_cr(self, save_path, xml_data_list, dir_name):
        try:
            # 创建目标文件夹
            new_path = self.create_folder(save_path, dir_name)

            for data in xml_data_list:
                # 提取字典中的属性
                main_id = data.get("main_id")
                xml_data = data.get("xml_data")
                event_time = data.get("event_time")
                xml_type = data.get("type")
                message_id = data.get("messageID")

                air_way_bill = db.get_cr_air_way_bill(self.username, main_id)
                self.create_folder(new_path, air_way_bill)

                # 检查必须的字段是否存在
                if not main_id or not xml_data or not event_time:
                    print(f"数据缺失，跳过: {data}")
                    continue

                # 生成文件名：main_id_event_time.xml
                # 替换 event_time 中不合法的文件名字符（如冒号）
                # sanitized_event_time = event_time.replace(":", "_").replace(" ", "_")
                file_name = f"{xml_type}-{message_id}-{event_time}.xml"
                file_name = file_name.replace(":", "-")
                xml_file_path = self.generate_file_path(new_path, [air_way_bill], file_name)

                # 保存 xml_data 为 XML 文件
                with open(xml_file_path, "w", encoding="utf-8") as f:
                    f.write(xml_data)

                print(f"已保存文件: {xml_file_path}")

        except Exception as e:
            print(f"处理 XML 数据时发生错误: {e}")

    def handle_xml_udp(self, save_path, xml_data_list, dir_name):
        """
        处理 xml_data_list，将其中的 xml_data 保存为 XML 文件，文件名格式为 main_id_event_time.xml。

        参数:
            save_path (str): 根文件夹路径。
            xml_data_list (list): 包含字典的列表，每个字典包含 main_id、xml_data、type、event_time、direction 属性。
            dir_name (str): 在 save_path 下创建的文件夹名称。
        """
        try:
            # 创建目标文件夹
            self.create_folder(save_path, dir_name)

            for data in xml_data_list:
                # 提取字典中的属性
                main_id = data.get("main_id")
                xml_data = data.get("xml_data")
                event_time = data.get("event_time")
                message_id = data.get("messageID")

                # 检查必须的字段是否存在
                if not main_id or not xml_data or not event_time:
                    print(f"数据缺失，跳过: {data}")
                    continue

                # 生成文件名：main_id_event_time.xml
                # 替换 event_time 中不合法的文件名字符（如冒号）
                # sanitized_event_time = event_time.replace(":", "_").replace(" ", "_")
                file_name = f"{message_id}-{event_time}.xml"
                file_name = file_name.replace(":", "-")
                xml_file_path = self.generate_file_path(save_path, [dir_name], file_name)

                # 保存 xml_data 为 XML 文件
                with open(xml_file_path, "w", encoding="utf-8") as f:
                    f.write(xml_data)

                print(f"已保存文件: {xml_file_path}")

        except Exception as e:
            print(f"处理 XML 数据时发生错误: {e}")

    def create_folder(self, base_path, file_name):
        """
        在指定的 base_path 下创建一个名为 file_name 的文件夹。

        参数:
            base_path (str): 根文件夹路径。
            file_name (str): 要创建的文件夹名称。
        """
        try:
            # 构造文件夹路径
            folder_path = os.path.join(base_path, file_name)

            # 创建文件夹（如果不存在）
            os.makedirs(folder_path, exist_ok=True)
            print(f"已创建文件夹: {folder_path}")
            return folder_path

        except Exception as e:
            print(f"创建文件夹时发生错误: {e}")

    def create_nested_folders(self, base_path, air_way_bill, ioss, tracking_number, folder_type):
        """
        根据 AirWayBill、IOSS、TrackingNumber 创建嵌套文件夹，并在 AirWayBill 文件夹名前添加类型前缀。
        参数:
            base_path (str): 根文件夹路径。
            air_way_bill (str): AirWayBill 文件夹名称。
            ioss (str): IOSS 文件夹名称。
            tracking_number (str): TrackingNumber 文件夹名称。
            folder_type (str): 文件类型 ("pdf" 或 "xml")，用于在 AirWayBill 文件夹前添加前缀。
        """
        try:
            # 根据 folder_type 确定前缀
            if folder_type.lower() == "pdf":
                air_way_bill = f"pdf-{air_way_bill}"
            elif folder_type.lower() == "xml":
                air_way_bill = f"xml-{air_way_bill}"
            else:
                raise ValueError("folder_type 必须是 'pdf' 或 'xml'")

            # 构造文件夹路径
            air_way_bill_path = os.path.join(base_path, air_way_bill)
            ioss_path = os.path.join(air_way_bill_path, ioss)
            tracking_number_path = os.path.join(ioss_path, tracking_number)

            # 创建文件夹（如果不存在）
            os.makedirs(tracking_number_path, exist_ok=True)
            print(f"已创建文件夹: {tracking_number_path}")

        except Exception as e:
            print(f"创建文件夹时发生错误: {e}")

    def generate_file_path(self, base_dir, sub_dirs, filename):
        # 替换文件名中的冒号 ':' 为 '-'
        filename = filename.replace(":", "-")

        # 拼接路径，确保跨平台兼容
        sub_path = os.path.join(*sub_dirs)  # 使用 os.path.join 来确保分隔符正确

        # 最终的完整文件路径
        full_path = os.path.join(base_dir, sub_path, filename)

        return full_path
