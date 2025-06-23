from PyQt6.QtWidgets import QDialog, QLabel, QScrollArea, QWidget, QVBoxLayout, QGridLayout, QCalendarWidget
from PyQt6.QtGui import QTextCharFormat, QColor
from PyQt6.QtCore import QDate
from utils.db import get_all_assignments


class YearlyViewDialog(QDialog):
    def __init__(self, conn, year):
        super().__init__()
        self.setWindowTitle(f"Yearly Custody View - {year}")
        self.resize(1000, 800)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QGridLayout()

        for month in range(1, 13):
            month_name = QDate(2000, month, 1).toString("MMMM")
            label = QLabel(month_name)
            label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 4px;")

            calendar = QCalendarWidget()
            calendar.setMinimumDate(QDate(year, month, 1))
            calendar.setMaximumDate(QDate(year, month, QDate(year, month, 1).daysInMonth()))
            calendar.setGridVisible(True)
            calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            calendar.setNavigationBarVisible(False)
            calendar.setEnabled(False)
            self.highlight_dates(calendar, conn)

            row = (month - 1) // 4
            col = (month - 1) % 4
            layout.addWidget(label, row * 2, col)
            layout.addWidget(calendar, row * 2 + 1, col)

        container.setLayout(layout)
        scroll.setWidget(container)

        dlg_layout = QVBoxLayout()
        dlg_layout.addWidget(scroll)
        self.setLayout(dlg_layout)

    def highlight_dates(self, calendar, conn):
        c = conn.cursor()
        c.execute("SELECT date, parent FROM assignments")
        for date_str, parent in c.fetchall():
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            fmt = QTextCharFormat()
            if parent == "Mom":
                fmt.setBackground(QColor("lightpink"))
            elif parent == "Dad":
                fmt.setBackground(QColor("lightblue"))
            calendar.setDateTextFormat(date, fmt)

