from PyQt6.QtWidgets import (QMainWindow, QCalendarWidget, QLabel, QVBoxLayout, QWidget,
                             QPushButton, QHBoxLayout, QMessageBox, QDialog, QComboBox,
                             QLineEdit, QDialogButtonBox, QFormLayout, QInputDialog, QCheckBox)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QTextCharFormat, QColor
from datetime import datetime, timedelta
import sqlite3

from gui.yearly_view import YearlyViewDialog
from utils.db import create_table, get_assignment, save_assignment, load_assignments, get_all_assignments


class CustodyCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        year, ok = QInputDialog.getInt(self, "Select Year", "Enter calendar year:", value=2025)
        self.year = year if ok else 2025
        self.setWindowTitle(f"Custody Calendar {self.year}")
        self.resize(500, 400)
        self.conn = sqlite3.connect("data/custody_calendar.db")
        create_table(self.conn)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate(self.year, 1, 1))
        self.calendar.setMaximumDate(QDate(self.year, 12, 31))
        self.calendar.clicked.connect(self.select_date)

        self.label = QLabel("Select a date to assign custody")

        self.mom_btn = QPushButton("Assign Mom")
        self.dad_btn = QPushButton("Assign Dad")
        self.clear_btn = QPushButton("Clear")
        self.mom_btn.clicked.connect(lambda: self.assign_parent("Mom"))
        self.dad_btn.clicked.connect(lambda: self.assign_parent("Dad"))
        self.clear_btn.clicked.connect(lambda: self.assign_parent(""))

        self.summary_btn = QPushButton("Show Custody Summary")
        self.recur_btn = QPushButton("Apply Recurring Schedule")
        self.note_btn = QPushButton("Add/View Note")
        self.yearly_btn = QPushButton("Yearly View")

        self.summary_btn.clicked.connect(self.show_summary)
        self.recur_btn.clicked.connect(self.open_recurring_schedule)
        self.note_btn.clicked.connect(self.add_view_note)
        self.yearly_btn.clicked.connect(self.open_yearly_view)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addWidget(self.label)
        layout.addWidget(self.summary_btn)
        layout.addWidget(self.recur_btn)
        layout.addWidget(self.note_btn)
        layout.addWidget(self.yearly_btn)

        button_row = QHBoxLayout()
        button_row.addWidget(self.mom_btn)
        button_row.addWidget(self.dad_btn)
        button_row.addWidget(self.clear_btn)
        layout.addLayout(button_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.selected_date = self.calendar.selectedDate()
        self.load_assignments()

    def select_date(self, date):
        self.selected_date = date
        date_str = date.toString("yyyy-MM-dd")
        parent = self.get_assignment(date_str)
        self.label.setText(f"{date_str} currently assigned to: {parent or 'None'}")

    def assign_parent(self, parent):
        date_str = self.selected_date.toString("yyyy-MM-dd")
        c = self.conn.cursor()
        c.execute("SELECT note FROM assignments WHERE date = ?", (date_str,))
        note_result = c.fetchone()
        note = note_result[0] if note_result else ""
        if parent:
            c.execute("REPLACE INTO assignments (date, parent, note) VALUES (?, ?, ?)", (date_str, parent, note))
        else:
            c.execute("DELETE FROM assignments WHERE date = ?", (date_str,))
        self.conn.commit()
        self.update_calendar_day(self.selected_date, parent)
        self.label.setText(f"{date_str} assigned to: {parent or 'None'}")

    def update_calendar_day(self, qdate, parent):
        fmt = QTextCharFormat()
        if parent == "Mom":
            fmt.setBackground(QColor("lightpink"))
        elif parent == "Dad":
            fmt.setBackground(QColor("lightblue"))
        else:
            fmt.setBackground(QColor("white"))
        self.calendar.setDateTextFormat(qdate, fmt)

    def load_assignments(self):
        c = self.conn.cursor()
        c.execute("SELECT date, parent FROM assignments")
        for date_str, parent in c.fetchall():
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            self.update_calendar_day(qdate, parent)

    def open_yearly_view(self):
        # Refresh the selected date formatting in case it was missed
        selected_str = self.selected_date.toString("yyyy-MM-dd")
        parent = self.get_assignment(selected_str)
        self.update_calendar_day(self.selected_date, parent)

        dlg = YearlyViewDialog(self.conn, self.year)
        dlg.exec()

    def show_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT date, parent FROM assignments")
        yearly_counts = {}
        for date_str, parent in cursor.fetchall():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                year = dt.year
                if parent not in ["Mom", "Dad"]:
                    continue
                if year not in yearly_counts:
                    yearly_counts[year] = {"Mom": {"total": 0, "weekend": 0}, "Dad": {"total": 0, "weekend": 0}}
                is_weekend = dt.weekday() >= 5
                yearly_counts[year][parent]["total"] += 1
                if is_weekend:
                    yearly_counts[year][parent]["weekend"] += 1
            except:
                continue
        summary = "=== Custody Summary by Year ===\n"


        for year in sorted(yearly_counts.keys()):
            counts = yearly_counts[year]
            summary += (
                f"Year {year}:"
                f"  Mom - {counts['Mom']['total']} days, {counts['Mom']['weekend']} weekend days"
                f"  Dad - {counts['Dad']['total']} days, {counts['Dad']['weekend']} weekend days"

            )
        QMessageBox.information(self, "Custody Summary", summary)

    def open_recurring_schedule(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Apply Recurring Schedule")

        form = QFormLayout(dialog)
        parent_input = QComboBox()
        parent_input.addItems(["Mom", "Dad"])
        days_checkboxes = {day: QCheckBox(day) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
        interval_input = QLineEdit("2")
        start_input = QLineEdit(f"{self.year}-01-01")
        end_input = QLineEdit(f"{self.year}-12-31")

        form.addRow("Parent:", parent_input)
        for day, checkbox in days_checkboxes.items():
            form.addRow(day + ":", checkbox)
        form.addRow("Every N Weeks:", interval_input)
        form.addRow("Start Date (YYYY-MM-DD):", start_input)
        form.addRow("End Date (YYYY-MM-DD):", end_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        form.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                parent = parent_input.currentText()
                interval = int(interval_input.text())
                selected_days = [i for i, d in enumerate(days_checkboxes) if days_checkboxes[d].isChecked()]
                start = datetime.strptime(start_input.text(), "%Y-%m-%d")
                end = datetime.strptime(end_input.text(), "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Invalid input.")
                return

            cursor = self.conn.cursor()
            applied = []
            dt = start
            week_index = 0
            while dt <= end:
                if week_index % interval == 0:
                    for weekday in selected_days:
                        d = dt + timedelta(days=(weekday - dt.weekday()) % 7)
                        if start <= d <= end:
                            date_str = d.strftime("%Y-%m-%d")
                            cursor.execute("REPLACE INTO assignments (date, parent, note) VALUES (?, ?, ?)", (date_str, parent, ""))
                            applied.append(date_str)
                dt += timedelta(weeks=1)
                week_index += 1

            self.conn.commit()
            for date_str in applied:
                qdate = QDate.fromString(date_str, "yyyy-MM-dd")
                self.update_calendar_day(qdate, parent)
            QMessageBox.information(self, "Schedule Applied", f"{len(applied)} dates assigned to {parent}.")

    def add_view_note(self):
        date_str = self.selected_date.toString("yyyy-MM-dd")
        cursor = self.conn.cursor()
        cursor.execute("SELECT note FROM assignments WHERE date = ?", (date_str,))
        existing_note = cursor.fetchone()
        note = existing_note[0] if existing_note else ""
        text, ok = QInputDialog.getMultiLineText(self, f"Note for {date_str}", "Note:", note)
        if ok:
            cursor.execute("SELECT parent FROM assignments WHERE date = ?", (date_str,))
            parent_result = cursor.fetchone()
            parent = parent_result[0] if parent_result else ""
            cursor.execute("REPLACE INTO assignments (date, parent, note) VALUES (?, ?, ?)", (date_str, parent, text))
            self.conn.commit()
