import os
import numpy as np

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
from utils.xml_generator import XMLGenerator  # 假设这是你自定义的 XML 生成器类
from datetime import datetime
from decimal import Decimal

import pytz


# label竖直显示
class SADInformation(QLabel):
    def __init__(self, input_information, data_rows):
        super().__init__()
        self.input_information = input_information
        self.data_rows = data_rows

        # print(self.input_information)
        # print(self.data_rows)

        self.sum_total_price = 0
        self.sum_GrossMassKg = 0
        # 保存不同的 declaration 名字所对应的row的序号
        self.declaration_dict = {}
        # 保存不同 declaration 的名字
        self.key_declaration_dict = []
        # 保存了 declaration 的一些基本信息，包括航班号
        self.information_declaration = []
        # 不同 declaration 下 goodsshipment 的 grossmasskg 总和
        self.declaration_goodsshipment_grossmasskg = []
        # declaration_exporter 的基本信息
        self.declaration_exporter = []
        # declaration_ioss_number
        self.declaration_ioss_number = []

        self.flag_importer = 0

        self.basic_information()
        self.ioss = self.data_rows[0]['IOSS']

        # print("############")
        # print(self.data_rows[0])
        # print(self.declaration_dict)
        # print(self.key_declaration_dict)
        # print(self.information_declaration)
        # print(self.declaration_goodsshipment_grossmasskg)
        # print(self.declaration_exporter)
        # print(self.declaration_ioss_number)

    def basic_information(self):
        i = 0
        for row in self.data_rows:
            self.sum_total_price += row['Total Price']
            self.sum_GrossMassKg += row['GrossMassKg']
            if row['ConsigneeName'] == '':
                self.flag_importer = 1
                consignee_name_id = row['ConsigneeNameID']
                if consignee_name_id not in self.declaration_dict:
                    self.declaration_dict[consignee_name_id] = []
                    self.key_declaration_dict.append(consignee_name_id)
                    self.information_declaration.append({
                        'ConsigneeNameID': row['ConsigneeNameID'],
                        'ConsigneeCountryCode': row['ConsigneeCountryCode']
                    })
                    self.declaration_goodsshipment_grossmasskg.append(Decimal(0.0))
                    self.declaration_exporter.append({
                        'ConsignorName': row['ConsignorName'],
                        'ConsignorStreetAndNr': row['ConsignorStreetAndNr'],
                        'ConsignorPostcode': row['ConsignorPostcode'],
                        'ConsignorCity': row['ConsignorCity'],
                        'ConsignorCountry': row['ConsignorCountry']
                    })
                    self.declaration_ioss_number.append({
                        'IOSS': row['IOSS']
                    })
                self.declaration_dict[consignee_name_id].append(i)
                self.declaration_goodsshipment_grossmasskg[
                    self.key_declaration_dict.index(consignee_name_id)] += Decimal(
                    str(row['GrossMassKg']))
            else:
                consignee_name = row['ConsigneeName'] + str(row['ConsigneePostcode'])
                if consignee_name not in self.declaration_dict:
                    self.declaration_dict[consignee_name] = []
                    self.key_declaration_dict.append(consignee_name)
                    self.information_declaration.append({
                        'ConsigneeName': row['ConsigneeName'],
                        'ConsigneeStreetAndNr': row['ConsigneeStreetAndNr'],
                        'ConsigneePostcode': row['ConsigneePostcode'],
                        'ConsigneeCity': row['ConsigneeCity'],
                        'ConsigneeCountryCode': row['ConsigneeCountryCode']
                        # 'AirWayBill': row['AirWayBill']
                    })
                    self.declaration_goodsshipment_grossmasskg.append(Decimal(0.0))
                    self.declaration_exporter.append({
                        'ConsignorName': row['ConsignorName'],
                        'ConsignorStreetAndNr': row['ConsignorStreetAndNr'],
                        'ConsignorPostcode': row['ConsignorPostcode'],
                        'ConsignorCity': row['ConsignorCity'],
                        'ConsignorCountry': row['ConsignorCountry']
                    })
                    self.declaration_ioss_number.append({
                        'IOSS': row['IOSS']
                    })
                self.declaration_dict[consignee_name].append(i)
                self.declaration_goodsshipment_grossmasskg[self.key_declaration_dict.index(consignee_name)] += Decimal(
                    str(row['GrossMassKg']))
            i += 1

    def update_input_information(self, new_input_information):
        self.input_information = new_input_information

    def check_keys_in_dict(self, dictionary, *keys):
        return all(key in dictionary for key in keys)

    def convert_excel_to_xml(self, file_path, target_dir):
        try:
            flag_exporter = 0
            flag_referencenumberucr = 0
            flag_previous_document = 0
            flag_additional_information = 0
            flag_supporting_document = 0
            flag_additional_reference = 0
            flag_transprot_document = 0

            # 创建 XMLGenerator 对象和 XML 结构
            # datetime.now().strftime("%Y-%m-%d")
            attr_root = {
                'xmlns:ns': 'http://www.w3.org/2000/09/xmldsig#',
                'xmlns:ns1': 'http://www.mf.gov.pl/xsd/ais/hub/ZC415HUB.xsd'
            }
            xml_gen = XMLGenerator(
                "ns1:ZC415HUB",
                attrib=attr_root
            )

            # 获取当前时间
            now = datetime.now()
            # 设置波兰时区
            poland_tz = pytz.timezone('Europe/Warsaw')
            # 将当前时间转换为波兰时间
            poland_time = now.astimezone(poland_tz)
            # 格式化为所需的字符串格式
            formatted_time = poland_time.strftime("%Y-%m-%dT%H:%M:%S")
            zc415hub_preparation = xml_gen.add_element(
                'preparationDateAndTime',
                text=formatted_time
            )

            # 固定的部分
            XXX = "02"  # 三字母标识，已经指定为 02
            OpcjonalnyIdentyfikatorPodmiotu = ""  # 如果需要，你可以填写可选的标识符
            # 设置波兰时区
            poland_tz = pytz.timezone('Europe/Warsaw')
            # 获取当前时间并转换为波兰时间
            current_date = datetime.now(poland_tz)
            # 提取年份、月份和日期
            RR = current_date.strftime("%y")  # 当前年份的最后两位
            MM = current_date.strftime("%m")  # 当前月份
            DD = current_date.strftime("%d")  # 当前日期
            # 消息的递增编号，从 000001 开始
            counter = 1
            # 格式化 NNNNNN 部分
            NNNNNN = f"{counter:06d}"
            # 生成完整的字符串
            messageIdentification = f"{XXX}{RR}{MM}{DD}{NNNNNN}{OpcjonalnyIdentyfikatorPodmiotu}"

            zc415hub_messageidentification = xml_gen.add_element(
                'messageIdentification',
                text=messageIdentification
            )

            sequence_number_declaration = 0
            for j in range(len(self.declaration_dict)):
                zc415hub_declaration = xml_gen.add_element(
                    'Declaration'
                )

                zc415hub_declaration_sequencenumber = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'sequenceNumber',
                    text=str(sequence_number_declaration + 1)
                )

                zc415hub_declaration_lrn = xml_gen.add_sub_element(
                    zc415hub_declaration, 'lrn',
                    text=self.input_information['LRN']
                )

                zc415hub_declaration_additionaldeclarationtype = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'additionalDeclarationType',
                    text=self.input_information['additional declaration type']
                )

                zc415hub_declaration_importer = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'Importer'
                )

                if self.flag_importer == 0:
                    zc415hub_declaration_importer_name = xml_gen.add_sub_element(
                        zc415hub_declaration_importer,
                        'name',
                        text=self.information_declaration[sequence_number_declaration]['ConsigneeName']
                    )

                    zc415hub_declaration_importer_address = xml_gen.add_sub_element(
                        zc415hub_declaration_importer,
                        'Address'
                    )

                    zc415hub_declaration_importer_address_streetandnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_importer_address,
                        'streetAndNumber',
                        text=self.information_declaration[sequence_number_declaration]['ConsigneeStreetAndNr']
                    )

                    zc415hub_declaration_importer_address_postcode = xml_gen.add_sub_element(
                        zc415hub_declaration_importer_address,
                        'postcode',
                        text=str(self.information_declaration[sequence_number_declaration]['ConsigneePostcode'])
                    )

                    zc415hub_declaration_importer_address_city = xml_gen.add_sub_element(
                        zc415hub_declaration_importer_address,
                        'city',
                        text=self.information_declaration[sequence_number_declaration]['ConsigneeCity']
                    )

                    zc415hub_declaration_importer_address_country = xml_gen.add_sub_element(
                        zc415hub_declaration_importer_address,
                        'country',
                        text=self.information_declaration[sequence_number_declaration]['ConsigneeCountryCode']
                    )
                else:
                    zc415hub_declaration_importer_identificationnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_importer,
                        'identificationNumber',
                        text=str(self.information_declaration[sequence_number_declaration]['ConsigneeNameID'])
                    )

                    zc415hub_declaration_importer_address = xml_gen.add_sub_element(
                        zc415hub_declaration_importer,
                        'Address'
                    )

                    zc415hub_declaration_importer_address_country = xml_gen.add_sub_element(
                        zc415hub_declaration_importer_address,
                        'country',
                        text=self.information_declaration[sequence_number_declaration]['ConsigneeCountryCode']
                    )

                if self.input_information['representative status'] != '2':
                    zc415hub_declaration_declarant = xml_gen.add_sub_element(
                        zc415hub_declaration,
                        'Declarant'
                    )

                    if self.input_information['representative status'] == '3':
                        zc415hub_declaration_declarant_identificationnumber = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant,
                            'identificationNumber',
                            text=self.input_information['declarant identification number']
                        )
                    else:
                        if self.input_information['declarant name'] != '':
                            zc415hub_declaration_declarant_name = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant,
                                'name',
                                text=self.input_information['declarant name']
                            )

                        if self.input_information['declarant identification number'] != '':
                            zc415hub_declaration_declarant_identificationnumber = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant,
                                'identificationNumber',
                                text=self.input_information['declarant identification number']
                            )

                        if self.input_information['declarant street and number'] != '' and self.input_information[
                            'declarant postcode'] != '' and self.input_information['declarant city'] != '' and \
                                self.input_information['declarant country'] != '':
                            zc415hub_declaration_declarant_address = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant,
                                'Address'
                            )

                            zc415hub_declaration_declarant_address_streetandnumber = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant_address,
                                'streetAndNumber',
                                text=self.input_information['declarant street and number']
                            )

                            zc415hub_declaration_declarant_address_postcode = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant_address,
                                'postcode',
                                text=self.input_information['declarant postcode']
                            )

                            zc415hub_declaration_declarant_address_city = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant_address,
                                'city',
                                text=self.input_information['declarant city']
                            )

                            zc415hub_declaration_declarant_address_country = xml_gen.add_sub_element(
                                zc415hub_declaration_declarant_address,
                                'country',
                                text=self.input_information['declarant country']
                            )

                    for k in range(len(self.input_information['contact person'])):
                        contact_person = self.input_information['contact person'][k]
                        zc415hub_declaration_declarant_contactperson = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant,
                            'ContactPerson'
                        )

                        zc415hub_declaration_declarant_contactperson_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant_contactperson,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_declarant_contactperson_name = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant_contactperson,
                            'name',
                            text=contact_person['name']
                        )

                        zc415hub_declaration_declarant_contactperson_phonenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant_contactperson,
                            'phoneNumber',
                            text=contact_person['phoneNumber']
                        )

                        zc415hub_declaration_declarant_contactperson_emailaddress = xml_gen.add_sub_element(
                            zc415hub_declaration_declarant_contactperson,
                            'eMailAddress',
                            text=contact_person['eMailAddress']
                        )

                zc415hub_declaration_representative = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'Representative'
                )

                zc415hub_declaration_representative_status = xml_gen.add_sub_element(
                    zc415hub_declaration_representative,
                    'status',
                    text=self.input_information['representative status']
                )

                if self.input_information['representative status'] == '2':
                    zc415hub_declaration_representative_identificationnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_representative,
                        'identificationNumber',
                        text=self.input_information['representative identification number']
                    )
                else:
                    if self.input_information['representative identification number'] != '':
                        zc415hub_declaration_representative_identificationnumber = xml_gen.add_sub_element(
                            zc415hub_declaration_representative,
                            'identificationNumber',
                            text=self.input_information['representative identification number']
                        )

                for k in range(len(self.input_information['representative contact person'])):
                    representative_contact_person = self.input_information['representative contact person'][k]
                    zc415hub_declaration_representative_contactperson = xml_gen.add_sub_element(
                        zc415hub_declaration_representative,
                        'ContactPerson'
                    )

                    zc415hub_declaration_representative_contactperson_sequencenumber = xml_gen.add_sub_element(
                        zc415hub_declaration_representative_contactperson,
                        'sequenceNumber',
                        text=str(k + 1)
                    )

                    zc415hub_declaration_representative_contactperson_name = xml_gen.add_sub_element(
                        zc415hub_declaration_representative_contactperson,
                        'name',
                        text=representative_contact_person['name']
                    )

                    zc415hub_declaration_representative_contactperson_phonenumber = xml_gen.add_sub_element(
                        zc415hub_declaration_representative_contactperson,
                        'phoneNumber',
                        text=representative_contact_person['phoneNumber']
                    )

                    zc415hub_declaration_representative_contactperson_emailaddress = xml_gen.add_sub_element(
                        zc415hub_declaration_representative_contactperson,
                        'eMailAddress',
                        text=representative_contact_person['eMailAddress']
                    )

                zc415hub_declaration_customsofficeofdeclaration = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'CustomsOfficeOfDeclaration'
                )

                zc415hub_declaration_customsofficeofdeclaration_referencenumber = xml_gen.add_sub_element(
                    zc415hub_declaration_customsofficeofdeclaration,
                    'referenceNumber',
                    text=self.input_information['customs office referenceNumber']
                )

                zc415hub_declaration_goodsshipment = xml_gen.add_sub_element(
                    zc415hub_declaration,
                    'GoodsShipment'
                )

                if self.input_information['goodshipment referenceNumberUCR'] != '':
                    flag_referencenumberucr = 1
                    zc415hub_declaration_goodsshipment_referencenumberucr = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment,
                        'referenceNumberUCR',
                        text=self.input_information['goodshipment referenceNumberUCR']
                    )

                # zc415hub_declaration_goodsshipment_grossmass = xml_gen.add_sub_element(
                #     zc415hub_declaration_goodsshipment,
                #     'grossMass',
                #     text=str(self.declaration_goodsshipment_grossmasskg[sequence_number_declaration])
                # )

                if self.input_information['goodshipment previous document']:
                    flag_previous_document = 1
                    for k in range(len(self.input_information['goodshipment previous document'])):
                        previous_document = self.input_information['goodshipment previous document'][k]
                        zc415hub_declaration_goodsshipment_previousdocument = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment,
                            'PreviousDocument'
                        )

                        zc415hub_declaration_goodsshipment_previousdocument_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_previousdocument,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_goodsshipment_previousdocument_referencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_previousdocument,
                            'referenceNumber',
                            text=previous_document['reference number']
                        )

                        zc415hub_declaration_goodsshipment_previousdocument_type = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_previousdocument,
                            'type',
                            text=previous_document['type(CL214)']
                        )

                        if previous_document['goodsItem identifier'] != '':
                            zc415hub_declaration_goodsshipment_previousdocument_goodsitemidentifier = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_previousdocument,
                                'goodsItemIdentifier',
                                text=previous_document['goodsItem identifier']
                            )

                if self.input_information['goodshipment additional information']:
                    flag_additional_information = 1
                    for k in range(len(self.input_information['goodshipment additional information'])):
                        additional_information = self.input_information['goodshipment additional information'][k]
                        zc415hub_declaration_goodsshipment_additionalinformation = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment,
                            'AdditionalInformation'
                        )

                        zc415hub_declaration_goodsshipment_additionalinformation_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_additionalinformation,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_goodsshipment_additionalinformation_code = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_additionalinformation,
                            'code',
                            text=additional_information['code(CL239)']
                        )

                        if additional_information['text'] != '':
                            zc415hub_declaration_goodsshipment_additionalinformation_text = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_additionalinformation,
                                'text',
                                text=additional_information['text']
                            )

                if self.input_information['goodshipment supporting document']:
                    flag_supporting_document = 1
                    for k in range(len(self.input_information['goodshipment supporting document'])):
                        supporting_document = self.input_information['goodshipment supporting document'][k]
                        zc415hub_declaration_goodsshipment_supportingdocument = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment,
                            'SupportingDocument'
                        )

                        zc415hub_declaration_goodsshipment_supportingdocument_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_supportingdocument,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_goodsshipment_supportingdocument_referencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_supportingdocument,
                            'referenceNumber',
                            text=supporting_document['reference number']
                        )

                        zc415hub_declaration_goodsshipment_supportingdocument_type = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_supportingdocument,
                            'type',
                            text=supporting_document['type(CL213)']
                        )

                if self.input_information['goodshipment additional reference']:
                    flag_additional_reference = 1
                    for k in range(len(self.input_information['goodshipment additional reference'])):
                        additional_reference = self.input_information['goodshipment additional reference'][k]
                        zc415hub_declaration_goodsshipment_additionalreference = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment,
                            'AdditionalReference'
                        )

                        zc415hub_declaration_goodsshipment_additionalreference_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_additionalreference,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_goodsshipment_additionalreference_referencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_additionalreference,
                            'referenceNumber',
                            text=additional_reference['reference number']
                        )

                        zc415hub_declaration_goodsshipment_additionalreference_type = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_additionalreference,
                            'type',
                            text=additional_reference['type(CL380)']
                        )

                if self.input_information['goodshipment transport document']:
                    flag_transprot_document = 1
                    for k in range(len(self.input_information['goodshipment transport document'])):
                        transprot_document = self.input_information['goodshipment transport document'][k]
                        zc415hub_declaration_goodsshipment_transportdocument = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment,
                            'TransportDocument'
                        )

                        zc415hub_declaration_goodsshipment_transportdocument_sequencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_transportdocument,
                            'sequenceNumber',
                            text=str(k + 1)
                        )

                        zc415hub_declaration_goodsshipment_transportdocument_referencenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_transportdocument,
                            'referenceNumber',
                            text=transprot_document['reference number']
                        )

                        zc415hub_declaration_goodsshipment_transportdocument_type = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_transportdocument,
                            'type',
                            text=transprot_document['type(CL754)']
                        )

                if self.declaration_exporter[sequence_number_declaration]['ConsignorName'] != '':
                    flag_exporter = 1
                    zc415hub_declaration_goodsshipment_exporter = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment,
                        'Exporter'
                    )

                    zc415hub_declaration_goodsshipment_exporter_name = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter,
                        'name',
                        text=self.declaration_exporter[sequence_number_declaration]['ConsignorName']
                    )

                    zc415hub_declaration_goodsshipment_exporter_address = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter,
                        'Address'
                    )

                    zc415hub_declaration_goodsshipment_exporter_address_streetandnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter_address,
                        'streetAndNumber',
                        text=self.declaration_exporter[sequence_number_declaration]['ConsignorStreetAndNr']
                    )

                    zc415hub_declaration_goodsshipment_exporter_address_postcode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter_address,
                        'postcode',
                        text=str(self.declaration_exporter[sequence_number_declaration]['ConsignorPostcode'])
                    )

                    zc415hub_declaration_goodsshipment_exporter_address_city = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter_address,
                        'city',
                        text=self.declaration_exporter[sequence_number_declaration]['ConsignorCity']
                    )

                    zc415hub_declaration_goodsshipment_exporter_address_country = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_exporter_address,
                        'country',
                        text=self.declaration_exporter[sequence_number_declaration]['ConsignorCountry']
                    )

                for k in range(len(self.input_information['goodshipment additional fiscal reference'])):
                    additional_fiscal_reference = self.input_information['goodshipment additional fiscal reference'][k]
                    zc415hub_declaration_goodsshipment_additionalfiscalreference = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment,
                        'AdditionalFiscalReference'
                    )

                    zc415hub_declaration_goodsshipment_additionalfiscalreference_sequencenumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_additionalfiscalreference,
                        'sequenceNumber',
                        text=str(k + 1)
                    )

                    zc415hub_declaration_goodsshipment_additionalfiscalreference_role = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_additionalfiscalreference,
                        'role',
                        text=additional_fiscal_reference['role']
                    )

                    zc415hub_declaration_goodsshipment_additionalfiscalreference_vatidentificationnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_additionalfiscalreference,
                        'vatIdentificationNumber',
                        text=str(self.ioss)
                    )

                if self.input_information['goodshipment transport costs to destination currency'] != '' and \
                        self.input_information['goodshipment transport costs to destination amount'] != '':
                    zc415hub_declaration_goodsshipment_transportcoststodestination = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment,
                        'TransportCostsToDestination'
                    )

                    zc415hub_declaration_goodsshipment_transportcoststodestination_currency = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_transportcoststodestination,
                        'currency',
                        text=self.input_information['goodshipment transport costs to destination currency']
                    )

                    zc415hub_declaration_goodsshipment_transportcoststodestination_amount = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_transportcoststodestination,
                        'amount',
                        text=self.input_information['goodshipment transport costs to destination amount']
                    )

                zc415hub_declaration_goodsshipment_locationofgoods = xml_gen.add_sub_element(
                    zc415hub_declaration_goodsshipment,
                    'LocationOfGoods'
                )

                zc415hub_declaration_goodsshipment_locationofgoods_typeoflocation = xml_gen.add_sub_element(
                    zc415hub_declaration_goodsshipment_locationofgoods,
                    'typeOfLocation',
                    text=self.input_information['type of location']
                )

                zc415hub_declaration_goodsshipment_locationofgoods_qualifierofidentification = xml_gen.add_sub_element(
                    zc415hub_declaration_goodsshipment_locationofgoods,
                    'qualifierOfIdentification',
                    text=self.input_information['qualifier of identification']
                )

                if self.input_information['qualifier of identification'] == 'U':
                    zc415hub_declaration_goodsshipment_locationofgoods_unlocode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'unLocode',
                        text=self.input_information['unLocode']
                    )

                if self.input_information['qualifier of identification'] == 'Y':
                    zc415hub_declaration_goodsshipment_locationofgoods_authorisationnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'authorisationNumber',
                        text=self.input_information['authorisation number']
                    )

                if self.input_information['additional identifier'] != '':
                    zc415hub_declaration_goodsshipment_locationofgoods_additionalidentifier = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'additionalIdentifier',
                        text=self.input_information['additional identifier']
                    )

                if self.input_information['qualifier of identification'] == 'V':
                    zc415hub_declaration_goodsshipment_locationofgoods_customsoffice = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'CustomsOffice'
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_customsoffice_referencenumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_customsoffice,
                        'referenceNumber',
                        text=self.input_information['customs office reference number']
                    )

                if self.input_information['qualifier of identification'] == 'W':
                    zc415hub_declaration_goodsshipment_locationofgoods_gnss = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'GNSS'
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_gnss_latitude = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_gnss,
                        'latitude',
                        text=self.input_information['latitude']
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_gnss_longitude = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_gnss,
                        'longitude',
                        text=self.input_information['longitude']
                    )

                if self.input_information['qualifier of identification'] == 'X':
                    zc415hub_declaration_goodsshipment_locationofgoods_economicoperator = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'EconomicOperator'
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_economicoperator_identificationnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_economicoperator,
                        'identificationNumber',
                        text=self.input_information['EORI Number']
                    )

                if self.input_information['qualifier of identification'] == 'Z':
                    zc415hub_declaration_goodsshipment_locationofgoods_address = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'Address'
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_address_streetandnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_address,
                        'streetAndNumber',
                        text=self.input_information['address street and number']
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_address_postcode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_address,
                        'postcode',
                        text=str(self.input_information['address postcode'])
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_address_city = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_address,
                        'city',
                        text=self.input_information['address city']
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_address_country = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_address,
                        'country',
                        text=self.input_information['address country']
                    )

                if self.input_information['qualifier of identification'] == 'T':
                    zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods,
                        'PostcodeAddress'
                    )

                    zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress_postcode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress,
                        'postcode',
                        text=str(self.input_information['postcode address postcode'])
                    )

                    if self.input_information['postcode address house number'] != '':
                        zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress_housenumber = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress,
                            'houseNumber',
                            text=self.input_information['postcode address house number']
                        )

                    zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress_country = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_locationofgoods_postcodeaddress,
                        'country',
                        text=self.input_information['postcode address country']
                    )

                for k in self.declaration_dict[self.key_declaration_dict[sequence_number_declaration]]:
                    row = self.data_rows[k]
                    zc415hub_declaration_goodsshipment_goodsitem = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment,
                        'GoodsItem'
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_goodsitemnumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'goodsItemNumber',
                        text=str(k + 1)
                    )

                    if flag_referencenumberucr != 1:
                        zc415hub_declaration_goodsshipment_goodsitem_greferencenumberucr = xml_gen.add_sub_element(
                            zc415hub_declaration_goodsshipment_goodsitem,
                            'referenceNumberUCR',
                            text=str(row['TrackingNumber'])
                        )

                    zc415hub_declaration_goodsshipment_goodsitem_grossmass = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'grossMass',
                        text=str(row['GrossMassKg'])
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_descriptionofgoods = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'descriptionOfGoods',
                        text=str(row['DescriptionGoods'])
                    )

                    if self.input_information['goodsitem additional procedure']:
                        for l in range(len(self.input_information['goodsitem additional procedure'])):
                            additional_procedure = self.input_information['goodsitem additional procedure'][l]
                            zc415hub_declaration_goodsshipment_goodsitem_additionalprocedure1 = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem,
                                'AdditionalProcedure'
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_additionalprocedure1_sequencenumber = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_additionalprocedure1,
                                'sequenceNumber',
                                text=str(l + 1)
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_additionalprocedure1_additionalprocedure = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_additionalprocedure1,
                                'additionalProcedure',
                                text=additional_procedure['additional procedure(CL457)']
                            )

                    if flag_previous_document != 1:
                        if self.input_information['goodsitem previous document']:
                            for l in range(len(self.input_information['goodsitem previous document'])):
                                previous_document = self.input_information['goodsitem previous document'][l]
                                zc415hub_declaration_goodsshipment_goodsitem_previousdocument = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem,
                                    'PreviousDocument'
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_previousdocument_sequencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_previousdocument,
                                    'sequenceNumber',
                                    text=str(l + 1)
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_previousdocument_referencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_previousdocument,
                                    'referenceNumber',
                                    text=previous_document['reference number']
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_previousdocument_type = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_previousdocument,
                                    'type',
                                    text=previous_document['type(CL214)']
                                )

                                if previous_document['goodsItem identifier'] != '':
                                    zc415hub_declaration_goodsshipment_goodsitem_previousdocument_goodsitemidentifier = xml_gen.add_sub_element(
                                        zc415hub_declaration_goodsshipment_goodsitem_previousdocument,
                                        'goodsItemIdentifier',
                                        text=previous_document['goodsItem identifier']
                                    )

                    if flag_additional_information != 1:
                        if self.input_information['goodsitem additional information']:
                            for l in range(len(self.input_information['goodsitem additional information'])):
                                additional_information = self.input_information['goodsitem additional information'][l]
                                zc415hub_declaration_goodsshipment_goodsitem_additionalinformation = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem,
                                    'AdditionalInformation'
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_additionalinformation_sequencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalinformation,
                                    'sequenceNumber',
                                    text=str(l + 1)
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_additionalinformation_code = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalinformation,
                                    'code',
                                    text=additional_information['code(CL239)']
                                )

                                if additional_information['text'] != '':
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalinformation_text = xml_gen.add_sub_element(
                                        zc415hub_declaration_goodsshipment_goodsitem_additionalinformation,
                                        'text',
                                        text=additional_information['text']
                                    )

                    if flag_supporting_document != 1:
                        if self.input_information['goodsitem supporting document']:
                            for l in range(len(self.input_information['goodsitem supporting document'])):
                                supporting_document = self.input_information['goodsitem supporting document'][l]
                                zc415hub_declaration_goodsshipment_goodsitem_supportingdocument = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem,
                                    'SupportingDocument'
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_supportingdocument_sequencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_supportingdocument,
                                    'sequenceNumber',
                                    text=str(l + 1)
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_supportingdocument_referencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_supportingdocument,
                                    'referenceNumber',
                                    text=supporting_document['reference number']
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_supportingdocument_type = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_supportingdocument,
                                    'type',
                                    text=supporting_document['type(CL213)']
                                )

                    if flag_additional_reference != 1:
                        if self.input_information['goodsitem additional reference']:
                            for l in range(len(self.input_information['goodsitem additional reference'])):
                                additional_reference = self.input_information['goodsitem additional reference'][l]
                                zc415hub_declaration_goodsshipment_goodsitem_additionalreference = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem,
                                    'AdditionalReference'
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_additionalreference_sequencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalreference,
                                    'sequenceNumber',
                                    text=str(l + 1)
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_additionalreference_referencenumber = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalreference,
                                    'referenceNumber',
                                    text=additional_reference['reference number']
                                )

                                zc415hub_declaration_goodsshipment_goodsitem_additionalreference_type = xml_gen.add_sub_element(
                                    zc415hub_declaration_goodsshipment_goodsitem_additionalreference,
                                    'type',
                                    text=additional_reference['type(CL380)']
                                )

                    if flag_transprot_document != 1:
                        for l in range(len(self.input_information['goodsitem transport document'])):
                            transprot_document = self.input_information['goodsitem transport document'][l]
                            zc415hub_declaration_goodsshipment_goodsitem_transportdocument = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem,
                                'TransportDocument'
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_transportdocument_sequencenumber = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_transportdocument,
                                'sequenceNumber',
                                text=str(l + 1)
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_transportdocument_referencenumber = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_transportdocument,
                                'referenceNumber',
                                text=transprot_document['reference number']
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_transportdocument_type = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_transportdocument,
                                'type',
                                text=self.input_information['type(CL754)']
                            )

                    if flag_exporter != 1:
                        if self.declaration_exporter[sequence_number_declaration]['ConsignorName'] != '':
                            zc415hub_declaration_goodsshipment_goodsitem_exporter = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem,
                                'Exporter'
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_name = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter,
                                'name',
                                text=self.declaration_exporter[sequence_number_declaration]['ConsignorName']
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_address = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter,
                                'Address'
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_address_streetandnumber = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter_address,
                                'streetAndNumber',
                                text=self.declaration_exporter[sequence_number_declaration]['ConsignorStreetAndNr']
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_address_postcode = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter_address,
                                'postcode',
                                text=str(self.declaration_exporter[sequence_number_declaration]['ConsignorPostcode'])
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_address_city = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter_address,
                                'city',
                                text=self.declaration_exporter[sequence_number_declaration]['ConsignorCity']
                            )

                            zc415hub_declaration_goodsshipment_goodsitem_exporter_address_country = xml_gen.add_sub_element(
                                zc415hub_declaration_goodsshipment_goodsitem_exporter_address,
                                'country',
                                text=self.declaration_exporter[sequence_number_declaration]['ConsignorCountry']
                            )

                    zc415hub_declaration_goodsshipment_goodsitem_intrinsicvalue = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'IntrinsicValue'
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_intrinsicvalue_currency = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem_intrinsicvalue,
                        'currency',
                        text=row['InvoiceCurrency']
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_intrinsicvalue_amount = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem_intrinsicvalue,
                        'amount',
                        text=str(row['Total Price'])
                    )

                    # zc415hub_declaration_goodsshipment_goodsitem_transportcoststodestination = xml_gen.add_sub_element(
                    #     zc415hub_declaration_goodsshipment_goodsitem,
                    #     'TransportCostsToDestination'
                    # )
                    #
                    # zc415hub_declaration_goodsshipment_goodsitem_transportcoststodestination_currency = xml_gen.add_sub_element(
                    #     zc415hub_declaration_goodsshipment_goodsitem_transportcoststodestination,
                    #     'currency',
                    #     text=''
                    # )
                    #
                    # zc415hub_declaration_goodsshipment_goodsitem_transportcoststodestination_amount = xml_gen.add_sub_element(
                    #     zc415hub_declaration_goodsshipment_goodsitem_transportcoststodestination,
                    #     'amount',
                    #     text=''
                    # )

                    # 此项必须存在
                    zc415hub_declaration_goodsshipment_goodsitem_packaging = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'Packaging'
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_packaging_sequencenumber = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem_packaging,
                        'sequenceNumber',
                        text='1'
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_packaging_numberofpackages = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem_packaging,
                        'numberOfPackages',
                        text=str(row['AmountPackages'])
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_commoditycode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem,
                        'CommodityCode'
                    )

                    zc415hub_declaration_goodsshipment_goodsitem_commoditycode_harmonisedsystemsubheadingcode = xml_gen.add_sub_element(
                        zc415hub_declaration_goodsshipment_goodsitem_commoditycode,
                        'harmonisedSystemSubheadingCode',
                        text=str(row['HSCode'])
                    )

                sequence_number_declaration += 1

            # signature = xml_gen.add_element("Signature")

            # 构建输出的 XML 文件路径
            output_file = os.path.splitext(os.path.basename(file_path))[0] + ".xml"
            output_file_path = os.path.join(target_dir, output_file)

            # 将 XML 写入文件
            xml_gen.write_to_file(output_file_path)
            print(f"XML 文件生成成功: {output_file_path}")

        except Exception as e:
            print(f'Error processing file {file_path}: {str(e)}')
