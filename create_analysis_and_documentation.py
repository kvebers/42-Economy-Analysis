import json
import matplotlib.pyplot as plt
from datetime import datetime

def basic_plot(data_map, title, x_axis, y_axis, save_name):
    dates = [d for d, _ in data_map]
    counts = [c for _, c in data_map]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker=".")
    plt.xticks(dates[::30], rotation=30)
    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.tight_layout()
    plt.savefig(f"img/{save_name}", dpi=300)


with open("data/perform_temp_analysis.json", "r") as f:
    data = json.load(f)


total_active_users_per_date = data.get("total_active_users_per_date", {})
total_active_users_per_date_sorted = sorted(
    total_active_users_per_date.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

basic_plot(data_map=total_active_users_per_date_sorted, x_axis="Date", y_axis="User Count", title="User Count Over Time", save_name="user_over_time_count")

evals_per_day_map = data.get("evals_per_day_map", {})

evals_per_day_map_sorted = sorted(
    evals_per_day_map.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

basic_plot(data_map=evals_per_day_map_sorted, x_axis="Date", y_axis="Eval Count", title="Evals per day map", save_name="evals_per_day_count")


