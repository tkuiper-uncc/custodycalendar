from calendar_logic import CustodyCalendar

# Create a calendar for 2025, starting Jan 1, with a 2-2-5-5 split
cc = CustodyCalendar(year=2025, start_date="2025-01-01")

# Add summer and holiday overrides
cc.add_override("2025-07-01", "2025-07-14", "Mom")
cc.add_override("2025-11-25", "2025-11-30", "Dad")

# Flip a day (swap parenting assignment)
cc.flip_day("2025-03-10")

# Print July calendar
print("\n=== July 2025 ===")
cc.print_calendar(month=7)

# Summary of total days
print("\n=== Summary ===")
print(cc.summary())
