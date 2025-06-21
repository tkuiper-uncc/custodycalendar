import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QCalendarWidget,
    QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QMessageBox, QDialog, QComboBox, QLineEdit, QDialogButtonBox, QFormLayout, QCheckBox
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QTextCharFormat, QColor
from datetime import datetime, timedelta


class CustodyCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custody Calendar 2025")
        self.resize(500, 400)

        self.conn = sqlite3.connect("custody_calendar.db")
        self.create_table()

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate(2025, 1, 1))
        self.calendar.setMaximumDate(QDate(2025, 12, 31))
        self.calendar.clicked.connect(self.select_date)

        self.label = QLabel("Select a date to assign custody")

        self.mom_btn = QPushButton("Assign Mom")
        self.dad_btn = QPushButton("Assign Dad")
        self.clear_btn = QPushButton("Clear")

        self.mom_btn.clicked.connect(lambda: self.assign_parent("Mom"))
        self.dad_btn.clicked.connect(lambda: self.assign_parent("Dad"))
        self.clear_btn.clicked.connect(lambda: self.assign_parent(""))

        self.summary_btn = QPushButton("Show Custody Summary")
        self.summary_btn.clicked.connect(self.show_summary)

        self.recur_btn = QPushButton("Apply Recurring Schedule")
        self.recur_btn.clicked.connect(self.open_recurring_schedule)

        # Layout
        button_row = QHBoxLayout()
        button_row.addWidget(self.mom_btn)
        button_row.addWidget(self.dad_btn)
        button_row.addWidget(self.clear_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.label)
        layout.addWidget(self.summary_btn)
        layout.addWidget(self.recur_btn)
        layout.addLayout(button_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.selected_date = self.calendar.selectedDate()
        self.load_assignments()

    def create_table(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS assignments (date TEXT PRIMARY KEY, parent TEXT)")
        self.conn.commit()

    def select_date(self, date):
        self.selected_date = date
        date_str = date.toString("yyyy-MM-dd")
        parent = self.get_assignment(date_str)
        self.label.setText(f"{date_str} currently assigned to: {parent or 'None'}")

    def assign_parent(self, parent):
        date_str = self.selected_date.toString("yyyy-MM-dd")
        c = self.conn.cursor()

        if parent:
            c.execute("REPLACE INTO assignments (date, parent) VALUES (?, ?)", (date_str, parent))
        else:
            c.execute("DELETE FROM assignments WHERE date = ?", (date_str,))
        self.conn.commit()

        self.update_calendar_day(self.selected_date, parent)
        self.label.setText(f"{date_str} assigned to: {parent or 'None'}")

    def get_assignment(self, date_str):
        c = self.conn.cursor()
        c.execute("SELECT parent FROM assignments WHERE date = ?", (date_str,))
        result = c.fetchone()
        return result[0] if result else ""

    def load_assignments(self):
        c = self.conn.cursor()
        c.execute("SELECT date, parent FROM assignments")
        for date_str, parent in c.fetchall():
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.update_calendar_day(qdate, parent)

    def update_calendar_day(self, qdate, parent):
        fmt = QTextCharFormat()
        if parent == "Mom":
            fmt.setBackground(QColor("lightpink"))
        elif parent == "Dad":
            fmt.setBackground(QColor("lightblue"))
        else:
            fmt.setBackground(QColor("white"))
        self.calendar.setDateTextFormat(qdate, fmt)

    def show_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, parent FROM assignments")
        counts = {"Mom": {"total": 0, "weekend": 0}, "Dad": {"total": 0, "weekend": 0}}

        for date_str, parent in cursor.fetchall():
            if parent not in counts:
                continue
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            is_weekend = dt.weekday() >= 5
            counts[parent]["total"] += 1
            if is_weekend:
                counts[parent]["weekend"] += 1

        summary = (
            f"=== Custody Summary ===\n"
            f"Mom: {counts['Mom']['total']} total days, {counts['Mom']['weekend']} weekend days\n"
            f"Dad: {counts['Dad']['total']} total days, {counts['Dad']['weekend']} weekend days"
        )
        QMessageBox.information(self, "Custody Summary", summary)

    def open_recurring_schedule(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Apply Recurring Schedule")

        form = QFormLayout(dialog)
        parent_input = QComboBox()
        parent_input.addItems(["Mom", "Dad"])
        days_checkboxes = {
            "Monday": QCheckBox("Monday"),
            "Tuesday": QCheckBox("Tuesday"),
            "Wednesday": QCheckBox("Wednesday"),
            "Thursday": QCheckBox("Thursday"),
            "Friday": QCheckBox("Friday"),
            "Saturday": QCheckBox("Saturday"),
            "Sunday": QCheckBox("Sunday"),
        }
        start_input = QLineEdit("2025-01-01")
        end_input = QLineEdit("2025-12-31")

        form.addRow("Parent:", parent_input)
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            form.addRow(f"{day}:", days_checkboxes[day])
        form.addRow("Start Date (YYYY-MM-DD):", start_input)
        form.addRow("End Date (YYYY-MM-DD):", end_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        form.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                parent = parent_input.currentText()
                selected_days = [i for i, d in
                                 enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                                 if days_checkboxes[d].isChecked()]
                start = datetime.strptime(start_input.text(), "%Y-%m-%d")
                end = datetime.strptime(end_input.text(), "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Invalid date format.")
                return

            cursor = self.conn.cursor()
            applied = []

            dt = start
            while dt <= end:
                if dt.weekday() in selected_days:
                    date_str = dt.strftime("%Y-%m-%d")
                    cursor.execute("REPLACE INTO assignments (date, parent) VALUES (?, ?)", (date_str, parent))
                    applied.append(date_str)
                dt += timedelta(days=1)

            self.conn.commit()
            for date_str in applied:
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                self.update_calendar_day(qdate, parent)
            QMessageBox.information(self, "Schedule Applied", f"{len(applied)} dates assigned to {parent}.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustodyCalendar()
    window.show()
    sys.exit(app.exec())
