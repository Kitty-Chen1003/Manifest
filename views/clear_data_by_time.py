import sys
import pytz
from PyQt5.QtWidgets import (
    QDialog, QApplication, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton
)
from datetime import datetime


class DateTimeDialog(QDialog):
    def __init__(self, flag):
        super().__init__()

        self.setWindowTitle("Enter filter date")
        self.setFixedSize(500, 200)
        self.flag = flag

        # 获取波兰当前时间（CET/CEST）
        pl_tz = pytz.timezone("Europe/Warsaw")
        pl_time = datetime.now(pl_tz)

        # 主布局
        main_layout = QVBoxLayout()

        # 创建筛选状态布局
        filter_layout = QHBoxLayout()
        self.filter_status_label = QLabel("Current status: Closed")
        self.enable_filter_button = QPushButton("Enable time filtering")
        self.disable_filter_button = QPushButton("Close time filter")

        self.enable_filter_button.clicked.connect(self.enable_time_filter)
        self.disable_filter_button.clicked.connect(self.disable_time_filter)

        filter_layout.addWidget(self.filter_status_label)
        filter_layout.addWidget(self.enable_filter_button)
        filter_layout.addWidget(self.disable_filter_button)

        # 年月日布局
        date_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(pl_time.year)

        self.month_spin = QSpinBox()
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(pl_time.month)

        self.day_spin = QSpinBox()
        self.day_spin.setRange(1, 31)
        self.day_spin.setValue(pl_time.day)

        date_layout.addWidget(QLabel("Year"))
        date_layout.addWidget(self.year_spin)
        date_layout.addWidget(QLabel("Month"))
        date_layout.addWidget(self.month_spin)
        date_layout.addWidget(QLabel("Day"))
        date_layout.addWidget(self.day_spin)

        # 小时分钟秒布局
        time_layout = QHBoxLayout()
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(pl_time.hour)

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(pl_time.minute)

        self.second_spin = QSpinBox()
        self.second_spin.setRange(0, 59)
        self.second_spin.setValue(pl_time.second)

        time_layout.addWidget(QLabel("Hour"))
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(QLabel("Minute"))
        time_layout.addWidget(self.minute_spin)
        time_layout.addWidget(QLabel("Second"))
        time_layout.addWidget(self.second_spin)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        self.ok_button.setDefault(True)

        # 添加组件到主布局
        main_layout.addLayout(filter_layout)  # 添加状态和按钮
        main_layout.addLayout(date_layout)
        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # 默认关闭时间筛选
        self.disable_time_filter()

        if self.flag:
            self.enable_time_filter()

    def enable_time_filter(self):
        """启用时间筛选，允许修改日期时间"""
        self.set_time_widgets_enabled(True)
        self.filter_status_label.setText("Current status: Enabled")
        self.flag = 1

    def disable_time_filter(self):
        """关闭时间筛选，不允许修改日期时间"""
        self.set_time_widgets_enabled(False)
        self.filter_status_label.setText("Current status: Closed")
        self.flag = 0

    def set_time_widgets_enabled(self, enabled):
        """控制时间输入框的启用/禁用状态"""
        self.year_spin.setEnabled(enabled)
        self.month_spin.setEnabled(enabled)
        self.day_spin.setEnabled(enabled)
        self.hour_spin.setEnabled(enabled)
        self.minute_spin.setEnabled(enabled)
        self.second_spin.setEnabled(enabled)

    def get_datetime(self):
        """获取用户选择的日期时间，并格式化为 'YYYY-MM-DD HH:MM:SS' """
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            self.year_spin.value(),
            self.month_spin.value(),
            self.day_spin.value(),
            self.hour_spin.value(),
            self.minute_spin.value(),
            self.second_spin.value()
        )

    def get_time_flag(self):
        return self.flag


# 运行示例
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DateTimeDialog(0)

    if dialog.exec_():
        selected_datetime = dialog.get_datetime()
        print("用户选择的时间:", selected_datetime)

    sys.exit(app.exec_())