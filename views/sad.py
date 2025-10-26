import sys
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, \
    QGroupBox, QScrollArea, QDialog, QVBoxLayout, QDialogButtonBox, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from utils.vertical_label import VerticalLabel

from utils.clickable_groupbox import ClickableGroupBox
from utils.sad_information import SADInformation

from views.input_sad_information import InputSADInformationDialog
from views.goodsitem_manual_information import GoodsitemManualInformation

from utils import db


# SAD表单
class SADWindow(QDialog):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.username = kwargs.get('username', None)
        self.index_item_number = 0
        input_information = kwargs.get('input_information', None)
        self.manual_datas = kwargs.get('manual_datas', None)
        # print(self.manual_datas)

        self.main_id_for_sub_table_data = kwargs.get('main_id_for_sub_table_data', None)

        self.main_table_id = kwargs.get('main_table_id', None)
        self.sub_table_id = kwargs.get('sub_table_id', None)

        self.goodshipment_CL380 = db.get_sub_table_data_from_sub_table_by_sub_id(self.sub_table_id, self.username)
        self.if_sent = db.is_state_sent_of_sub_table(self.sub_table_id, self.username)

        data_rows = kwargs.get('data_rows', None)

        self.sad_information = SADInformation(input_information, data_rows)

        self.number_of_declaraion = len(self.sad_information.key_declaration_dict)
        self.sequence_number_declaraion = 0

        self.number_of_declaraion_goods = {key: len(self.sad_information.declaration_dict[key]) for key in
                                           self.sad_information.key_declaration_dict}
        # print(self.number_of_declaraion_goods)
        self.sequene_number_goods = 0

        self.initUI()
        self.update_data()

    def initUI(self):
        self.setGeometry(0, 0, 1450, 800)
        self.setWindowTitle('SAD')

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # 创建一个主Widget，并设置其大小
        main_widget = QWidget()
        main_widget.setMinimumSize(1405, 1830)  # 这里设置滚动区域的大小
        scroll_area.setWidget(main_widget)

        self.sad_groupbox_AIS = QGroupBox(main_widget)
        self.sad_groupbox_AIS.setGeometry(50, 15, 500, 30)
        self.sad_groupbox_AIS.setStyleSheet('QGroupBox {border: none;}')
        self.sad_groupbox_AIS_label1 = QLabel('WSPOLNOTA EUROPEJSKA', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label1.setStyleSheet("font-size: 25px;")
        self.sad_groupbox_AIS_label1.move(5, 1)
        # self.sad_groupbox_AIS_prev_button = QPushButton('<', self.sad_groupbox_AIS)
        # self.sad_groupbox_AIS_prev_button.setFixedWidth(35)
        # self.sad_groupbox_AIS_prev_button.move(350, 5)
        # self.sad_groupbox_AIS_prev_button.clicked.connect(self.prev_goods_sequence_number)
        # self.sad_groupbox_AIS_lineedit = QLineEdit(self.sad_groupbox_AIS)
        # self.sad_groupbox_AIS_lineedit.setValidator(QIntValidator(0, self.number_of_declaraion_goods[
        #     self.sad_information.key_declaration_dict[self.sequence_number_declaraion]] - 1))
        # self.sad_groupbox_AIS_lineedit.setFixedWidth(45)
        # self.sad_groupbox_AIS_lineedit.setAlignment(Qt.AlignRight)
        # self.sad_groupbox_AIS_lineedit.setText('1')
        # self.sad_groupbox_AIS_lineedit.setStyleSheet('border-radius: 3px;')
        # self.sad_groupbox_AIS_lineedit.textChanged.connect(self.adjust_goods_sequence_number)
        # self.sad_groupbox_AIS_lineedit.move(380, 11)
        # self.sad_groupbox_AIS_next_button = QPushButton('>', self.sad_groupbox_AIS)
        # self.sad_groupbox_AIS_next_button.setFixedWidth(35)
        # self.sad_groupbox_AIS_next_button.move(420, 5)
        # self.sad_groupbox_AIS_next_button.clicked.connect(self.next_goods_sequence_number)
        # self.sad_groupbox_AIS_jump_button = QPushButton('jump', self.sad_groupbox_AIS)
        # self.sad_groupbox_AIS_jump_button.setFixedWidth(60)
        # self.sad_groupbox_AIS_jump_button.move(445, 5)
        # self.sad_groupbox_AIS_jump_button.clicked.connect(self.jump_to_goods_sequence_number)

        self.sad_groupbox_title = QGroupBox(main_widget)
        self.sad_groupbox_title.setGeometry(50, 50, 50, 598)
        self.sad_groupbox_title.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        self.sad_groupbox_title_label1 = QLabel('6', self.sad_groupbox_title)
        self.sad_groupbox_title_label1.setStyleSheet("font-size: 30px; border: 1px solid #222; border-right: none;")
        self.sad_groupbox_title_label1.setGeometry(0, 0, 50, 50)
        self.sad_groupbox_title_label1.setAlignment(Qt.AlignCenter)
        self.sad_groupbox_title_label2 = VerticalLabel('Egzemplarz dla kraju przeznaczenia', self.sad_groupbox_title)
        self.sad_groupbox_title_label2.setStyleSheet("font-size: 25px; border: 1px solid #222; border-right: none;")
        self.sad_groupbox_title_label2.setGeometry(0, 0, 50, 598)
        self.sad_groupbox_title_label2.setAlignment(Qt.AlignCenter)
        self.sad_groupbox_title_label3 = QLabel('6', self.sad_groupbox_title)
        self.sad_groupbox_title_label3.setStyleSheet("font-size: 30px; border: 1px solid #222; border-right: none;")
        self.sad_groupbox_title_label3.setGeometry(0, 548, 50, 50)
        self.sad_groupbox_title_label3.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_A = QGroupBox(main_widget)
        self.sad_groupbox_A.setGeometry(760, 10, 300, 135)
        self.sad_groupbox_A.setStyleSheet('QGroupBox {border: 1px solid #222; border-bottom: none;}')
        # URZAD PRZEZNACZENIA
        self.sad_groupbox_A_label1 = QLabel('A URZAD PRZEZNACZENIA', self.sad_groupbox_A)
        self.sad_groupbox_A_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_A_label1.move(5, 1)
        self.sad_groupbox_A_label2 = QLabel('', self.sad_groupbox_A)
        self.sad_groupbox_A_label2.setGeometry(15, 15, 270, 120)
        self.sad_groupbox_A_label2.setWordWrap(True)
        self.sad_groupbox_A_label2.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.sad_groupbox_1 = ClickableGroupBox(main_widget)
        self.sad_groupbox_1.setGeometry(600, 35, 160, 65)
        self.sad_groupbox_1.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        if not self.if_sent:
            self.sad_groupbox_1.clicked.connect(lambda: self.open_input_sad_information_dialog(0))
        self.sad_groupbox_1_label1 = QLabel('1 Z G L O S Z E N I E', self.sad_groupbox_1)
        self.sad_groupbox_1_label1.move(5, 1)
        self.sad_groupbox_1_label2 = QLabel('', self.sad_groupbox_1)
        self.sad_groupbox_1_label2.setStyleSheet("border: 1px solid #222; border-top: none;")
        self.sad_groupbox_1_label2.setGeometry(0, 20, 76, 45)
        self.sad_groupbox_1_label2.setAlignment(Qt.AlignCenter)
        self.sad_groupbox_1_label3 = QLabel('', self.sad_groupbox_1)
        self.sad_groupbox_1_label3.setStyleSheet("border: 1px solid #222; border-top: none;")
        self.sad_groupbox_1_label3.setGeometry(75, 20, 22, 45)
        self.sad_groupbox_1_label3.setAlignment(Qt.AlignCenter)
        self.sad_groupbox_1_label4 = QLabel('', self.sad_groupbox_1)
        # self.sad_groupbox_1_label4.setStyleSheet("border: 1px solid #222; border-top: none;")
        self.sad_groupbox_1_label4.setGeometry(95, 20, 70, 45)
        self.sad_groupbox_1_label4.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_2 = QGroupBox(main_widget)
        self.sad_groupbox_2.setGeometry(100, 50, 500, 140)
        self.sad_groupbox_2.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        # 托运人/出口商
        self.sad_groupbox_2_label1 = QLabel('2 Nadawcal/eksporter', self.sad_groupbox_2)
        self.sad_groupbox_2_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_2_label1.move(5, 3)
        self.sad_groupbox_2_label2 = QLabel('Nr', self.sad_groupbox_2)
        self.sad_groupbox_2_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_2_label2.move(240, 3)
        self.sad_groupbox_2_label3 = QLabel('BN', self.sad_groupbox_2)
        self.sad_groupbox_2_label3.move(420, 1)
        self.sad_groupbox_2_label4 = QLabel('', self.sad_groupbox_2)
        self.sad_groupbox_2_label4.setGeometry(15, 20, 470, 120)
        self.sad_groupbox_2_label4.setWordWrap(True)
        self.sad_groupbox_2_label4.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.sad_groupbox_2_edit = QPlainTextEdit(self.sad_groupbox_2)
        # self.sad_groupbox_2_edit.setGeometry(5, 20, 490, 95)
        self.sad_groupbox_2_label5 = QLabel('BR', self.sad_groupbox_2)
        self.sad_groupbox_2_label5.move(440, 120)

        self.sad_groupbox_3 = QGroupBox(main_widget)
        self.sad_groupbox_3.setGeometry(600, 100, 81, 45)
        self.sad_groupbox_3.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_3_label1 = QLabel('3 Formularze', self.sad_groupbox_3)
        self.sad_groupbox_3_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_3_label1.move(5, 1)
        self.sad_groupbox_3_label2 = QLabel('', self.sad_groupbox_3)
        self.sad_groupbox_3_label2.setGeometry(0, 15, 79, 30)
        self.sad_groupbox_3_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_4 = QGroupBox(main_widget)
        self.sad_groupbox_4.setGeometry(680, 100, 80, 45)
        self.sad_groupbox_4.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_4_label1 = QLabel('4 Wyk. zalad.', self.sad_groupbox_4)
        self.sad_groupbox_4_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_4_label1.move(5, 1)
        self.sad_groupbox_4_label2 = QLabel('', self.sad_groupbox_4)
        self.sad_groupbox_4_label2.setGeometry(0, 15, 80, 30)
        self.sad_groupbox_4_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_5 = QGroupBox(main_widget)
        self.sad_groupbox_5.setGeometry(600, 145, 80, 45)
        self.sad_groupbox_5.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_5_label1 = QLabel('5 Pozycje', self.sad_groupbox_5)
        self.sad_groupbox_5_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_5_label1.move(5, 1)
        self.sad_groupbox_5_label2 = QLabel('', self.sad_groupbox_5)
        self.sad_groupbox_5_label2.setGeometry(0, 15, 80, 30)
        self.sad_groupbox_5_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_6 = QGroupBox(main_widget)
        self.sad_groupbox_6.setGeometry(680, 144, 110, 46)
        self.sad_groupbox_6.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        self.sad_groupbox_6_label1 = QLabel('6 Liczba opakowan', self.sad_groupbox_6)
        self.sad_groupbox_6_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_6_label1.move(5, 2)
        self.sad_groupbox_6_label2 = QLabel('', self.sad_groupbox_6)
        self.sad_groupbox_6_label2.setGeometry(0, 16, 110, 30)
        self.sad_groupbox_6_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_7 = QGroupBox(main_widget)
        self.sad_groupbox_7.setGeometry(790, 144, 270, 46)
        self.sad_groupbox_7.setStyleSheet('QGroupBox {border: 1px solid #222;}')
        self.sad_groupbox_7_label1 = QLabel('7 Numer referncyjny', self.sad_groupbox_7)
        self.sad_groupbox_7_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_7_label1.move(5, 2)
        self.sad_groupbox_7_label2 = QLabel('', self.sad_groupbox_7)
        self.sad_groupbox_7_label2.setGeometry(15, 16, 255, 30)

        self.sad_groupbox_8 = QGroupBox(main_widget)
        self.sad_groupbox_8.setGeometry(100, 190, 500, 140)
        self.sad_groupbox_8.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-right: none;}')
        # 接受者
        self.sad_groupbox_8_label1 = QLabel('8 Odbiorca', self.sad_groupbox_8)
        self.sad_groupbox_8_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_8_label1.move(5, 3)
        self.sad_groupbox_8_label2 = QLabel('Nr', self.sad_groupbox_8)
        self.sad_groupbox_8_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_8_label2.move(240, 3)
        self.sad_groupbox_8_label3 = QLabel('', self.sad_groupbox_8)
        self.sad_groupbox_8_label3.move(330, 1)
        self.sad_groupbox_8_label4 = QLabel('', self.sad_groupbox_8)
        self.sad_groupbox_8_label4.setGeometry(15, 20, 470, 120)
        self.sad_groupbox_8_label4.setWordWrap(True)
        self.sad_groupbox_8_label4.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.sad_groupbox_8_edit = QPlainTextEdit(self.sad_groupbox_8)
        # self.sad_groupbox_8_edit.setGeometry(5, 20, 490, 95)
        self.sad_groupbox_8_label5 = QLabel('', self.sad_groupbox_8)
        self.sad_groupbox_8_label5.move(360, 120)
        self.sad_groupbox_8_prev_button = QPushButton('<', self.sad_groupbox_8)
        self.sad_groupbox_8_prev_button.setFixedWidth(35)
        self.sad_groupbox_8_prev_button.move(360, 20)
        self.sad_groupbox_8_prev_button.clicked.connect(self.prev_declaration_sequence_number)
        self.sad_groupbox_8_lineedit = QLineEdit(self.sad_groupbox_8)
        self.sad_groupbox_8_lineedit.setValidator(QIntValidator(1, self.number_of_declaraion))
        self.sad_groupbox_8_lineedit.setFixedWidth(30)
        self.sad_groupbox_8_lineedit.setAlignment(Qt.AlignRight)
        self.sad_groupbox_8_lineedit.setText('1')
        self.sad_groupbox_8_lineedit.setStyleSheet('border-radius: 3px;')
        self.sad_groupbox_8_lineedit.textChanged.connect(self.adjust_declaration_sequence_number)
        self.sad_groupbox_8_lineedit.move(390, 26)
        self.sad_groupbox_8_next_button = QPushButton('>', self.sad_groupbox_8)
        self.sad_groupbox_8_next_button.setFixedWidth(35)
        self.sad_groupbox_8_next_button.move(415, 20)
        self.sad_groupbox_8_next_button.clicked.connect(self.next_declaration_sequence_number)
        self.sad_groupbox_8_jump_button = QPushButton('jump', self.sad_groupbox_8)
        self.sad_groupbox_8_jump_button.setFixedWidth(60)
        self.sad_groupbox_8_jump_button.move(440, 20)
        self.sad_groupbox_8_jump_button.clicked.connect(self.jump_to_declaration_sequence_number)

        self.sad_groupbox_9 = QGroupBox(main_widget)
        self.sad_groupbox_9.setGeometry(600, 190, 460, 95)
        self.sad_groupbox_9.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_9_label1 = QLabel('9 Osoba odpowiedzialna za sprawy finansowe', self.sad_groupbox_9)
        self.sad_groupbox_9_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_9_label1.move(5, 1)
        self.sad_groupbox_9_label2 = QLabel('Nr.', self.sad_groupbox_9)
        self.sad_groupbox_9_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_9_label2.move(280, 1)
        self.sad_groupbox_9_label3 = QLabel('', self.sad_groupbox_9)
        self.sad_groupbox_9_label3.setGeometry(15, 20, 430, 75)
        self.sad_groupbox_9_label3.setWordWrap(True)
        self.sad_groupbox_9_label3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # self.sad_groupbox_9_edit = QPlainTextEdit(self.sad_groupbox_9)
        # self.sad_groupbox_9_edit.setGeometry(5, 15, 450, 75)

        self.sad_groupbox_10 = QGroupBox(main_widget)
        self.sad_groupbox_10.setGeometry(600, 285, 110, 45)
        self.sad_groupbox_10.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_10_label1 = QLabel('10 Ostatni Krajzalad.', self.sad_groupbox_10)
        self.sad_groupbox_10_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_10_label1.move(5, 1)
        self.sad_groupbox_10_label2 = QLabel('', self.sad_groupbox_10)
        self.sad_groupbox_10_label2.setGeometry(0, 15, 110, 30)
        self.sad_groupbox_10_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_11 = QGroupBox(main_widget)
        self.sad_groupbox_11.setGeometry(710, 285, 105, 45)
        self.sad_groupbox_11.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_11_label1 = QLabel('11 Kraj handi/prod.', self.sad_groupbox_11)
        self.sad_groupbox_11_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_11_label1.move(5, 1)
        self.sad_groupbox_11_label2 = QLabel('', self.sad_groupbox_11)
        self.sad_groupbox_11_label2.setGeometry(0, 15, 105, 30)
        self.sad_groupbox_11_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_12 = QGroupBox(main_widget)
        self.sad_groupbox_12.setGeometry(815, 285, 180, 45)
        self.sad_groupbox_12.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_12_label1 = QLabel('12 Szczegoly dotyczace wartosci', self.sad_groupbox_12)
        self.sad_groupbox_12_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_12_label1.move(5, 1)
        self.sad_groupbox_12_label2 = QLabel('', self.sad_groupbox_12)
        self.sad_groupbox_12_label2.setGeometry(0, 15, 180, 30)
        self.sad_groupbox_12_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_13 = QGroupBox(main_widget)
        self.sad_groupbox_13.setGeometry(995, 285, 65, 45)
        self.sad_groupbox_13.setStyleSheet('QGroupBox {border: 1px solid #222;none; border-top: none;}')
        self.sad_groupbox_13_label1 = QLabel('13 W.P.R.', self.sad_groupbox_13)
        self.sad_groupbox_13_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_13_label1.move(5, 1)
        self.sad_groupbox_13_label2 = QLabel('', self.sad_groupbox_13)
        self.sad_groupbox_13_label2.setWordWrap(True)
        self.sad_groupbox_13_label2.setGeometry(0, 15, 65, 30)
        self.sad_groupbox_13_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_14 = ClickableGroupBox(main_widget)
        self.sad_groupbox_14.setGeometry(100, 330, 500, 105)
        self.sad_groupbox_14.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-right: none;}')
        if not self.if_sent:
            self.sad_groupbox_14.clicked.connect(lambda: self.open_input_sad_information_dialog(1))
        # 申请人/代表
        self.sad_groupbox_14_label1 = QLabel('14 Zgtaszajacy/Przedstawiciel', self.sad_groupbox_14)
        self.sad_groupbox_14_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_14_label1.move(5, 3)
        self.sad_groupbox_14_label2 = QLabel('Nr', self.sad_groupbox_14)
        self.sad_groupbox_14_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_14_label2.move(240, 3)
        self.sad_groupbox_14_label3 = QLabel('', self.sad_groupbox_14)
        self.sad_groupbox_14_label3.move(330, 1)
        # self.sad_groupbox_14_label4 = QLabel('', self.sad_groupbox_14)
        # self.sad_groupbox_14_label4.setGeometry(15, 20, 470, 85)
        # self.sad_groupbox_14_label4.setWordWrap(True)
        # self.sad_groupbox_14_label4.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        # 创建第二个标签
        self.sad_groupbox_14_label4 = QLabel(
            "sadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\nsadjfkjwaefjkajbejfbjakbejfa\n")  # 确保有足够的内容来测试滚动
        self.sad_groupbox_14_label4.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.sad_groupbox_14_label4.setWordWrap(True)
        # 创建 QScrollArea
        self.sad_groupbox_14_label4_scroll_area = QScrollArea(self.sad_groupbox_14)
        self.sad_groupbox_14_label4_scroll_area.setGeometry(15, 20, 470, 83)  # 设置位置和大小
        self.sad_groupbox_14_label4_scroll_area.setWidget(self.sad_groupbox_14_label4)
        self.sad_groupbox_14_label4_scroll_area.setWidgetResizable(True)  # 允许调整大小
        self.sad_groupbox_14_label4_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        self.sad_groupbox_14_label4_scroll_area.setStyleSheet('border: none;')  # 去掉边框
        # self.sad_groupbox_14_edit = QPlainTextEdit(self.sad_groupbox_14)
        # self.sad_groupbox_14_edit.setGeometry(5, 20, 490, 60)
        self.sad_groupbox_14_label5 = QLabel('', self.sad_groupbox_14)
        self.sad_groupbox_14_label5.move(360, 83)

        self.sad_groupbox_15_1 = QGroupBox(main_widget)
        self.sad_groupbox_15_1.setGeometry(600, 330, 150, 53)
        self.sad_groupbox_15_1.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_15_1_label1 = QLabel('15 Kraj wysylkj / wywozu', self.sad_groupbox_15_1)
        self.sad_groupbox_15_1_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_15_1_label1.move(5, 1)
        self.sad_groupbox_15_1_label2 = QLabel('', self.sad_groupbox_15_1)
        self.sad_groupbox_15_1_label2.setGeometry(0, 15, 150, 38)
        self.sad_groupbox_15_1_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_15_2 = QGroupBox(main_widget)
        self.sad_groupbox_15_2.setGeometry(750, 330, 150, 53)
        self.sad_groupbox_15_2.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_15_2_label1 = QLabel('15 Kod kr. wys. / wyw.', self.sad_groupbox_15_2)
        self.sad_groupbox_15_2_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_15_2_label1.move(5, 1)
        self.sad_groupbox_15_2_label2 = QLabel('', self.sad_groupbox_15_2)
        self.sad_groupbox_15_2_label2.setGeometry(0, 15, 150, 38)
        self.sad_groupbox_15_2_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_16 = QGroupBox(main_widget)
        self.sad_groupbox_16.setGeometry(600, 383, 230, 52)
        self.sad_groupbox_16.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_16_label1 = QLabel('16 Kraj pochodzenia', self.sad_groupbox_16)
        self.sad_groupbox_16_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_16_label1.move(5, 1)
        self.sad_groupbox_16_label2 = QLabel('', self.sad_groupbox_16)
        self.sad_groupbox_16_label2.setGeometry(15, 15, 200, 37)

        self.sad_groupbox_17_1 = QGroupBox(main_widget)
        self.sad_groupbox_17_1.setGeometry(900, 330, 160, 53)
        self.sad_groupbox_17_1.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_17_1_label1 = QLabel('17 Kod kraju przeznaczenia', self.sad_groupbox_17_1)
        self.sad_groupbox_17_1_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_17_1_label1.move(5, 1)
        self.sad_groupbox_17_1_label2 = QLabel('', self.sad_groupbox_17_1)
        self.sad_groupbox_17_1_label2.setGeometry(15, 15, 130, 38)
        self.sad_groupbox_17_1_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_17_2 = QGroupBox(main_widget)
        self.sad_groupbox_17_2.setGeometry(830, 383, 230, 52)
        self.sad_groupbox_17_2.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_17_2_label1 = QLabel('17 Kraj przeznaczenia', self.sad_groupbox_17_2)
        self.sad_groupbox_17_2_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_17_2_label1.move(5, 1)
        self.sad_groupbox_17_2_label2 = QLabel('', self.sad_groupbox_17_2)
        self.sad_groupbox_17_2_label2.setGeometry(15, 15, 200, 37)

        self.sad_groupbox_18 = QGroupBox(main_widget)
        self.sad_groupbox_18.setGeometry(100, 435, 440, 53)
        self.sad_groupbox_18.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_18_label1 = QLabel('18 Znaki i pizynaleznos parstwowa srodka transportu przy przybyciu',
                                             self.sad_groupbox_18)
        self.sad_groupbox_18_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_18_label1.move(5, 1)
        self.sad_groupbox_18_label2 = QLabel('', self.sad_groupbox_18)
        self.sad_groupbox_18_label2.setGeometry(15, 15, 410, 38)

        self.sad_groupbox_19 = QGroupBox(main_widget)
        self.sad_groupbox_19.setGeometry(540, 435, 60, 53)
        self.sad_groupbox_19.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_19_label1 = QLabel('19 Kont.', self.sad_groupbox_19)
        self.sad_groupbox_19_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_19_label1.move(5, 1)
        self.sad_groupbox_19_label2 = QLabel('', self.sad_groupbox_19)
        self.sad_groupbox_19_label2.setGeometry(0, 15, 60, 38)
        self.sad_groupbox_19_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_20 = QGroupBox(main_widget)
        self.sad_groupbox_20.setGeometry(600, 435, 460, 53)
        self.sad_groupbox_20.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_20_label1 = QLabel('20 Warunki dostawy', self.sad_groupbox_20)
        self.sad_groupbox_20_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_20_label1.move(5, 1)
        self.sad_groupbox_20_label2 = QLabel('', self.sad_groupbox_20)
        self.sad_groupbox_20_label2.setGeometry(15, 15, 430, 38)

        self.sad_groupbox_21 = QGroupBox(main_widget)
        self.sad_groupbox_21.setGeometry(100, 488, 500, 53)
        self.sad_groupbox_21.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_21_label1 = QLabel(
            '21 Znaki i przynależność par\' stwowa aktywnego srodka transportu przekraczajacego granice',
            self.sad_groupbox_21)
        self.sad_groupbox_21_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_21_label1.move(5, 1)
        self.sad_groupbox_21_label2 = QLabel('', self.sad_groupbox_21)
        self.sad_groupbox_21_label2.setGeometry(15, 15, 470, 38)

        self.sad_groupbox_22 = QGroupBox(main_widget)
        self.sad_groupbox_22.setGeometry(600, 488, 230, 53)
        self.sad_groupbox_22.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_22_label1 = QLabel('22 Waluta i ogólna wartość\' faktury', self.sad_groupbox_22)
        self.sad_groupbox_22_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_22_label1.move(5, 1)
        self.sad_groupbox_22_label2 = QLabel('EUR', self.sad_groupbox_22)
        self.sad_groupbox_22_label2.setGeometry(15, 15, 115, 38)
        self.sad_groupbox_22_label3 = QLabel('', self.sad_groupbox_22)
        self.sad_groupbox_22_label3.setGeometry(145, 15, 115, 38)

        self.sad_groupbox_23 = QGroupBox(main_widget)
        self.sad_groupbox_23.setGeometry(830, 488, 115, 53)
        self.sad_groupbox_23.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_23_label1 = QLabel('23 Kurs waluty', self.sad_groupbox_23)
        self.sad_groupbox_23_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_23_label1.move(5, 1)
        self.sad_groupbox_23_label2 = QLabel('', self.sad_groupbox_23)
        self.sad_groupbox_23_label2.setGeometry(15, 15, 85, 38)

        self.sad_groupbox_24 = QGroupBox(main_widget)
        self.sad_groupbox_24.setGeometry(945, 488, 115, 53)
        self.sad_groupbox_24.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        self.sad_groupbox_24_label1 = QLabel('24 Rodzaj transakcji', self.sad_groupbox_24)
        self.sad_groupbox_24_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_24_label1.move(5, 1)
        self.sad_groupbox_24_label2 = QLabel('', self.sad_groupbox_24)
        self.sad_groupbox_24_label2.setGeometry(15, 15, 85, 38)

        self.sad_groupbox_25 = QGroupBox(main_widget)
        self.sad_groupbox_25.setGeometry(100, 541, 125, 53)
        self.sad_groupbox_25.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # 边境运输类型
        self.sad_groupbox_25_label1 = QLabel('25 Rodzaj transportu \n na granicy', self.sad_groupbox_25)
        self.sad_groupbox_25_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_25_label1.move(5, 1)
        self.sad_groupbox_25_label2 = QLabel('', self.sad_groupbox_25)
        self.sad_groupbox_25_label2.setGeometry(15, 15, 95, 38)

        self.sad_groupbox_26 = QGroupBox(main_widget)
        self.sad_groupbox_26.setGeometry(225, 541, 125, 53)
        self.sad_groupbox_26.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # 内部运输类型
        self.sad_groupbox_26_label1 = QLabel('26 Rodzaj transportu \n wewnetrznego', self.sad_groupbox_26)
        self.sad_groupbox_26_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_26_label1.move(5, 1)
        self.sad_groupbox_26_label2 = QLabel('', self.sad_groupbox_26)
        self.sad_groupbox_26_label2.setGeometry(15, 15, 95, 38)

        self.sad_groupbox_27 = QGroupBox(main_widget)
        self.sad_groupbox_27.setGeometry(350, 541, 250, 53)
        self.sad_groupbox_27.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # 着陆地点
        self.sad_groupbox_27_label1 = QLabel('27 Miejsce wyladunku', self.sad_groupbox_27)
        self.sad_groupbox_27_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_27_label1.move(5, 1)
        self.sad_groupbox_27_label2 = QLabel('', self.sad_groupbox_27)
        self.sad_groupbox_27_label2.setGeometry(15, 15, 220, 38)

        self.sad_groupbox_28 = QGroupBox(main_widget)
        self.sad_groupbox_28.setGeometry(600, 541, 460, 106)
        self.sad_groupbox_28.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-bottom: none;}')
        # Adnotacje finansowe i bankowe
        self.sad_groupbox_28_label1 = QLabel('28 Adnotacje finansowe i bankowe', self.sad_groupbox_28)
        self.sad_groupbox_28_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_28_label1.move(5, 1)
        self.sad_groupbox_28_label2 = QLabel('', self.sad_groupbox_28)
        self.sad_groupbox_28_label2.setGeometry(15, 15, 430, 38)

        self.sad_groupbox_29 = ClickableGroupBox(main_widget)
        self.sad_groupbox_29.setGeometry(100, 594, 250, 53)
        self.sad_groupbox_29.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none; border-bottom: none;}')
        if not self.if_sent:
            self.sad_groupbox_29.clicked.connect(lambda: self.open_input_sad_information_dialog(2))
        # Urzad wprowadzenia
        self.sad_groupbox_29_label1 = QLabel('29 Urzad wprowadzenia', self.sad_groupbox_29)
        self.sad_groupbox_29_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_29_label1.move(5, 1)
        self.sad_groupbox_29_label2 = QLabel('', self.sad_groupbox_29)
        self.sad_groupbox_29_label2.setGeometry(15, 15, 220, 38)

        self.sad_groupbox_30 = ClickableGroupBox(main_widget)
        self.sad_groupbox_30.setGeometry(350, 594, 250, 53)
        self.sad_groupbox_30.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none; border-bottom: none;}')
        if not self.if_sent:
            self.sad_groupbox_30.clicked.connect(lambda: self.open_input_sad_information_dialog(3))
        # 货物所在地
        self.sad_groupbox_30_label1 = QLabel('30 Lokalizacja towaru', self.sad_groupbox_30)
        self.sad_groupbox_30_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_30_label1.move(5, 1)
        self.sad_groupbox_30_label2 = QLabel('', self.sad_groupbox_30)
        self.sad_groupbox_30_label2.setGeometry(15, 15, 220, 38)

        # self.sad_groupbox_31 = QGroupBox(main_widget)
        self.sad_groupbox_31 = ClickableGroupBox(main_widget)
        self.sad_groupbox_31.setGeometry(10, 647, 700, 240)
        self.sad_groupbox_31.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        if not self.if_sent:
            self.sad_groupbox_31.clicked.connect(self.open_goodsitem_manual_information_dialog)
        # Opakowania i opis towaru
        self.sad_groupbox_31_label1 = QLabel('31 Opakowania i opis towaru', self.sad_groupbox_31)
        self.sad_groupbox_31_label1.setStyleSheet("font-size: 11px; border: 1px solid #222;")
        self.sad_groupbox_31_label1.setGeometry(0, 0, 91, 240)
        self.sad_groupbox_31_label1.setWordWrap(True)
        self.sad_groupbox_31_label1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_31_label2 = QLabel('Znaki i numery-Numer(-y) kontenera (-ów)-Liczba i rodzaj',
                                             self.sad_groupbox_31)
        self.sad_groupbox_31_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_31_label2.move(100, 1)
        # self.sad_groupbox_31_label3 = QLabel('', self.sad_groupbox_31)
        # self.sad_groupbox_31_label3.setGeometry(100, 35, 490, 190)
        # self.sad_groupbox_31_label3.setWordWrap(True)
        # self.sad_groupbox_31_label3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_31_label3 = QLabel()  # 确保有足够的内容来测试滚动
        self.sad_groupbox_31_label3.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.sad_groupbox_31_label3.setWordWrap(True)
        # 创建 QScrollArea
        self.sad_groupbox_31_label3_scroll_area = QScrollArea(self.sad_groupbox_31)
        self.sad_groupbox_31_label3_scroll_area.setGeometry(100, 35, 445, 190)  # 设置位置和大小
        self.sad_groupbox_31_label3_scroll_area.setWidget(self.sad_groupbox_31_label3)
        self.sad_groupbox_31_label3_scroll_area.setWidgetResizable(True)  # 允许调整大小
        self.sad_groupbox_31_label3_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        self.sad_groupbox_31_label3_scroll_area.setStyleSheet('border: none;')  # 去掉边框

        self.sad_groupbox_32 = QGroupBox(main_widget)
        self.sad_groupbox_32.setGeometry(558, 647, 162, 53)
        self.sad_groupbox_32.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none;}')
        # Pozycja Nr
        self.sad_groupbox_32_label1 = QLabel('32 Pozycja Nr', self.sad_groupbox_32)
        self.sad_groupbox_32_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_32_label1.move(5, 1)
        self.sad_groupbox_32_prev_button = QPushButton('<', self.sad_groupbox_32)
        self.sad_groupbox_32_prev_button.setFixedWidth(35)
        self.sad_groupbox_32_prev_button.move(0, 20)
        self.sad_groupbox_32_prev_button.clicked.connect(self.prev_goods_sequence_number)
        self.sad_groupbox_32_lineedit = QLineEdit(self.sad_groupbox_32)
        self.sad_groupbox_32_lineedit.setValidator(QIntValidator(0, self.number_of_declaraion_goods[
            self.sad_information.key_declaration_dict[self.sequence_number_declaraion]] - 1))
        self.sad_groupbox_32_lineedit.setFixedWidth(45)
        self.sad_groupbox_32_lineedit.setAlignment(Qt.AlignRight)
        self.sad_groupbox_32_lineedit.setText('1')
        self.sad_groupbox_32_lineedit.setStyleSheet('border-radius: 3px;')
        self.sad_groupbox_32_lineedit.textChanged.connect(self.adjust_goods_sequence_number)
        self.sad_groupbox_32_lineedit.move(30, 26)
        self.sad_groupbox_32_next_button = QPushButton('>', self.sad_groupbox_32)
        self.sad_groupbox_32_next_button.setFixedWidth(35)
        self.sad_groupbox_32_next_button.move(70, 20)
        self.sad_groupbox_32_next_button.clicked.connect(self.next_goods_sequence_number)
        self.sad_groupbox_32_jump_button = QPushButton('jump', self.sad_groupbox_32)
        self.sad_groupbox_32_jump_button.setFixedWidth(60)
        self.sad_groupbox_32_jump_button.move(95, 20)
        self.sad_groupbox_32_jump_button.clicked.connect(self.jump_to_goods_sequence_number)

        self.sad_groupbox_33 = QGroupBox(main_widget)
        self.sad_groupbox_33.setGeometry(710, 647, 350, 53)
        self.sad_groupbox_33.setStyleSheet(
            'QGroupBox {border: 1px solid #222;}')
        # Kod towaru
        self.sad_groupbox_33_label1 = QLabel('33 Kod towaru', self.sad_groupbox_33)
        self.sad_groupbox_33_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_33_label1.move(5, 1)
        self.sad_groupbox_33_label2 = QLabel('', self.sad_groupbox_33)
        self.sad_groupbox_33_label2.setGeometry(15, 15, 200, 38)
        self.sad_groupbox_33_label3 = QLabel('', self.sad_groupbox_33)
        self.sad_groupbox_33_label3.setGeometry(230, 15, 105, 38)

        self.sad_groupbox_34 = QGroupBox(main_widget)
        self.sad_groupbox_34.setGeometry(710, 700, 116, 53)
        self.sad_groupbox_34.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # Kod kraju poch.
        self.sad_groupbox_34_label1 = QLabel('34 Kod kraju poch.', self.sad_groupbox_34)
        self.sad_groupbox_34_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_34_label1.move(5, 1)
        self.sad_groupbox_34_label2 = QLabel('', self.sad_groupbox_34)
        self.sad_groupbox_34_label2.setGeometry(0, 15, 116, 38)
        self.sad_groupbox_34_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_35 = QGroupBox(main_widget)
        self.sad_groupbox_35.setGeometry(826, 700, 117, 53)
        self.sad_groupbox_35.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # Masa bnuitto (kg)
        self.sad_groupbox_35_label1 = QLabel('35 Masa bnuitto (kg)', self.sad_groupbox_35)
        self.sad_groupbox_35_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_35_label1.move(5, 1)
        self.sad_groupbox_35_label2 = QLabel('', self.sad_groupbox_35)
        self.sad_groupbox_35_label2.setGeometry(0, 15, 117, 38)
        self.sad_groupbox_35_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_36 = QGroupBox(main_widget)
        self.sad_groupbox_36.setGeometry(943, 700, 117, 53)
        self.sad_groupbox_36.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-top: none;}')
        # Preferencje
        self.sad_groupbox_36_label1 = QLabel('36 Preferencje', self.sad_groupbox_36)
        self.sad_groupbox_36_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_36_label1.move(5, 1)
        self.sad_groupbox_36_label2 = QLabel('', self.sad_groupbox_36)
        self.sad_groupbox_36_label2.setGeometry(0, 15, 117, 38)
        self.sad_groupbox_36_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_37 = ClickableGroupBox(main_widget)
        self.sad_groupbox_37.setGeometry(710, 753, 116, 53)
        self.sad_groupbox_37.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        if not self.if_sent:
            self.sad_groupbox_37.clicked.connect(lambda: self.open_input_sad_information_dialog(4))
        # PROCEDURA
        self.sad_groupbox_37_label1 = QLabel('37 PROCEDURA', self.sad_groupbox_37)
        self.sad_groupbox_37_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_37_label1.move(5, 1)
        self.sad_groupbox_37_label2 = QLabel('', self.sad_groupbox_37)
        self.sad_groupbox_37_label2.setGeometry(0, 15, 70, 38)
        self.sad_groupbox_37_label2.setAlignment(Qt.AlignCenter)
        self.sad_groupbox_37_label2.setStyleSheet("border: 1px solid #222; border-top: none;")
        # 创建 QScrollArea
        self.sad_groupbox_37_scroll_area = QScrollArea(self.sad_groupbox_37)
        self.sad_groupbox_37_scroll_area.setGeometry(80, 15, 35, 37)
        self.sad_groupbox_37_scroll_area.setWidgetResizable(True)  # 设置为可调整大小
        # 隐藏 QScrollArea 的边框
        self.sad_groupbox_37_scroll_area.setStyleSheet("QScrollArea { border: none; }")
        # 创建 QLabel
        self.sad_groupbox_37_label3 = QLabel('', self.sad_groupbox_37_scroll_area)
        self.sad_groupbox_37_label3.setStyleSheet("font-size: 11px;")
        # 设置 QLabel 的属性
        self.sad_groupbox_37_label3.setWordWrap(True)  # 自动换行
        # 将 QLabel 添加到 QScrollArea
        self.sad_groupbox_37_scroll_area.setWidget(self.sad_groupbox_37_label3)

        self.sad_groupbox_38 = QGroupBox(main_widget)
        self.sad_groupbox_38.setGeometry(826, 753, 117, 53)
        self.sad_groupbox_38.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # Masa netta (kg)
        self.sad_groupbox_38_label1 = QLabel('38 Masa netta (kg)', self.sad_groupbox_38)
        self.sad_groupbox_38_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_38_label1.move(5, 1)
        self.sad_groupbox_38_label2 = QLabel('', self.sad_groupbox_38)
        self.sad_groupbox_38_label2.setGeometry(0, 15, 117, 38)
        self.sad_groupbox_38_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_39 = QGroupBox(main_widget)
        self.sad_groupbox_39.setGeometry(943, 753, 117, 53)
        self.sad_groupbox_39.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        # Kontyngent
        self.sad_groupbox_39_label1 = QLabel('39 Kontyngent', self.sad_groupbox_39)
        self.sad_groupbox_39_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_39_label1.move(5, 1)
        self.sad_groupbox_39_label2 = QLabel('', self.sad_groupbox_39)
        self.sad_groupbox_39_label2.setGeometry(0, 15, 117, 38)
        self.sad_groupbox_39_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_40 = ClickableGroupBox(main_widget)
        self.sad_groupbox_40.setGeometry(710, 806, 350, 53)
        self.sad_groupbox_40.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        if not self.if_sent:
            self.sad_groupbox_40.clicked.connect(lambda: self.open_input_sad_information_dialog(3))
        # 创建标签并设置样式
        self.sad_groupbox_40_label1 = QLabel('40 Deklaracja skrÃcona /Poprzedni dokument', self.sad_groupbox_40)
        self.sad_groupbox_40_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_40_label1.move(5, 1)
        # 创建第二个标签
        self.sad_groupbox_40_label2 = QLabel()  # 确保有足够的内容来测试滚动
        self.sad_groupbox_40_label2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.sad_groupbox_40_label2.setWordWrap(True)
        # 创建 QScrollArea
        self.sad_groupbox_40_label2_scroll_area = QScrollArea(self.sad_groupbox_40)
        self.sad_groupbox_40_label2_scroll_area.setGeometry(15, 15, 320, 35)  # 设置位置和大小
        self.sad_groupbox_40_label2_scroll_area.setWidget(self.sad_groupbox_40_label2)
        self.sad_groupbox_40_label2_scroll_area.setWidgetResizable(True)  # 允许调整大小
        self.sad_groupbox_40_label2_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        self.sad_groupbox_40_label2_scroll_area.setStyleSheet('border: none;')  # 去掉边框

        self.sad_groupbox_41 = QGroupBox(main_widget)
        self.sad_groupbox_41.setGeometry(710, 859, 170, 53)
        self.sad_groupbox_41.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        self.sad_groupbox_41.raise_()
        # 补充计量单位
        self.sad_groupbox_41_label1 = QLabel('41\t Uzupelniajaca\n\t jednostka miary', self.sad_groupbox_41)
        self.sad_groupbox_41_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_41_label1.move(5, 1)
        self.sad_groupbox_41_label2 = QLabel('', self.sad_groupbox_41)
        self.sad_groupbox_41_label2.setGeometry(15, 15, 140, 38)

        self.sad_groupbox_42 = QGroupBox(main_widget)
        self.sad_groupbox_42.setGeometry(880, 859, 120, 53)
        self.sad_groupbox_42.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-right: none; border-top: none;}')
        # 物品价值
        self.sad_groupbox_42_label1 = QLabel('42 WNartosc pozycj', self.sad_groupbox_42)
        self.sad_groupbox_42_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_42_label1.move(5, 1)
        self.sad_groupbox_42_label2 = QLabel('', self.sad_groupbox_42)
        self.sad_groupbox_42_label2.setGeometry(0, 15, 120, 38)
        self.sad_groupbox_42_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_43 = QGroupBox(main_widget)
        self.sad_groupbox_43.setGeometry(1000, 859, 60, 53)
        self.sad_groupbox_43.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-top: none;}')
        # Kod
        self.sad_groupbox_43_label1 = QLabel('43 Kod', self.sad_groupbox_43)
        self.sad_groupbox_43_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_43_label1.move(5, 1)
        self.sad_groupbox_43_label2 = QLabel('', self.sad_groupbox_43)
        self.sad_groupbox_43_label2.setGeometry(0, 15, 60, 38)
        self.sad_groupbox_43_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_44 = ClickableGroupBox(main_widget)
        self.sad_groupbox_44.setGeometry(10, 887, 870, 131)
        self.sad_groupbox_44.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top:none;}')
        if not self.if_sent:
            self.sad_groupbox_44.clicked.connect(lambda: self.open_input_sad_information_dialog(3))
        # Dodatkowwe infomacje/Zalaczone dokumenty/Swiadectwa i pozwolenia
        self.sad_groupbox_44_label1 = QLabel('44 Dodatkowwe infomacje/Zalaczone dokumenty/Swiadectwa i pozwolenia',
                                             self.sad_groupbox_44)
        self.sad_groupbox_44_label1.setStyleSheet("font-size: 11px; border: 1px solid #222; border-top: none;")
        self.sad_groupbox_44_label1.setGeometry(0, 0, 91, 131)
        self.sad_groupbox_44_label1.setWordWrap(True)
        self.sad_groupbox_44_label1.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # 创建第二个标签
        self.sad_groupbox_44_label2 = QLabel()  # 确保有足够的内容来测试滚动
        self.sad_groupbox_44_label2.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.sad_groupbox_44_label2.setWordWrap(True)
        # 创建 QScrollArea
        self.sad_groupbox_44_label2_scroll_area = QScrollArea(self.sad_groupbox_44)
        self.sad_groupbox_44_label2_scroll_area.setGeometry(100, 10, 490, 111)  # 设置位置和大小
        self.sad_groupbox_44_label2_scroll_area.setWidget(self.sad_groupbox_44_label2)
        self.sad_groupbox_44_label2_scroll_area.setWidgetResizable(True)  # 允许调整大小
        self.sad_groupbox_44_label2_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        self.sad_groupbox_44_label2_scroll_area.setStyleSheet('border: none;')  # 去掉边框

        self.sad_groupbox_KodDI = QGroupBox(main_widget)
        self.sad_groupbox_KodDI.setGeometry(880, 912, 60, 53)
        self.sad_groupbox_KodDI.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-top: none; border-bottom: none; border-right: none;}')
        # Korekta
        self.sad_groupbox_KodDI_label1 = QLabel('Kod D.I.', self.sad_groupbox_KodDI)
        self.sad_groupbox_KodDI_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_KodDI_label1.move(5, 1)
        self.sad_groupbox_KodDI_label2 = QLabel('', self.sad_groupbox_KodDI)
        self.sad_groupbox_KodDI_label2.setGeometry(0, 15, 60, 38)
        self.sad_groupbox_KodDI_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_PLN = QGroupBox(main_widget)
        self.sad_groupbox_PLN.setGeometry(700, 965, 180, 53)
        self.sad_groupbox_PLN.setStyleSheet(
            'QGroupBox {border: 1px dashed #222; border-right: none; border-bottom: none;}')
        # Wartość statystyczna
        self.sad_groupbox_PLN_label1 = QLabel('', self.sad_groupbox_PLN)
        self.sad_groupbox_PLN_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_PLN_label1.move(5, 1)
        self.sad_groupbox_PLN_label2 = QLabel('PLN', self.sad_groupbox_PLN)
        self.sad_groupbox_PLN_label2.setGeometry(15, 15, 150, 38)

        self.sad_groupbox_45 = QGroupBox(main_widget)
        self.sad_groupbox_45.setGeometry(940, 912, 120, 53)
        self.sad_groupbox_45.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-bottom: none;}')
        # Korekta
        self.sad_groupbox_45_label1 = QLabel('45 Korekta', self.sad_groupbox_45)
        self.sad_groupbox_45_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_45_label1.move(5, 1)
        self.sad_groupbox_45_label2 = QLabel('', self.sad_groupbox_45)
        self.sad_groupbox_45_label2.setGeometry(15, 15, 90, 38)

        self.sad_groupbox_46 = QGroupBox(main_widget)
        self.sad_groupbox_46.setGeometry(880, 965, 180, 53)
        self.sad_groupbox_46.setStyleSheet('QGroupBox {border: 1px solid #222;}')
        # 统计值
        self.sad_groupbox_46_label1 = QLabel('46 Wartość statystyczna', self.sad_groupbox_46)
        self.sad_groupbox_46_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_46_label1.move(5, 1)
        self.sad_groupbox_46_label2 = QLabel('', self.sad_groupbox_46)
        self.sad_groupbox_46_label2.setGeometry(15, 15, 150, 38)

        self.sad_groupbox_AIS = ClickableGroupBox(main_widget)
        self.sad_groupbox_AIS.setGeometry(43, 1018, 1017, 60)
        self.sad_groupbox_AIS.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-top:none; border-bottom: none;}')
        if not self.if_sent:
            self.sad_groupbox_AIS.clicked.connect(lambda: self.open_input_sad_information_dialog(3))
        # Dodatkowwe infomacje/Zalaczone dokumenty/Swiadectwa i pozwolenia
        self.sad_groupbox_AIS_label1 = QLabel('AIS', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label1.setStyleSheet(
            "font-size: 25px; border: 1px solid #222; border-top: none; border-bottom: none;")
        self.sad_groupbox_AIS_label1.setGeometry(0, 0, 58, 60)
        # 创建第二个标签
        self.sad_groupbox_AIS_label2 = QLabel('Zabe pieczania', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label2.setGeometry(58, 0, 60, 60)
        self.sad_groupbox_AIS_label2.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border: none;")
        self.sad_groupbox_AIS_label2.setWordWrap(True)
        self.sad_groupbox_AIS_label3 = QLabel('', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label3.setGeometry(118, 0, 540, 60)
        self.sad_groupbox_AIS_label3.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-left: none; border-bottom: none;")
        self.sad_groupbox_AIS_label3.setWordWrap(True)
        self.sad_groupbox_AIS_label4 = QLabel('Odniesienia podatkowe', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label4.setGeometry(658, 0, 70, 60)
        self.sad_groupbox_AIS_label4.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_AIS_label4.setWordWrap(True)
        self.sad_groupbox_AIS_label5 = QLabel('VAT: IM2760089575 Rola: FR5', self.sad_groupbox_AIS)
        self.sad_groupbox_AIS_label5.setGeometry(728, 0, 300, 60)
        self.sad_groupbox_AIS_label5.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_AIS_label5.setWordWrap(True)

        self.sad_groupbox_47 = QGroupBox(main_widget)
        self.sad_groupbox_47.setGeometry(10, 1078, 590, 240)
        self.sad_groupbox_47.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        # Obliczanie oplat
        self.sad_groupbox_47_label1 = QLabel('47 Obliczanie oplat', self.sad_groupbox_47)
        self.sad_groupbox_47_label1.setStyleSheet("font-size: 11px; border: 1px solid #222; border-top: none;")
        self.sad_groupbox_47_label1.setGeometry(0, 0, 91, 240)
        self.sad_groupbox_47_label1.setWordWrap(True)
        self.sad_groupbox_47_label1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label2 = QLabel('Typ', self.sad_groupbox_47)
        self.sad_groupbox_47_label2.setGeometry(90, 0, 50, 20)
        self.sad_groupbox_47_label2.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label3 = QLabel('Podstawa oplaty', self.sad_groupbox_47)
        self.sad_groupbox_47_label3.setGeometry(140, 0, 140, 20)
        self.sad_groupbox_47_label3.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label4 = QLabel('Stawka', self.sad_groupbox_47)
        self.sad_groupbox_47_label4.setGeometry(280, 0, 140, 20)
        self.sad_groupbox_47_label4.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label5 = QLabel('Kwota', self.sad_groupbox_47)
        self.sad_groupbox_47_label5.setGeometry(420, 0, 140, 20)
        self.sad_groupbox_47_label5.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label6 = QLabel('MP', self.sad_groupbox_47)
        self.sad_groupbox_47_label6.setGeometry(560, 0, 30, 20)
        self.sad_groupbox_47_label6.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label7 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label7.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label7.setGeometry(90, 20, 50, 200)
        self.sad_groupbox_47_label7.setWordWrap(True)
        self.sad_groupbox_47_label7.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label8 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label8.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label8.setGeometry(140, 20, 140, 200)
        self.sad_groupbox_47_label8.setWordWrap(True)
        self.sad_groupbox_47_label8.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label9 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label9.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label9.setGeometry(280, 20, 140, 200)
        self.sad_groupbox_47_label9.setWordWrap(True)
        self.sad_groupbox_47_label9.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label10 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label10.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label10.setGeometry(280, 20, 140, 200)
        self.sad_groupbox_47_label10.setWordWrap(True)
        self.sad_groupbox_47_label10.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label11 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label11.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label11.setGeometry(420, 20, 140, 200)
        self.sad_groupbox_47_label11.setWordWrap(True)
        self.sad_groupbox_47_label11.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label12 = QLabel('', self.sad_groupbox_47)
        self.sad_groupbox_47_label12.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-right: none;")
        self.sad_groupbox_47_label12.setGeometry(560, 20, 30, 200)
        self.sad_groupbox_47_label12.setWordWrap(True)
        self.sad_groupbox_47_label12.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_47_label13 = QLabel('Razem:', self.sad_groupbox_47)
        self.sad_groupbox_47_label13.setGeometry(90, 220, 500, 20)
        self.sad_groupbox_47_label13.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_47_label13.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_48 = QGroupBox(main_widget)
        self.sad_groupbox_48.setGeometry(600, 1078, 230, 53)
        self.sad_groupbox_48.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none;}')
        # Płatność\' odroczona
        self.sad_groupbox_48_label1 = QLabel('48 Płatność\' odroczona', self.sad_groupbox_48)
        self.sad_groupbox_48_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_48_label1.move(5, 1)
        self.sad_groupbox_48_label2 = QLabel('', self.sad_groupbox_48)
        self.sad_groupbox_48_label2.setGeometry(15, 15, 200, 38)

        self.sad_groupbox_49 = QGroupBox(main_widget)
        self.sad_groupbox_49.setGeometry(830, 1078, 230, 53)
        self.sad_groupbox_49.setStyleSheet('QGroupBox {border: 1px solid #222;}')
        # Oznaczenie skladu
        self.sad_groupbox_49_label1 = QLabel('49 Oznaczenie skladu', self.sad_groupbox_49)
        self.sad_groupbox_49_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_49_label1.move(5, 1)
        self.sad_groupbox_49_label2 = QLabel('', self.sad_groupbox_49)
        self.sad_groupbox_49_label2.setGeometry(15, 15, 200, 38)

        self.sad_groupbox_B = QGroupBox(main_widget)
        self.sad_groupbox_B.setGeometry(600, 1131, 460, 187)
        self.sad_groupbox_B.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        # ELEMENTY KALKULACYJNE
        self.sad_groupbox_B_label1 = QLabel('B ELEMENTY KALKULACYJNE', self.sad_groupbox_B)
        self.sad_groupbox_B_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_B_label1.move(5, 1)
        self.sad_groupbox_B_label2 = QLabel('24PL44302B00ZVF3R8', self.sad_groupbox_B)
        self.sad_groupbox_B_label2.move(180, 1)
        self.sad_groupbox_B_label3 = QLabel('', self.sad_groupbox_B)
        self.sad_groupbox_B_label3.setGeometry(15, 15, 430, 187)
        self.sad_groupbox_B_label3.setWordWrap(True)
        self.sad_groupbox_B_label3.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.sad_groupbox_50 = QGroupBox(main_widget)
        self.sad_groupbox_50.setGeometry(100, 1318, 640, 200)
        self.sad_groupbox_50.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-right: none;}')
        # Glowny zobowiazany
        self.sad_groupbox_50_label1 = QLabel('50 Glowny zobowiazany', self.sad_groupbox_50)
        self.sad_groupbox_50_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_50_label1.move(5, 1)
        self.sad_groupbox_50_label2 = QLabel('Nr', self.sad_groupbox_50)
        self.sad_groupbox_50_label2.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_50_label2.move(220, 1)
        self.sad_groupbox_50_label3 = QLabel('Podpis:', self.sad_groupbox_50)
        self.sad_groupbox_50_label3.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_50_label3.move(450, 1)
        self.sad_groupbox_50_label4 = QLabel('', self.sad_groupbox_50)
        self.sad_groupbox_50_label4.setGeometry(15, 15, 610, 140)
        self.sad_groupbox_50_label4.setWordWrap(True)
        self.sad_groupbox_50_label4.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_50_label5 = QLabel('reprezentowany przez', self.sad_groupbox_50)
        self.sad_groupbox_50_label5.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_50_label5.move(40, 160)
        self.sad_groupbox_50_label6 = QLabel('Miejsce i data:', self.sad_groupbox_50)
        self.sad_groupbox_50_label6.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_50_label6.move(40, 180)

        self.sad_groupbox_C = QGroupBox(main_widget)
        self.sad_groupbox_C.setGeometry(740, 1318, 320, 200)
        self.sad_groupbox_C.setStyleSheet('QGroupBox {border: 1px dashed #222; border-top: none;}')
        # URZAD WYJSCIA
        self.sad_groupbox_C_label1 = QLabel('C URZAD WYJSCIA', self.sad_groupbox_C)
        self.sad_groupbox_C_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_C_label1.move(5, 1)
        self.sad_groupbox_C_label2 = QLabel('', self.sad_groupbox_C)
        self.sad_groupbox_C_label2.setGeometry(15, 15, 290, 38)

        self.sad_groupbox_51 = QGroupBox(main_widget)
        self.sad_groupbox_51.setGeometry(10, 1471, 1050, 100)
        self.sad_groupbox_51.setStyleSheet('QGroupBox {border: 1px solid #222; border-right: none; border-top:none;}')
        # Przewidywane urzędy tranzytowe(i kraj)
        self.sad_groupbox_51_label1 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label1.setStyleSheet("font-size: 11px; border: 1px solid #222; border-right: none;")
        self.sad_groupbox_51_label1.setGeometry(0, 0, 91, 100)
        self.sad_groupbox_51_label1.setWordWrap(True)
        self.sad_groupbox_51_label1.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label2 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label2.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none; border-right: none;")
        self.sad_groupbox_51_label2.setGeometry(90, 50, 160, 50)
        self.sad_groupbox_51_label2.setWordWrap(True)
        self.sad_groupbox_51_label2.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label3 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label3.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none; border-right: none;")
        self.sad_groupbox_51_label3.setGeometry(250, 50, 160, 50)
        self.sad_groupbox_51_label3.setWordWrap(True)
        self.sad_groupbox_51_label3.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label4 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label4.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none; border-right: none;")
        self.sad_groupbox_51_label4.setGeometry(410, 50, 160, 50)
        self.sad_groupbox_51_label4.setWordWrap(True)
        self.sad_groupbox_51_label4.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label5 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label5.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none; border-right: none;")
        self.sad_groupbox_51_label5.setGeometry(570, 50, 160, 50)
        self.sad_groupbox_51_label5.setWordWrap(True)
        self.sad_groupbox_51_label5.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label6 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label6.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none; border-right: none;")
        self.sad_groupbox_51_label6.setGeometry(730, 50, 160, 50)
        self.sad_groupbox_51_label6.setWordWrap(True)
        self.sad_groupbox_51_label6.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_51_label7 = QLabel('51 Przewidywane urzędy tranzytowe(i kraj)', self.sad_groupbox_51)
        self.sad_groupbox_51_label7.setStyleSheet(
            "font-size: 11px; border: 1px solid #222; border-top: none; border-bottom:none;")
        self.sad_groupbox_51_label7.setGeometry(890, 50, 160, 50)
        self.sad_groupbox_51_label7.setWordWrap(True)
        self.sad_groupbox_51_label7.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.sad_groupbox_52 = QGroupBox(main_widget)
        self.sad_groupbox_52.setGeometry(10, 1571, 730, 53)
        self.sad_groupbox_52.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-right: none;}')
        # Gwarancja
        self.sad_groupbox_52_label1 = QLabel('52 Gwarancja', self.sad_groupbox_52)
        self.sad_groupbox_52_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_52_label1.move(5, 1)
        self.sad_groupbox_52_label2 = QLabel('', self.sad_groupbox_52)
        self.sad_groupbox_52_label2.setGeometry(15, 15, 150, 38)

        self.sad_groupbox_Kod = QGroupBox(main_widget)
        self.sad_groupbox_Kod.setGeometry(700, 1571, 40, 53)
        self.sad_groupbox_Kod.setStyleSheet(
            'QGroupBox {border: 1px solid #222; border-top: none; border-bottom: none; border-right: none;}')
        # Kod
        self.sad_groupbox_Kod_label1 = QLabel('Kod', self.sad_groupbox_Kod)
        self.sad_groupbox_Kod_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_Kod_label1.move(5, 1)
        self.sad_groupbox_Kod_label2 = QLabel('', self.sad_groupbox_Kod)
        self.sad_groupbox_Kod_label2.setGeometry(0, 15, 40, 38)
        self.sad_groupbox_Kod_label2.setAlignment(Qt.AlignCenter)

        self.sad_groupbox_53 = QGroupBox(main_widget)
        self.sad_groupbox_53.setGeometry(740, 1571, 320, 53)
        self.sad_groupbox_53.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        # Urzad przeznaczenia (i kraj)
        self.sad_groupbox_53_label1 = QLabel('53 Urzad przeznaczenia (i kraj)', self.sad_groupbox_53)
        self.sad_groupbox_53_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_53_label1.move(5, 1)
        self.sad_groupbox_53_label2 = QLabel('', self.sad_groupbox_53)
        self.sad_groupbox_53_label2.setGeometry(15, 15, 290, 38)

        self.sad_groupbox_J = QGroupBox(main_widget)
        self.sad_groupbox_J.setGeometry(10, 1624, 690, 180)
        self.sad_groupbox_J.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none; border-right: none;}')
        # KONTROLAPRZEZ URZAD PRZEZNACZENIA
        self.sad_groupbox_J_label1 = QLabel('J KONTROLAPRZEZ URZAD PRZEZNACZENIA', self.sad_groupbox_J)
        self.sad_groupbox_J_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_J_label1.move(5, 1)
        self.sad_groupbox_J_label2 = QLabel('', self.sad_groupbox_J)
        self.sad_groupbox_J_label2.setGeometry(15, 15, 660, 140)
        self.sad_groupbox_J_label2.setWordWrap(True)
        self.sad_groupbox_J_label2.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sad_groupbox_J_label2 = QLabel('', self.sad_groupbox_J)
        self.sad_groupbox_J_label2.move(40, 155)

        self.sad_groupbox_54 = QGroupBox(main_widget)
        self.sad_groupbox_54.setGeometry(700, 1624, 360, 180)
        self.sad_groupbox_54.setStyleSheet('QGroupBox {border: 1px solid #222; border-top: none;}')
        # Miejsce i data:
        self.sad_groupbox_54_label1 = QLabel('54 Miejsce i data:', self.sad_groupbox_54)
        self.sad_groupbox_54_label1.setStyleSheet("font-size: 11px;")
        self.sad_groupbox_54_label1.move(5, 1)
        # self.sad_groupbox_54_label2 = QLabel('WARSZAWA 2024-06-04', self.sad_groupbox_54)
        # self.sad_groupbox_54_label2.setGeometry(15, 15, 330, 15)
        # self.sad_groupbox_54_label3 = QLabel('Podpis i nazwisko zglaszajacego / przedstawiciela', self.sad_groupbox_54)
        # self.sad_groupbox_54_label3.setGeometry(15, 35, 330, 15)
        # self.sad_groupbox_54_label4 = QLabel('ZABROCKI TOMASZ', self.sad_groupbox_54)
        # self.sad_groupbox_54_label4.setGeometry(15, 55, 330, 15)
        # self.sad_groupbox_54_label5 = QLabel('+48698156094', self.sad_groupbox_54)
        # self.sad_groupbox_54_label5.setGeometry(15, 75, 330, 15)
        # self.sad_groupbox_54_label6 = QLabel('Tomasz.Zabrocki@gmail.com', self.sad_groupbox_54)
        # self.sad_groupbox_54_label6.setGeometry(15, 95, 330, 15)
        # self.sad_groupbox_54_label7 = QLabel(
        #     'Karte 8 otrzymatem, zostatem powiadomionyo kwocie naleznosci wynikajacej z dtugu celnego',
        #     self.sad_groupbox_54)
        # self.sad_groupbox_54_label7.setGeometry(40, 116, 305, 30)
        # self.sad_groupbox_54_label7.setWordWrap(True)
        # self.sad_groupbox_54_label7.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # self.xml_generate_btn_groupbox = QGroupBox(main_widget)
        # self.xml_generate_btn_groupbox.setGeometry(1080, 10, 120, 40)
        # self.xml_generate_btn_groupbox.setStyleSheet('QGroupBox {border: none;}')
        # self.xml_generate_btn = QPushButton("generate xml file", self.xml_generate_btn_groupbox)
        # self.xml_generate_btn.setStyleSheet("background: #3d8649; border-radius: 6px; color: #fff;")
        # self.xml_generate_btn.setGeometry(0, 5, 120, 20)
        # self.xml_generate_btn.clicked.connect(self.generate_xml)

        # 创建一个布局并将滚动区域添加到该布局中
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)

        # 设置对话框的布局
        self.setLayout(layout)

        # 确定和取消按钮
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.refresh_button_styles()

        # 将按钮框添加到main_widget
        self.buttons.setParent(main_widget)

        # 设置按钮框的位置到右上角
        self.buttons.move(main_widget.width() - self.buttons.sizeHint().width() - 10, 10)

        # 保证窗口大小变化时按钮框依然保持在右上角
        main_widget.resizeEvent = lambda event: self.buttons.move(
            main_widget.width() - self.buttons.sizeHint().width() - 10, 10)

    def update_data(self):
        input_information = self.sad_information.input_information
        # print(input_information)
        data_rows = self.sad_information.data_rows
        # print(data_rows)
        row = data_rows[
            self.sad_information.declaration_dict[
                self.sad_information.key_declaration_dict[self.sequence_number_declaraion]][
                self.sequene_number_goods]]
        # print(row)

        self.sad_groupbox_1_label2.setText(input_information['LRN'])
        self.sad_groupbox_1_label3.setText(input_information['additional declaration type'])
        self.sad_groupbox_1_label4.setText(input_information['customs office referenceNumber'])

        text_sad_groupbox_2 = ''
        text_sad_groupbox_2 = self.add_text(text_sad_groupbox_2, 'ConsignorName', row)
        text_sad_groupbox_2 = self.add_text(text_sad_groupbox_2, 'ConsignorStreetAndNr', row)
        text_sad_groupbox_2 = self.add_text(text_sad_groupbox_2, 'ConsignorPostcode', row)
        text_sad_groupbox_2 = self.add_text(text_sad_groupbox_2, 'ConsignorCity', row)
        text_sad_groupbox_2 = self.add_text(text_sad_groupbox_2, 'ConsignorCountry', row)
        self.sad_groupbox_2_label4.setText(text_sad_groupbox_2)

        text_sad_groupbox_8_label4 = '\n'.join(
            f'{k}: {v}' for k, v in
            self.sad_information.information_declaration[self.sequence_number_declaraion].items())
        self.sad_groupbox_8_label4.setText(text_sad_groupbox_8_label4)

        if input_information['contact person']:
            text_sad_groupbox_14 = self.format_dict_list(input_information['contact person'])
            self.sad_groupbox_14_label4.setText(text_sad_groupbox_14)

        self.sad_groupbox_22_label3.setText(str(row['Total Price']))

        text_sad_groupbox_29 = input_information['customs office referenceNumber']
        self.sad_groupbox_29_label2.setText(text_sad_groupbox_29)

        text_sad_groupbox_30 = input_information['unLocode'] + input_information['authorisation number']
        self.sad_groupbox_30_label2.setText(text_sad_groupbox_30)

        # sad_groupbox_31_label3
        self.update_goods_information()

        self.sad_groupbox_33_label2.setText(str(row['CountryOriginCode']))
        self.sad_groupbox_34_label2.setText(str(row['CountryOriginCode']))
        self.sad_groupbox_35_label2.setText(str(row['GrossMassKg']))

        procedures = input_information.get('goodsitem additional procedure', [])
        # 提取 'additional procedure(CL457)' 值，并组成字符串，每个值换行
        sad_groupbox_37_label3_text = "\n".join(item.get('additional procedure(CL457)', '') for item in procedures)
        self.sad_groupbox_37_label3.setText(sad_groupbox_37_label3_text)


        self.sad_groupbox_38_label2.setText(str(row['GrossMassKg']))

        if input_information['goodshipment previous document']:
            text_sad_groupbox_40 = self.format_dict_list(input_information['goodshipment previous document'])
            self.sad_groupbox_40_label2.setText(text_sad_groupbox_40)

        self.sad_groupbox_42_label2.setText(str(row['Total Price']))

        text_sad_groupbox_44 = ''
        if input_information['goodshipment additional information']:
            text = self.format_dict_list(input_information['goodshipment additional information'])
            text_sad_groupbox_44 += 'goodshipment transport document: \n' + text
        if input_information['goodshipment supporting document']:
            text = self.format_dict_list(input_information['goodshipment supporting document'])
            text_sad_groupbox_44 += 'goodshipment supporting document: \n' + text
        if len(input_information['goodshipment additional reference']) > 0:
            if input_information['goodshipment additional reference']:
                text = self.format_dict_list(input_information['goodshipment additional reference'])
                text_sad_groupbox_44 += 'goodshipment additional reference: \n' + text
        elif len(self.goodshipment_CL380) > 0:
            text = self.format_dict_list(self.goodshipment_CL380)
            text_sad_groupbox_44 += 'goodshipment additional reference: \n' + text
        if input_information['goodshipment transport document']:
            text = self.format_dict_list(input_information['goodshipment transport document'])
            text_sad_groupbox_44 += 'goodshipment transport document: \n' + text
        self.sad_groupbox_44_label2.setText(text_sad_groupbox_44)

        role_data = self.sad_information.input_information['goodshipment additional fiscal reference']
        print(role_data)
        roles = ','.join(item['role(CL149)'] for item in role_data)
        text_sad_groupbox_AIS_label5 = 'VAT:' + str(row['IOSS']) + ';Rola:' + roles
        self.sad_groupbox_AIS_label5.setText(text_sad_groupbox_AIS_label5)

    def format_dict_list(self, dict_list):
        # 将字典列表中的值格式化为字符串
        formatted_text = ""
        for d in dict_list:
            # 提取每个字典的 value，并用 ',' 分隔
            values_string = ', '.join(str(value) for value in d.values())
            # 将格式化的字符串添加到总文本中，并换行
            formatted_text += f"{values_string}\n"
        return formatted_text

    # def generate_xml(self):
    #     pass

    def adjust_declaration_sequence_number(self):
        value = self.sad_groupbox_8_lineedit.text()
        max_value = self.number_of_declaraion
        if value:
            if int(value) > max_value:
                self.sad_groupbox_8_lineedit.setText(str(max_value))
            elif int(value) < 1:
                self.sad_groupbox_8_lineedit.setText('1')

    def prev_declaration_sequence_number(self):
        self.sequence_number_declaraion -= 1
        if self.sequence_number_declaraion < 0:
            self.sequence_number_declaraion = 0
        self.sad_groupbox_8_lineedit.setText(str(self.sequence_number_declaraion + 1))
        self.adjust_goods_sequence_number_after_clicked_declaration_button()

    def next_declaration_sequence_number(self):
        self.sequence_number_declaraion += 1
        if self.sequence_number_declaraion > self.number_of_declaraion - 1:
            self.sequence_number_declaraion = self.number_of_declaraion - 1
        self.sad_groupbox_8_lineedit.setText(str(self.sequence_number_declaraion + 1))
        self.adjust_goods_sequence_number_after_clicked_declaration_button()

    def jump_to_declaration_sequence_number(self):
        self.sequence_number_declaraion = int(self.sad_groupbox_8_lineedit.text()) - 1
        self.adjust_goods_sequence_number_after_clicked_declaration_button()

    def adjust_goods_sequence_number_after_clicked_declaration_button(self):
        self.sad_groupbox_32_lineedit.setText('1')
        self.sequene_number_goods = 0
        self.update_data()

    def adjust_goods_sequence_number(self):
        value = self.sad_groupbox_32_lineedit.text()
        max_value = self.number_of_declaraion_goods[
            self.sad_information.key_declaration_dict[self.sequence_number_declaraion]]
        if value:
            if int(value) > max_value:
                self.sad_groupbox_32_lineedit.setText(str(max_value))
            elif int(value) < 1:
                self.sad_groupbox_32_lineedit.setText('1')

    def prev_goods_sequence_number(self):
        self.sequene_number_goods -= 1
        if self.sequene_number_goods < 0:
            self.sequene_number_goods = 0
        self.sad_groupbox_32_lineedit.setText(str(self.sequene_number_goods + 1))
        self.update_goods_information()
        self.update_data()

    def next_goods_sequence_number(self):
        self.sequene_number_goods += 1
        max_value = self.number_of_declaraion_goods[
                        self.sad_information.key_declaration_dict[self.sequence_number_declaraion]] - 1
        if self.sequene_number_goods > max_value:
            self.sequene_number_goods = max_value
        self.sad_groupbox_32_lineedit.setText(str(self.sequene_number_goods + 1))
        self.update_goods_information()
        self.update_data()

    def jump_to_goods_sequence_number(self):
        self.sequene_number_goods = int(self.sad_groupbox_32_lineedit.text()) - 1
        self.update_goods_information()
        self.update_data()

    def update_goods_information(self):
        consignee_name = self.sad_information.key_declaration_dict[self.sequence_number_declaraion]
        # print(consignee_name)
        row_number = self.sad_information.declaration_dict[consignee_name][self.sequene_number_goods]
        # print(row_number)
        row = self.sad_information.data_rows[row_number]
        text_sad_groupbox_31 = 'referenceNumberUCR: ' + str(row['TrackingNumber']) + '\n' + 'grossMass: ' + str(
            row['GrossMassKg']) + '\n' + 'descriptionOfGoods: ' + str(row['DescriptionGoods']) + '\n'

        goodsitem_information = self.manual_datas[self.sequene_number_goods]
        keys = ['goodsitem previous_document',
                'goodsitem additional_information',
                'goodsitem supporting_document',
                'goodsitem additional_reference',
                'goodsitem transport_document'
                ]
        dict_goodsitem_information = dict(zip(keys, goodsitem_information))

        if dict_goodsitem_information['goodsitem previous_document']:
            text = self.format_dict_list(dict_goodsitem_information['goodsitem previous_document'])
            text_sad_groupbox_31 += 'goodsitem previous_document: \n' + text
        if dict_goodsitem_information['goodsitem additional_information']:
            text = self.format_dict_list(dict_goodsitem_information['goodsitem additional_information'])
            text_sad_groupbox_31 += 'goodsitem additional_information: \n' + text
        if dict_goodsitem_information['goodsitem supporting_document']:
            text = self.format_dict_list(dict_goodsitem_information['goodsitem supporting_document'])
            text_sad_groupbox_31 += 'goodsitem supporting_document: \n' + text
        if len(self.sad_information.input_information['goodshipment additional reference']) == 0:
            if len(self.goodshipment_CL380) == 0:
                if dict_goodsitem_information['goodsitem additional_reference']:
                    text = self.format_dict_list(dict_goodsitem_information['goodsitem additional_reference'])
                    text_sad_groupbox_31 += 'goodsitem additional_reference: \n' + text
        if dict_goodsitem_information['goodsitem transport_document']:
            text = self.format_dict_list(dict_goodsitem_information['goodsitem transport_document'])
            text_sad_groupbox_31 += 'goodsitem transport_document: \n' + text

        self.sad_groupbox_31_label3.setText(text_sad_groupbox_31)

    def add_text(self, text, key, information):
        if information[key] != '':
            text += key + ': ' + str(information[key]) + '\n'
        return text

    def open_input_sad_information_dialog(self, index):
        self.buttons.button(QDialogButtonBox.Ok).setStyleSheet("color: #222;")
        old_goodsitem_information = self.get_goodsitem_information_from_input_information(
            self.sad_information.input_information)
        dialog = InputSADInformationDialog(index, self.sad_information.input_information, self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            text_input = dialog.get_input_information()
            # print(text_input)
            if text_input:
                # print("#####change#######")
                new_goodsitem_information = self.get_goodsitem_information_from_input_information(text_input)
                self.update_all_goodsitem_information(old_goodsitem_information, new_goodsitem_information)

                self.sad_information.update_input_information(text_input)

                db.update_main_table(self.main_table_id, new_data=text_input)
                # print("修改成功")
        self.refresh_button_styles()
        self.update_data()

    def update_all_goodsitem_information(self, dict1, dict2):
        # 映射字典：将字典中的键名映射到数据库中的字段名
        key_mapping = {
            'goodsitem previous document': 'previous_document',
            'goodsitem additional information': 'additional_information',
            'goodsitem supporting document': 'supporting_document',
            'goodsitem additional reference': 'additional_reference',
            'goodsitem transport document': 'transport_document'
        }

        keys = list(key_mapping.keys())  # 获取字典中的所有键名
        changes = []  # 用于存储变化的键
        for key in keys:
            db_key = key_mapping[key]  # 获取对应的数据库字段名

            # 确保两个字典都包含该关键字
            if key in dict1 and key in dict2:
                if dict1[key] != dict2[key]:
                    # 值发生变化，记录变化的键及其值
                    changes.append((db_key, dict1[key], dict2[key]))  # 记录数据库字段名

        # 如果有变化，更新所有列表中的对应项
        if changes:
            for change in changes:
                db_key, old_value, new_value = change
                # 更新所有列表中的对应项
                # print(self.manual_datas)
                for item in self.manual_datas:
                    # 根据映射关系更新对应的列表
                    if db_key == 'previous_document':
                        item[0] = new_value  # 假设对应的列表索引为0
                    elif db_key == 'additional_information':
                        item[1] = new_value  # 假设对应的列表索引为1
                    elif db_key == 'supporting_document':
                        item[2] = new_value  # 假设对应的列表索引为2
                    elif db_key == 'additional_reference':
                        item[3] = new_value  # 假设对应的列表索引为3
                    elif db_key == 'transport_document':
                        item[4] = new_value  # 假设对应的列表索引为4
                # print(self.manual_datas)

                # 在数据库中更新值
                list_sub_table = db.get_sub_tables_by_main_id(self.main_table_id, self.username)
                sub_tables_id = [item[0] for item in list_sub_table]
                for sub_table_id in sub_tables_id:
                    db.update_all_by_sub_table_id(sub_table_id, db_key, new_value)
                # print(f"Key '{db_key}' has changed: {old_value} -> {new_value}")

    def open_goodsitem_manual_information_dialog(self):
        self.buttons.button(QDialogButtonBox.Ok).setStyleSheet("color: #222;")
        # GoodsitemManualInformation
        goodshipment_information = self.get_goodshipment_information_from_input_information(
            self.sad_information.input_information)

        # self.sequene_number_goods
        row_number = self.sequene_number_goods
        keys = ['goodsitem previous document', 'goodsitem additional information',
                'goodsitem supporting document', 'goodsitem additional reference',
                'goodsitem transport document']
        goodsitem_information = {key: value for key, value in zip(keys, self.manual_datas[row_number])}
        # print(goodsitem_information)

        dialog = GoodsitemManualInformation(0, goodsitem_information, goodshipment_information, self.username, self)

        if dialog.exec_() == QDialog.Accepted:
            text_input = dialog.get_input_information()
            # print(text_input)
            if text_input:
                sequence = self.sequene_number_goods
                sub_table_data_id = self.main_id_for_sub_table_data[sequence]
                print("1111:", sub_table_data_id)
                previous_document = text_input['goodsitem previous document']
                additional_information = text_input['goodsitem additional information']
                supporting_document = text_input['goodsitem supporting document']
                additional_reference = text_input['goodsitem additional reference']
                transport_document = text_input['goodsitem transport document']
                db.update_sub_table_data(sub_table_data_id, previous_document=previous_document,
                                         additional_information=additional_information,
                                         supporting_document=supporting_document,
                                         additional_reference=additional_reference,
                                         transport_document=transport_document)
                self.manual_datas[sequence] = [previous_document, additional_information, supporting_document,
                                               additional_reference, transport_document]
                # self.sad_information.update_input_information(text_input)
                # db.update_main_table(self.main_table_id, new_data=text_input)
                # print("修改成功")
        self.refresh_button_styles()
        self.update_data()

    def get_goodshipment_information_from_input_information(self, input_information):
        keys_to_extract = ['goodshipment previous document', 'goodshipment additional information',
                           'goodshipment supporting document', 'goodshipment additional reference',
                           'goodshipment transport document']
        goodshipment_information = {key: input_information[key] for key in keys_to_extract if key in input_information}
        return goodshipment_information

    def get_goodsitem_information_from_input_information(self, input_information):
        keys_to_extract = ['goodsitem previous document', 'goodsitem additional information',
                           'goodsitem supporting document', 'goodsitem additional reference',
                           'goodsitem transport document']
        goodshipment_information = {key: input_information[key] for key in keys_to_extract if key in input_information}
        return goodshipment_information

    def refresh_button_styles(self):
        # self.buttons.button(QDialogButtonBox.Ok).setStyleSheet("color: #fff;")
        pass

    def get_some_return_information(self):
        return_list = []
        return_list.append("detail_dialog")
        return return_list


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # a = {'LRN': '1', 'additional declaration type': 'A', 'customs office referenceNumber': 'PL443020',
    #      'declarant name': '', 'declarant identification number': 'PL521398303500000',
    #      'declarant street and number': '', 'declarant postcode': '', 'declarant city': '', 'declarant country': '',
    #      'contact person': [
    #          {'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094', 'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
    #      'representative identification number': '', 'representative status': '3', 'representative contact person': [
    #         {'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094', 'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
    #      'customs office reference number': '', 'type of location': 'B', 'qualifier of identification': 'Y',
    #      'unLocode': '', 'authorisation number': 'PLTST441000200001', 'additional identifier': '', 'latitude': '',
    #      'longitude': '', 'EORI Number': '', 'address street and number': '', 'address postcode': '',
    #      'address city': '', 'address country': '', 'postcode address postcode': '',
    #      'postcode address house number': '', 'postcode address country': '', 'goodshipment referenceNumberUCR': '',
    #      'goodshipment previous document': [
    #          {'reference number': '12345', 'type(CL214)': 'N271', 'goodsItem identifier': '643'}],
    #      'goodshipment additional information': [],
    #      'goodshipment supporting document': [{'reference number': '98765', 'type(CL213)': 'N380'}],
    #      'goodshipment additional reference': [],
    #      'goodshipment transport document': [{'reference number': '111-12345678', 'type(CL754)': 'N741'}],
    #      'goodshipment additional fiscal reference': [{'role': 'FR5', 'vatIdentificationNumber': 'IM6160000209'}],
    #      'goodshipment transport costs to destination currency': '',
    #      'goodshipment transport costs to destination amount': '',
    #      'goodsitem additional procedure': [{'additional procedure(CL457)': 'C07'},
    #                                         {'additional procedure(CL457)': 'F48'}], 'goodsitem previous document': [],
    #      'goodsitem additional information': [], 'goodsitem supporting document': [],
    #      'goodsitem additional reference': [], 'goodsitem transport document': []}
    a = {'LRN': '1', 'additional declaration type': 'A', 'customs office referenceNumber': 'PL443020',
         'declarant name': '', 'declarant identification number': 'PL521398303500000',
         'declarant street and number': '', 'declarant postcode': '', 'declarant city': '', 'declarant country': '',
         'contact person': [
             {'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094', 'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
         'representative identification number': '', 'representative status': '3', 'representative contact person': [
            {'name': 'Tomasz Zabrocki', 'phoneNumber': '+48698156094', 'eMailAddress': 'Tomasz.Zabrocki@gmail.com'}],
         'customs office reference number': '', 'type of location': 'B', 'qualifier of identification': 'Y',
         'unLocode': '', 'authorisation number': 'PLTST441000200001', 'additional identifier': '', 'latitude': '',
         'longitude': '', 'EORI Number': '', 'address street and number': '', 'address postcode': '',
         'address city': '', 'address country': '', 'postcode address postcode': '',
         'postcode address house number': '', 'postcode address country': '', 'goodshipment referenceNumberUCR': '',
         'goodshipment previous document': [],
         'goodshipment additional information': [],
         'goodshipment supporting document': [{'reference number': '1', 'type(CL213)': 'N380'}],
         'goodshipment additional reference': [],
         'goodshipment transport document': [{'reference number': '1', 'type(CL754)': 'N740'}, {'reference number': '2', 'type(CL754)': 'N703'}],
         'goodshipment additional fiscal reference': [{'role': 'FR5', 'vatIdentificationNumber': 'IM6160000209'}],
         'goodshipment transport costs to destination currency': '',
         'goodshipment transport costs to destination amount': '',
         'goodsitem additional procedure': [{'additional procedure(CL457)': 'C07'},
                                            {'additional procedure(CL457)': 'F48'}], 'goodsitem previous document': [
            {'reference number': '1', 'type(CL214)': 'N337', 'goodsItem identifier': '2'}
        ],
         'goodsitem additional information': [], 'goodsitem supporting document': [],
         'goodsitem additional reference': [], 'goodsitem transport document': []}
    b = [{'InvoiceNumber': 'CN00000000136', 'GoodsItemNumber': 1057, 'HSCode': 940199, 'Total Price': 0.8,
          'GrossMassKg': 0.01, 'AmountPackages': 1, 'TrackingNumber': '00057151272904133604',
          'ConsignorName': 'Shenzhen Test A Company', 'InvoiceCurrency': 'EUR', 'DescriptionGoods': 'brooch',
          'ConsignorStreetAndNr': 'Test,Test,Test,Test', 'ConsignorCity': 'Shenzhen', 'ConsignorPostcode': 518000,
          'ConsignorCountry': 'CN', 'ConsigneeStreetAndNr': 'Sundsmarkvej 58,  ', 'ConsigneePostcode': 6400,
          'ConsigneeCity': 'Sonderborg', 'ConsigneeCountryCode': 'DK', 'AirWayBill': '111-12345678',
          'IOSS': 'IM0123456780', 'CountryOriginCode': 'CN', 'ConsigneeNameID': 12345}]
    window = SADWindow(None, input_information=a, data_rows=b)
    window.show()
    sys.exit(app.exec_())
