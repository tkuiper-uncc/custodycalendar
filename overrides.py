import json

def load_holiday_overrides(filepath="data/holidays.json"):
    with open(filepath, "r") as f:
        return json.load(f)

def apply_holiday_overrides(calendar, holiday_data):
    for holiday, info in holiday_data.items():
        start = info["start"]
        end = info["end"]
        parent = info.get("assigned_to")
        calendar.add_override(start, end, parent)
