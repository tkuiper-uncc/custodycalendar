
import matplotlib.pyplot as plt
from datetime import datetime
import calendar




def flip_parent(current_parent):
    return "Dad" if current_parent == "Mom" else "Mom"


def show_calendar_heatmap(calendar_data, year):
    """Show a calendar heatmap for a given custody calendar."""
    mom_days = set()
    dad_days = set()

    for date_str, parent in calendar_data.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if parent == "Mom":
            mom_days.add(dt)
        elif parent == "Dad":
            dad_days.add(dt)

    fig, axs = plt.subplots(3, 4, figsize=(14, 8))
    fig.suptitle(f"Custody Calendar Heatmap - {year}", fontsize=16)

    for month in range(1, 13):
        ax = axs[(month - 1) // 4][(month - 1) % 4]
        ax.set_title(calendar.month_abbr[month])
        ax.axis("off")

        month_days = calendar.monthrange(year, month)[1]
        for day in range(1, month_days + 1):
            dt = datetime(year, month, day)
            weekday = dt.weekday()
            week = (day + calendar.monthrange(year, month)[0] - 1) // 7
            color = "white"
            if dt in mom_days:
                color = "#ffb6c1"  # light pink for Mom
            elif dt in dad_days:
                color = "#add8e6"  # light blue for Dad
            ax.add_patch(plt.Rectangle((weekday, -week), 1, 1, color=color))
            ax.text(weekday + 0.5, -week + 0.5, str(day), ha="center", va="center", fontsize=8)

        ax.set_xlim(0, 7)
        ax.set_ylim(-6, 0)

    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.show()