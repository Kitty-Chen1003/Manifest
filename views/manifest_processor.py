# 1、检查是否有 negative hscode，整改
# 2、按 consignee 分组 （上限 999goods、99IOSS）
# 3、剔除 >150euro 的 consignee
# 4、按每张 100 位 consignee 分割 manifest
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QCheckBox, QGridLayout, \
    QFileDialog, QVBoxLayout, QHBoxLayout, QSizePolicy, QMessageBox, QTableWidget, QHeaderView, QTableWidgetItem, \
    QScrollArea, QAbstractItemView

from utils.manifest import *


class ManifestProcessor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Manifest Processor")
        self.setGeometry(100, 100, 600, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create main layout
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Create grid layout for form fields
        self.grid_layout = QGridLayout()
        self.main_layout.addLayout(self.grid_layout)

        # Add widgets to grid layout
        self.grid_layout.addWidget(QLabel("Input File:"), 0, 0, Qt.AlignRight)
        self.input_file_edit = QLineEdit()
        self.grid_layout.addWidget(self.input_file_edit, 0, 1)
        self.input_file_button = QPushButton("Browse")
        self.input_file_button.clicked.connect(self.browse_input_file)
        self.grid_layout.addWidget(self.input_file_button, 0, 2)

        self.grid_layout.addWidget(QLabel("Output Directory:"), 1, 0, Qt.AlignRight)
        self.output_directory_edit = QLineEdit()
        self.grid_layout.addWidget(self.output_directory_edit, 1, 1)
        self.output_directory_button = QPushButton("Browse")
        self.output_directory_button.clicked.connect(self.browse_output_directory)
        self.grid_layout.addWidget(self.output_directory_button, 1, 2)

        self.add_good_item_id_checkbox = QCheckBox("Add a GoodsItemId column to your manifest file")
        self.grid_layout.addWidget(self.add_good_item_id_checkbox, 2, 1)

        self.grid_layout.addWidget(QLabel("Split Column:"), 3, 0, Qt.AlignRight)
        self.split_column_edit = QLineEdit("ConsigneeName+ConsigneeFamilyName+ConsigneePostcode")
        self.grid_layout.addWidget(self.split_column_edit, 3, 1)

        self.add_column_button = QPushButton("Add Column")
        self.add_column_button.clicked.connect(self.add_column)
        self.grid_layout.addWidget(self.add_column_button, 4, 1)

        # Container for new rows
        self.column_container = QVBoxLayout()
        self.main_layout.addLayout(self.column_container)

        # List to store references to the QLineEdit widgets in new rows
        self.new_rows = []

        # Horizontal layout for the run button
        self.run_layout = QHBoxLayout()
        self.main_layout.addLayout(self.run_layout)

        self.run_button = QPushButton("Run")
        self.run_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.run_button.clicked.connect(self.run_processing)
        self.run_layout.addWidget(self.run_button, alignment=Qt.AlignCenter)

        # Apply some basic styling
        self.setStyleSheet("""
            QLineEdit {
                font-family: Times New Roman;
                font-size: 18px;
                padding: 5px;
            }
            QPushButton {
                padding: 5px;
            }
        """)

    def browse_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            self.input_file_edit.setText(file_name)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.output_directory_edit.setText(directory)

    def add_column(self):
        # Create a new horizontal layout for the new row
        new_row_layout = QHBoxLayout()

        # Create two new QLineEdit fields
        column_name = QLineEdit()
        column_content = QLineEdit()

        # Create a delete button
        delete_button = QPushButton("remove")
        delete_button.clicked.connect(lambda: self.delete_row(new_row_layout, (column_name, column_content)))

        # Add the QLineEdit fields and the delete button to the new row layout
        new_row_layout.addWidget(column_name)
        new_row_layout.addWidget(column_content)
        new_row_layout.addWidget(delete_button)

        # Add the new row layout to the column container
        self.column_container.addLayout(new_row_layout)

        # Store references to the QLineEdit widgets
        self.new_rows.append((column_name, column_content))

    def delete_row(self, row_layout, fields):
        # Remove all widgets from the row layout
        while row_layout.count():
            item = row_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Remove the row layout from the column container
        self.column_container.removeItem(row_layout)

        # Remove the corresponding entry in self.new_rows
        if fields in self.new_rows:
            self.new_rows.remove(fields)

        self.adjustSize()

    def show_error(self, msg):
        msg_box = QMessageBox(QMessageBox.Critical, "Error", msg)
        msg_box.exec_()

    def show_info(self, msg):
        msg_box = QMessageBox(QMessageBox.Information, "Success", msg)
        msg_box.exec_()

    def show_negative_goods_items(self, data_negative):
        # Create a new window
        self.table_window = QMainWindow()
        self.table_window.setWindowTitle("Negative Goods Items")
        self.table_window.setGeometry(200, 200, 800, 400)

        # Create a central widget and set layout
        central_widget = QWidget()
        self.table_window.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a table widget
        table_widget = QTableWidget()
        table_widget.setRowCount(data_negative.shape[0])
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["GoodsItemNumber", "HSCode", "DescriptionGoods"])
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Populate the table widget with data
        for row, (_, item) in enumerate(data_negative.iterrows()):
            table_widget.setItem(row, 0, QTableWidgetItem(str(item.get('GoodsItemNumber'))))
            table_widget.setItem(row, 1, QTableWidgetItem(str(item.get('HSCode'))))
            table_widget.setItem(row, 2, QTableWidgetItem(str(item.get('DescriptionGoods'))))

        # Create a scroll area and set the table widget as its widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(table_widget)
        scroll_area.setWidgetResizable(True)

        # Add the scroll area to the layout
        layout.addWidget(scroll_area)

        # Show the new window
        self.table_window.show()

    def run_processing(self):
        data_path = self.input_file_edit.text()
        output_directory = self.output_directory_edit.text()
        add_id_column = self.add_good_item_id_checkbox.isChecked()
        split_columns = list(self.split_column_edit.text().split("+"))
        add_columns = list((field1.text(), field2.text()) for field1, field2 in self.new_rows)

        if not data_path:
            self.show_error("Please select an input file.")
            return False

        # if not output_directory:
        #     self.show_error("Please select an output directory.")
        #     return False

        try:
            input_file = pd.read_excel(data_path, dtype=str)
            # 去除所有字符串列的前后空格
            input_file = input_file.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        except Exception as e:
            self.show_error("No such file.")
            return False

        # try:
        #     input_file = align_hscode(input_file)
        # except HscodeError as e:
        #     self.show_error(e.__str__())
        #     return False

        data_negative = check_hscode(input_file)
        if not data_negative.empty:
            self.show_error(f'{data_negative.shape[0]} items with negative HScode detected.')
            self.show_negative_goods_items(data_negative)
            return False

        over_count = process_manifests(input_file, data_path, output_directory)
        self.show_info(f"Processed completed. Over 150: {over_count}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ManifestProcessor()
    main_window.show()
    sys.exit(app.exec_())
