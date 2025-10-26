import pandas as pd
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QDialog, QTableWidget, QTableWidgetItem, QDialogButtonBox, QHeaderView,
    QAbstractItemView, QLabel, QComboBox, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from utils import db


class SelectionDialog(QDialog):
    def __init__(self, index, json_file_path, title, height, width, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(height, width)
        self.index = index
        self.username = username

        # 加载数据
        if json_file_path != '':
            try:
                self.df = pd.read_json(json_file_path, orient='records', lines=True)
            except Exception as e:
                print(f"Error reading JSON file: {e}")
                self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame()

        cache_data = db.get_input_cache_data(index, self.username)
        self.common_df = pd.DataFrame(cache_data) if cache_data else pd.DataFrame()
        if json_file_path == '' and not self.common_df.empty:
            self.df = self.common_df

        # 查询控件布局
        query_layout = QHBoxLayout()
        self.column_selector = QComboBox()
        self.column_selector.addItems(self.df.columns)  # 下拉菜单加载列名
        self.query_input = QLineEdit()
        self.query_button = QPushButton("Query")
        self.query_button.clicked.connect(self.perform_query)
        nav_button_sheetstyle = """
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
        self.query_button.setStyleSheet(nav_button_sheetstyle)

        query_layout.addWidget(QLabel("Select Fields:"))
        query_layout.addWidget(self.column_selector)
        query_layout.addWidget(QLabel("Input content:"))
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(self.query_button)

        # 常用项表格
        self.commonTableWidget = QTableWidget()
        self.populate_table(self.commonTableWidget, self.common_df)
        self.commonTableWidget.setMaximumHeight(150)

        # 完整表格
        self.tableWidget = QTableWidget()
        self.populate_table(self.tableWidget, self.df)

        # 设置表格标题
        self.common_label = QLabel("Common items:")
        self.full_label = QLabel("Complete information:")

        # 设置表格为单选模式
        self.commonTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.commonTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 确定和取消按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # 主布局
        layout = QVBoxLayout()
        layout.addLayout(query_layout)
        layout.addWidget(self.common_label)
        layout.addWidget(self.commonTableWidget)
        layout.addWidget(self.full_label)
        layout.addWidget(self.tableWidget)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # 当前选择的表单
        self.current_table = self.commonTableWidget

        # 表单点击和双击事件
        self.commonTableWidget.clicked.connect(self.onCommonTableWidgetClicked)
        self.tableWidget.clicked.connect(self.onTableWidgetClicked)
        self.commonTableWidget.doubleClicked.connect(self.onTableWidgetDoubleClicked)
        self.tableWidget.doubleClicked.connect(self.onTableWidgetDoubleClicked)

    def populate_table(self, table_widget, data_frame):
        """填充表格控件内容"""
        table_widget.setRowCount(len(data_frame))
        table_widget.setColumnCount(len(data_frame.columns))
        table_widget.setHorizontalHeaderLabels(data_frame.columns)

        for row in data_frame.itertuples():
            for col in range(len(data_frame.columns)):
                item_text = str(row[col + 1]) if pd.notna(row[col + 1]) else ''
                item = QTableWidgetItem(item_text)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table_widget.setItem(row.Index, col, item)

        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def perform_query(self):
        """根据下拉菜单和输入框内容更新常用项表格"""
        selected_column = self.column_selector.currentText()

        if selected_column:
            query_text = self.query_input.text()

            if query_text.strip():
                filtered_df = self.df[self.df[selected_column].astype(str) == query_text]
                self.common_label.setText('Query results:')
            else:
                filtered_df = self.common_df
                self.common_label.setText('Common items:')

            self.populate_table(self.commonTableWidget, filtered_df)

    def onCommonTableWidgetClicked(self):
        self.current_table = self.commonTableWidget

    def onTableWidgetClicked(self):
        self.current_table = self.tableWidget

    def onTableWidgetDoubleClicked(self, index):
        self.accept()

    def getSelectedRowData(self):
        """获取当前表格选中行的数据"""
        selectedItems = self.current_table.selectedItems()
        if selectedItems:
            selectedRow = selectedItems[0].row()
            row_data = [self.current_table.item(selectedRow, col).text() for col in
                        range(self.current_table.columnCount())]
            return row_data, self.df.columns
        return None, self.df.columns
