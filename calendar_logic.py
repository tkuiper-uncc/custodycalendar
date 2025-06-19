from datetime import datetime, timedelta
from collections import defaultdict
from utils import flip_parent

class CustodyCalendar:
    def __init__(self, year, start_date, schedule_pattern=(2, 2, 5, 5)):
        self.year = year
        self.schedule_pattern = schedule_pattern
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.calendar = {}
        self.ownership_counts = defaultdict(int)
        self.parents = ["Mom", "Dad"]
        self.generate_base_schedule()

    def generate_base_schedule(self):
        pattern = self.schedule_pattern
        parent_index = 0
        current_date = self.start_date

        while current_date.year == self.year:
            for days in pattern:
                for _ in range(days):
                    if current_date.year == self.year:
                        date_str = current_date.strftime("%Y-%m-%d")
                        self.calendar[date_str] = self.parents[parent_index]
                        self.ownership_counts[self.parents[parent_index]] += 1
                    current_date += timedelta(days=1)
                parent_index = 1 - parent_index

    def add_override(self, start, end, parent):
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
        while start_dt <= end_dt:
            date_str = start_dt.strftime("%Y-%m-%d")
            old_parent = self.calendar.get(date_str)
            if old_parent:
                self.ownership_counts[old_parent] -= 1
            self.calendar[date_str] = parent
            self.ownership_counts[parent] += 1
            start_dt += timedelta(days=1)

    def flip_day(self, date_str):
        if date_str in self.calendar:
            current_parent = self.calendar[date_str]
            new_parent = flip_parent(current_parent)
            self.calendar[date_str] = new_parent
            self.ownership_counts[current_parent] -= 1
            self.ownership_counts[new_parent] += 1
        else:
            print(f"No assignment found on {date_str}")

    def print_calendar(self, month=None):
        for date_str in sorted(self.calendar):
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if month is None or date.month == month:
                print(f"{date_str} - {self.calendar[date_str]}")

    def summary(self):
        return dict(self.ownership_counts)
