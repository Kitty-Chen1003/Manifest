import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QFileDialog, QMessageBox, QScrollArea, QDialogButtonBox
)
from PyQt5.QtCore import Qt


class SignatureDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signature Dialog")
        self.setFixedSize(400, 300)

        # Initialize the layout
        layout = QVBoxLayout(self)

        # File selection section
        self.file_label = QLabel("Select .pfx file:")
        self.file_browse_button = QPushButton("Browse", self)
        self.file_browse_button.clicked.connect(self.browse_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_browse_button)

        # File path display section, with scrolling feature
        self.file_path_display = QLabel("Selected file path will be displayed here...")
        self.file_path_display.setWordWrap(True)  # Enable word wrapping
        self.file_path_display.setFixedHeight(40)  # Limit display height

        # Add file path label inside a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.file_path_display)

        # Password input section
        self.password_label1 = QLabel("Enter password:")
        self.password_input1 = QLineEdit(self)
        self.password_input1.setText('Kosmos2912!')
        # self.password_input1.setPlaceholderText("Enter password")
        self.password_input1.setEchoMode(QLineEdit.Password)

        self.password_label2 = QLabel("Confirm password:")
        self.password_input2 = QLineEdit(self)
        self.password_input2.setText('Kosmos2912!')
        # self.password_input2.setPlaceholderText("Confirm password")
        self.password_input2.setEchoMode(QLineEdit.Password)

        # Set label width to be the same and align text to the right
        label_width = 120
        self.password_label1.setFixedWidth(label_width)
        self.password_label2.setFixedWidth(label_width)
        self.password_label1.setAlignment(Qt.AlignRight)
        self.password_label2.setAlignment(Qt.AlignRight)

        # Password layout (each label and input on one line)
        password_layout1 = QHBoxLayout()
        password_layout1.addWidget(self.password_label1)
        password_layout1.addWidget(self.password_input1)

        password_layout2 = QHBoxLayout()
        password_layout2.addWidget(self.password_label2)
        password_layout2.addWidget(self.password_input2)

        # Button section using QDialogButtonBox for OK/Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.validate_and_close)
        button_box.rejected.connect(self.reject)

        # Set OK button as default button (focusable)
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setDefault(True)

        # Add widgets to the layout
        layout.addLayout(file_layout)
        layout.addWidget(self.scroll_area)
        layout.addLayout(password_layout1)
        layout.addLayout(password_layout2)
        layout.addWidget(button_box)

        # Save results
        self.selected_file = None
        self.password = None

    def browse_file(self):
        # Open the file dialog to select a file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select .pfx file", "", "PFX Files (*.pfx)"
        )
        if file_path:
            self.file_path_display.setText(file_path)  # Display the selected file path

    def validate_and_close(self):
        # Validate if the passwords match
        password1 = self.password_input1.text()
        password2 = self.password_input2.text()
        file_path = self.file_path_display.text()

        # Validate if the file path is selected
        if not file_path or file_path == "Selected file path will be displayed here...":
            QMessageBox.warning(self, "Error", "Please select a .pfx file!")
            return

        # Check if passwords are entered
        if not password1 or not password2:
            QMessageBox.warning(self, "Error", "Please enter both passwords.")
            return

        # Check if passwords match
        if password1 != password2:
            QMessageBox.warning(self, "Error", "The passwords do not match. Please try again.")
            return

        # If everything is valid, store the results and close
        self.selected_file = file_path
        self.password = password1
        self.accept()

    def get_results(self):
        # Return the selected file path and password
        return self.selected_file, self.password

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.validate_and_close()


# Test the dialog
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SignatureDialog()
    if dialog.exec_() == QDialog.Accepted:
        file_path, password = dialog.get_results()
        print("Selected file path:", file_path)
        print("Entered password:", password)
    else:
        print("Operation cancelled")
    sys.exit(app.exec_())
