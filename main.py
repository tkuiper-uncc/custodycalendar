from calendar_logic import CustodyCalendar

cc = CustodyCalendar(year=2025)

# School schedule (2-2-5-5)
cc.generate_school_schedule("2025-01-01", "2025-05-20")
cc.generate_school_schedule("2025-08-13", "2025-12-31")

# Summer schedule (week-on/week-off, Sunday 7PM exchanges — modeled by full days)
cc.generate_summer_schedule("2025-05-21", "2025-08-12")

# Overrides (e.g. Mom gets July 4–7)
cc.add_override("2025-07-04", "2025-07-07", "Mom")

# Optional day flip
cc.flip_day("2025-06-15")

# Output July
print("\n=== July 2025 ===")
cc.print_calendar(month=7)

# Summary
print("\n=== Summary ===")
print(cc.summary())

# Generate the report
report = cc.weekday_weekend_report()
print("\n=== Weekday/Weekend Report ===")
print("Weekdays:", report["Weekdays"])
print("Weekends:", report["Weekends"])
