import tkinter as tk
from tkinter import messagebox
from calendar_logic import CustodyCalendar
from utils import show_calendar_heatmap


class CustodyApp:
    def __init__(self, root):
        self.cc = CustodyCalendar(year=2025)
        self.root = root
        self.root.title("Custody Calendar 2025")

        self.output = tk.Text(root, height=20, width=60)
        self.output.pack()

        # Buttons
        tk.Button(root, text="Generate Calendar", command=self.generate_calendar).pack()
        tk.Button(root, text="Add Override", command=self.add_override_prompt).pack()
        tk.Button(root, text="Flip Day", command=self.flip_day_prompt).pack()
        tk.Button(root, text="View Summary", command=self.show_summary).pack()
        tk.Button(root, text="Weekday/Weekend Report", command=self.show_report).pack()
        tk.Button(root, text="Show Heatmap", command=self.show_heatmap).pack()  # <-- move this here


    def generate_calendar(self):
        self.cc.generate_school_schedule("2025-01-01", "2025-05-20")
        self.cc.generate_school_schedule("2025-08-13", "2025-12-31")
        self.cc.generate_summer_schedule("2025-05-21", "2025-08-12")
        self.output.insert(tk.END, "📅 Calendar generated.\n")

    def add_override_prompt(self):
        top = tk.Toplevel()
        tk.Label(top, text="Start Date (YYYY-MM-DD):").pack()
        start_entry = tk.Entry(top)
        start_entry.pack()
        tk.Label(top, text="End Date (YYYY-MM-DD):").pack()
        end_entry = tk.Entry(top)
        end_entry.pack()
        tk.Label(top, text="Parent (Mom or Dad):").pack()
        parent_entry = tk.Entry(top)
        parent_entry.pack()

        def submit():
            try:
                self.cc.add_override(start_entry.get(), end_entry.get(), parent_entry.get())
                self.output.insert(tk.END, f"✅ Override added: {parent_entry.get()} {start_entry.get()} to {end_entry.get()}\n")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="Submit", command=submit).pack()

    def flip_day_prompt(self):
        top = tk.Toplevel()
        tk.Label(top, text="Date to Flip (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(top)
        date_entry.pack()

        def submit():
            try:
                self.cc.flip_day(date_entry.get())
                self.output.insert(tk.END, f"🔄 Day flipped: {date_entry.get()}\n")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="Submit", command=submit).pack()

    def show_summary(self):
        summary = self.cc.summary()
        self.output.insert(tk.END, f"\n=== Summary ===\n{summary}\n")

    def show_report(self):
        report = self.cc.weekday_weekend_report()
        self.output.insert(tk.END, f"\n=== Weekday/Weekend Report ===\n")
        self.output.insert(tk.END, f"Weekdays: {report['Weekdays']}\n")
        self.output.insert(tk.END, f"Weekends: {report['Weekends']}\n")

    def show_heatmap(self):
        show_calendar_heatmap(self.cc.calendar, self.cc.year)


if __name__ == "__main__":
    root = tk.Tk()
    app = CustodyApp(root)
    root.mainloop()

