import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from utils.path import get_resource_path

# 设置字体路径，请根据你的文件夹路径调整
font_path = get_resource_path("fonts/Noto_Sans/static/NotoSans-Regular.ttf")

# 注册字体
pdfmetrics.registerFont(TTFont("NotoSans", font_path))

mapping = {
    # 'OdrzucenieKomunikatu': 'Element główny. Zawiera wszystkie pozostałe elementy.',
    'NumerIdentyfikacyjny': 'Numer Identyfikacyjny.',
    'IdentyfikatorECIPSEAP': 'Identyfikator ECIP SEAP.',
    'NazwaPodmiotuWydajacego': 'Nazwa Podmiotu wydającego komunikat.',
    'NazwaSystemuWydajacego': 'Nazwa Systemu wydajacego komunikat.',
    'DataDoreczenia': 'Data i czas, w którym wpłynął komunikat od klienta.',
    'DataWytworzenia': 'Data wygenerowania komunikatu.',
    'Dokument': 'Dokument. Element grupujący dane dokumentu przesłanego przez podmiot.',
    'Skrot': 'Skrót oryginalnego dokumentu.',
    'Tresc': 'Treść',
    'Typ': 'Sposób kodowania dokumentu.',
    'NrWlasny': 'Identyfikator nadany przez Klienta.',
    'Informacja': 'Dodatkowe informacje, np. ostrzeżenia z walidatora.',
    # 'Rodzaj': 'W przypadku Urzędowego Poświadczenia Odbioru (UPO) mogą pojawić się wyłącznie "WARNING" lub "INFO". W przypadku nie-UPO wyłącznie "ERROR".',
    'Tekst': 'Tekst komunikatu informacyjnego (może być w jednym lub dwóch językach).',
    'Jezyk': 'Język komunikatu informacyjnego.',
    'WskaznikXpath': 'Ścieżka w przesłanym w dokumencie XML, do której odnosi się informacja.',
    'Xpath': 'Ścieżka w przesłanym w dokumencie XML, do której odnosi się informacja.',

    'UPO': 'Element główny. Zawiera wszystkie pozostałe elementy.',

    # 'ZCX02HUB': 'Element główny komunikatu',
    'preparationDateAndTime': 'Data i czas utworzenia komunikatu',
    'messageIdentification': 'Identyfikator komunikatu',
    'correlationIdentifier': 'Identyfikator korelacji',
    'Declaration': 'Zgłoszenie',
    'upoIdentificationNumber': 'Identyfikator UPO',
    'Cancellation': 'Anulowanie zgłoszenia',
    'cancellationReason': 'Uzasadnienie anulowania',
    'Importer': 'Importera',
    'name': 'Nazwa / imię i nazwisko',
    'identificationNumber': 'Numer identyfikacyjny',
    'Address': 'Adres',
    'streetAndNumber': 'Ulica i numer domu',
    'postcode': 'Kod pocztowy',
    'city': 'Miejscowość',
    'country': 'Państwo',
    'Declarant': 'Zgłaszający',
    'ContactPerson': 'Osoba kontaktowa',
    'phoneNumber': 'Numer telefonu',
    'eMailAddress': 'Adres e-mail',
    'Representative': 'Przedstawiciel',
    'status': 'Status',
    'CustomsOfficeOfDeclaration': 'Urząd celny zgłoszenia',
    'referenceNumber': 'Numer referencyjny',

    # 'ZCX03HUB': 'Element główny komunikatu',
    'Signature': 'Podpis elektroniczny',

    'withdrawalReason': 'Powód wycofania',
    'Invalidation': 'Unieważnienie',
    'invalidationRequestUPOIdentificationNumber': 'Identyfikator UPO dla wniosku o unieważnienie',

    'additionalDeclarationType': 'Rodzaj dodatkowego zgłoszenia/deklaracji',
    'Rejection': 'Odmowa przyjęcia',
    'rejectionDateAndTime': 'Data i godzina odmowy przyjęcia',
    'rejectionReason': 'Uzasadnienie odmowy',
    'Error': 'Błąd',
    'pointer': 'XPath',
    'description': 'Opis',

    'GoodsShipment': 'Wysyłka towarów',
    'GoodsItem': 'Towar',
    'goodsItemNumber': 'Numer pozycji towarowej',
    'goodsItemState': 'Status pozycji towarowej',
    'text': 'Tekst',

    'Correction': 'Propozycja korekty',
    'instruction': 'Pouczenie',
    'correctionNumber': 'Numer korekty',
    'dateAndTime': 'Data i godzina zaproponowania korekty',
    'reason': 'Uzasadnienie korekty',
    'Change': 'Szczegóły proponowanej korekty',
    'valueBefore': 'Wartość przed korektą',
    'valueAfter': 'Wartość po korekcie',

    'decision': 'Decyzja w przedmiocie zaproponowanej korekty danych',

    'invalidationReason': 'Uzasadnienie wniosku o unieważnienie',
    'invalidationLRN': 'LRN',
    'invalidationUpoIdentificationNumber': 'Identyfikator UPO',

    'referenceNumberUCR': 'Numer referencyjny',
    'grossMass': 'Masa brutto',
    'PreviousDocument': 'Dokument poprzedni',
    'type': 'Rodzaj',
    'goodsItemIdentifier': 'Identyfikator pozycji towarowej',
    'AdditionalInformation': 'Dodatkowe informacje',
    'code': 'Kod',
    'SupportingDocument': 'Załączany dokument',
    'AdditionalReference': 'Dodatkowe odniesienie',
    'TransportDocument': 'Dokument przewozowy',
    'Exporter': 'Eksporter',
    'AdditionalFiscalReference': 'Dodatkowe odniesienie podatkowe',
    'role': 'Rola',
    'vatIdentificationNumber': 'Numer identyfikacyjny VAT',
    'TransportCostsToDestination': 'Koszty ubezpieczenia oraz transportu do miejsca przeznaczenia',
    'currency': 'Kod waluty',
    'amount': 'Kwota',
    'LocationOfGoods': 'Lokalizacja towarów',
    'typeOfLocation': 'Rodzaj lokalizacji',
    'qualifierOfIdentification': 'Kwalifikator oznaczenia',
    'unLocode': 'UN/LOCODE',
    'authorisationNumber': 'Numer pozwolenia',
    'additionalIdentifier': 'Dodatkowy identyfikator',
    'CustomsOffice': 'Urząd Celny',
    'GNSS': 'GNSS (ang. Global Navigation Satellite Systems)',
    'latitude': 'Szerokość geograficzna',
    'longitude': 'Długość geograficzna',
    'EconomicOperator': 'Przedsiębiorca',
    'PostcodeAddress': 'Adres pocztowy',
    'houseNumber': 'Numer domu',
    'descriptionOfGoods': 'Opis towarów',
    'AdditionalProcedure': 'Procedura dodatkowa',
    'additionalProcedure': 'Procedura dodatkowa',
    'IntrinsicValue': 'Wartość rzeczywista',
    'Packaging': 'Opakowanie',
    'numberOfPackages': 'Liczba opakowań',
    'CommodityCode': 'Kod towarowy',
    'harmonisedSystemSubheadingCode': 'Kod HS.',

    'declarationAcceptanceDate': 'Data i godzina przyjęcia dokumentu',
    'Warning': 'Ostrzeżenie',
    'officeAnnotations': 'Adnotacje urzędowe',
    'releaseDate': 'Data i godzina zwolnienia towaru',
    'validationDate': 'Data walidacji',
    'DutiesAndTaxes': 'Cła i podatki',
    'taxType': 'Rodzaj opłaty',
    'methodOfPayment': 'Metoda płatności',
    'payableTaxAmount': 'Kwota należnej opłaty',
    'TaxBase': 'Podstawa opłaty',
    'taxRate': 'Stawka opłaty',
    'measurementUnitAndQualifier': 'Jednostka miary i kwalifikator',
    'quantity': 'Ilość',
    'taxAmount': 'Kwota opłaty',

    'RequestedDocument': 'Dokumenty wymagane',
    'issuingAuthorityName': 'Organ wydający',
    'dateOfValidity': 'Data ważności',
    'documentLineItemNumber': 'Numer pozycji w dokumencie wymaganym',
    'eDocReferenceNumber': 'Identyfikator dokumentu przekazanego w wersji elektronicznej',

    'anticipatedControlDate': 'Planowana data i godzina kontroli',
    'electronicFormAllowed': 'Czy akceptowana wersja elektroniczna'
}


def draw_text_wrapped(pdf, text, x, y, line_width):
    """
    将长文本拆分为多行并绘制到 PDF 中。
    """
    font_size = 10
    pdf.setFont("NotoSans", font_size)

    # 拆分文本
    words = text.split(' ')
    current_line = ''
    max_width = line_width

    for word in words:
        # 构造当前行的文本
        test_line = current_line + (' ' if current_line else '') + word
        # 计算行宽
        line_width_test = pdf.stringWidth(test_line, "NotoSans", font_size)

        # 如果当前行的宽度超出最大宽度，则绘制当前行并换行
        if line_width_test <= max_width:
            current_line = test_line
        else:
            pdf.drawString(x, y, current_line)  # 绘制当前行
            y -= 10  # 减小行间距
            current_line = word  # 新的一行从当前单词开始

    # 绘制最后一行
    pdf.drawString(x, y, current_line)
    y -= 10  # 减小行间距

    return y


def draw_dict(pdf, data, x=50, y=800, indent=0, mapping=None, column=1):
    indent_space = ' ' * indent  # 根据缩进级别添加空格
    indent_space_width = 5  # 每级缩进的宽度

    # 设置字体为6号
    pdf.setFont("NotoSans", 10)

    for key, value in data.items():
        current_x = x + indent * indent_space_width  # 根据缩进级别调整 x 坐标
        line_width = 250 - indent * indent_space_width  # 根据缩进级别调整横线长度

        # 检查 value 是否是字典
        if isinstance(value, dict):
            # 如果字典中只有一个键 'value'，直接显示这个键的值
            if 'value' in value and len(value) == 1:
                y -= 10  # 减少行间距
                # 输出波兰文解释
                if mapping and key in mapping:
                    y = draw_text_wrapped(pdf, f"{indent_space}{mapping[key]}", current_x, y, line_width)  # 输出波兰文
                y = draw_text_wrapped(pdf, f"{indent_space}{key}: {value['value']}", current_x, y, line_width)  # 直接显示值
            else:
                y -= 10  # 减少行间距
                # 输出波兰文解释
                if mapping and key in mapping:
                    y = draw_text_wrapped(pdf, f"{indent_space}{mapping[key]}", current_x, y, line_width)  # 输出波兰文
                y = draw_text_wrapped(pdf, f"{indent_space}{key}:", current_x, y, line_width)  # 绘制字典的 key
                # 只在字典 key 绘制时绘制横线
                pdf.setStrokeColorRGB(0, 0, 0)  # 设置黑色
                pdf.setLineWidth(1)  # 设置线宽
                pdf.line(current_x, y - 5, current_x + line_width, y - 5)  # 绘制缩进后的横线
                y, column, x = draw_dict(pdf, value, x, y - 6, indent + 1, mapping, column)  # 递归绘制嵌套的字典

        # 如果 value 是列表，则逐个处理
        elif isinstance(value, list):
            y -= 10  # 减少行间距
            # 输出波兰文解释
            if mapping and key in mapping:
                y = draw_text_wrapped(pdf, f"{indent_space}{mapping[key]}", current_x, y, line_width)  # 输出波兰文
            y = draw_text_wrapped(pdf, f"{indent_space}{key}:", current_x, y, line_width)  # 绘制列表的 key
            # 只在列表 key 绘制时绘制一次横线
            pdf.setStrokeColorRGB(0, 0, 0)
            pdf.setLineWidth(1)
            pdf.line(current_x, y - 5, current_x + line_width, y - 5)

            for item in value:
                y -= 10  # 减少行间距
                if isinstance(item, dict):
                    y, column, x = draw_dict(pdf, item, x, y, indent + 1, mapping, column)  # 处理字典类型的列表元素
                else:
                    y = draw_text_wrapped(pdf, f"{item}", current_x + indent_space_width, y, line_width)  # 绘制列表元素

        # 其他情况，直接绘制 key-value 对
        else:
            y -= 10  # 减少行间距
            # 输出波兰文解释
            if mapping and key in mapping:
                y = draw_text_wrapped(pdf, f"{indent_space}{mapping[key]}", current_x, y, line_width)  # 输出波兰文
            y = draw_text_wrapped(pdf, f"{indent_space}{key}: {value}", current_x, y, line_width)  # 绘制 key-value 对

        # 检查是否到页面底部，如果到达，则另起一页
        if y < 75:
            if column == 1:
                y = 800
                column = 2
                x = 300  # 右栏起始位置
            else:
                pdf.showPage()  # 换页
                y = 800
                column = 1
                x = 50  # 左栏起始位置

    return y, column, x


def draw_header(pdf, signature_info, x=50, y=800, flag=None):
    """
    在 PDF 顶部绘制固定的两行签名和城市信息。
    """
    if flag == 1:
        font_size = 10
        pdf.setFont("NotoSans", font_size)
        pdf.drawString(x, y, "IssuerName:")
        y -= 15
        pdf.drawString(x, y, signature_info['CN'] + ',')
        y -= 15
        pdf.drawString(x, y, signature_info['OU'] + ',')
        y -= 15
        pdf.drawString(x, y, signature_info['O'] + ', ' + signature_info['C'])
        y -= 15
        pdf.drawString(x, y, "SigningTime: " + signature_info['SigningTime'])
        y -= 20  # 为接下来的内容留出更多的空间
        return y
    elif flag == 0:
        font_size = 10
        pdf.setFont("NotoSans", font_size)
        pdf.drawString(x, y, "signer (sygnatariusz): " + signature_info['name'])
        y -= 15
        pdf.drawString(x, y, "phoneNumber: " + signature_info['phoneNumber'])
        y -= 15
        pdf.drawString(x, y, "eMailAddress: " + signature_info['eMailAddress'])
        y -= 15
        pdf.drawString(x, y, "signatue_time: " + signature_info['signingTime'])
        y -= 20  # 为接下来的内容留出更多的空间
        return y
    else:
        return y


'''
1.	dict_to_pdf(data):
•	这个函数创建一个内存中的 PDF 文件。使用 io.BytesIO() 创建一个字节流缓冲区（buffer），所有生成的 PDF 内容都在内存中保存。
•	PDF 绘制完成后，函数通过 buffer.getvalue() 返回 PDF 的字节内容，而不将其保存到本地文件。这种方式适合于将生成的 PDF 直接发送到网络、电子邮件等，而不需要在本地存储。
2.	save_pdf(data, output_file):
•	这个函数将生成的 PDF 直接保存到指定的本地文件（output_file）。
•	在此函数中，您传递了一个文件路径，PDF 内容会被写入到这个文件中。

总结起来，dict_to_pdf 适用于需要将 PDF 内容直接作为数据处理的情况，而 save_pdf 则适用于将生成的 PDF 保存为文件以备将来使用。
'''


# 将pdf的内容显示到前端页面当中
def dict_to_pdf(data, signature_info, flag=None):
    buffer = io.BytesIO()  # 创建一个内存缓冲区
    pdf = canvas.Canvas(buffer, pagesize=A4)
    y_position = draw_header(pdf, signature_info, flag=flag)
    draw_dict(pdf, data, y=y_position, mapping=mapping)
    pdf.save()
    buffer.seek(0)  # 将指针移回缓冲区的开头
    return buffer.getvalue()  # 返回PDF的字节内容


# 保存为本地的pdf文件
def save_pdf(data, output_file, representative_contact_person, flag=None):
    pdf = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    y_position = draw_header(pdf, representative_contact_person, flag=flag)
    draw_dict(pdf, data, y=y_position, mapping=mapping)
    pdf.save()
