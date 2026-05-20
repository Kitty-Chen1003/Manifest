from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QDateTimeEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta
import pytz

from utils import db
from communication import http_client


class DeleteByTimeDialog(QDialog):
    def __init__(self, username, token):
        super().__init__()

        self.username = username
        self.token = token

        self.setWindowTitle("Delete Data By Time")
        self.setFixedSize(500, 400)

        main_layout = QVBoxLayout(self)

        # ===== 时间选择 =====
        time_layout = QHBoxLayout()

        self.start_time = QDateTimeEdit()
        self.end_time = QDateTimeEdit()

        self.start_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        self.start_time.setCalendarPopup(True)
        self.end_time.setCalendarPopup(True)

        # 默认时间（最近7天）
        pl_tz = pytz.timezone("Europe/Warsaw")
        now = datetime.now(pl_tz)
        one_week_ago = now - timedelta(days=7)

        self.start_time.setDateTime(one_week_ago)
        self.end_time.setDateTime(now)

        time_layout.addWidget(QLabel("Start Time"))
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(QLabel("End Time"))
        time_layout.addWidget(self.end_time)

        main_layout.addLayout(time_layout)

        # ===== 按钮 =====
        bottom_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)  # 设置为默认按钮
        self.cancel_btn = QPushButton("Cancel")
        bottom_layout.addWidget(self.ok_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        # ===== 绑定 =====
        self.ok_btn.clicked.connect(self.on_confirm)  # 确定按钮：执行操作
        self.cancel_btn.clicked.connect(self.reject)  # 取消按钮：关闭对话框

    def on_confirm(self):
        start = self.start_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end = self.end_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete ALL data between:\n{start} ~ {end} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        if self.token:
            # ===== 后端 =====
            payload = {
                "starttime": start,
                "endtime": end
            }

            response_status_code = http_client.delete_data_by_time(self.token, payload)

            if response_status_code != 200:
                QMessageBox.warning(self, "Error", "Backend delete failed.")
                return

            QMessageBox.information(self, "Success", 'Backend delete successfully!')
        else:
            QMessageBox.warning(self, "Error", 'Login failed: the account password is incorrect')
            return  # 返回发送界面，保持对话框打开

        # ===== 本地 =====
        success = db.delete_by_time(start, end)
        if not success:
            QMessageBox.warning(self, "Error", "Local delete failed.")
            return

        QMessageBox.information(self, "Success", "Local delete successfully.")

        self.accept()
