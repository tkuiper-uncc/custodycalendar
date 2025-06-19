from datetime import datetime, timedelta
from collections import defaultdict
from utils import flip_parent

class CustodyCalendar:
    def __init__(self, year):
        self.year = year
        self.calendar = {}
        self.ownership_counts = defaultdict(int)
        self.parents = ["Mom", "Dad"]

    def assign_day(self, date, parent):
        date_str = date.strftime("%Y-%m-%d")
        old_parent = self.calendar.get(date_str)
        if old_parent:
            self.ownership_counts[old_parent] -= 1
        self.calendar[date_str] = parent
        self.ownership_counts[parent] += 1

    def generate_school_schedule(self, start_date_str, end_date_str, pattern=(2, 2, 5, 5)):
        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        parent_index = 0  # Start with Mom

        while current_date <= end_date:
            for days in pattern:
                for _ in range(days):
                    if current_date > end_date:
                        break
                    self.assign_day(current_date, self.parents[parent_index])
                    current_date += timedelta(days=1)
                parent_index = 1 - parent_index  # Swap parent

    def generate_summer_schedule(self, start_date_str, end_date_str):
        current_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        parent_index = 0  # Start with Mom

        while current_date <= end_date:
            week_end = current_date + timedelta(days=6)
            for i in range(7):
                day = current_date + timedelta(days=i)
                if day > end_date:
                    break
                self.assign_day(day, self.parents[parent_index])
            # Flip parent after each 7-day block
            parent_index = 1 - parent_index
            current_date = week_end + timedelta(days=1)

    def add_override(self, start, end, parent):
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        while start_dt <= end_dt:
            self.assign_day(start_dt, parent)
            start_dt += timedelta(days=1)

    def flip_day(self, date_str):
        if date_str in self.calendar:
            current_parent = self.calendar[date_str]
            new_parent = flip_parent(current_parent)
            date = datetime.strptime(date_str, "%Y-%m-%d")
            self.assign_day(date, new_parent)

    def print_calendar(self, month=None):
        for date_str in sorted(self.calendar):
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if month is None or date.month == month:
                print(f"{date_str} - {self.calendar[date_str]}")

    def summary(self):
        return dict(self.ownership_counts)

    def weekday_weekend_report(self):
        weekday_counts = defaultdict(int)
        weekend_counts = defaultdict(int)

        for date_str, parent in self.calendar.items():
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date.weekday() < 5:  # Monday=0, Sunday=6
                weekday_counts[parent] += 1
            else:
                weekend_counts[parent] += 1

        return {
            "Weekdays": dict(weekday_counts),
            "Weekends": dict(weekend_counts)
        }



