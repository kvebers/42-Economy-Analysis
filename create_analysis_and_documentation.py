from collections import defaultdict
import json
from datetime import datetime
from tools.plot import basic_plot, multiplot


with open("data/campus.json", "r") as f:
    data = json.load(f)


total_active_users_per_date = data.get("total_active_users_per_date", {})
total_active_users_per_date_sorted = sorted(
    total_active_users_per_date.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

basic_plot(data_list=total_active_users_per_date_sorted, x_axis="Date", y_axis="User Count", title="User Count Over Time", save_name="user_over_time_count")

evals_per_day_map = data.get("evals_per_day_map", {})

evals_per_day_list_sorted = sorted(
    evals_per_day_map.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

basic_plot(data_list=evals_per_day_list_sorted, x_axis="Date", y_axis="Eval Count", title="Evals per day map", save_name="evals_per_day_count")


not_active_points_map = data.get("not_active_points_map", {})

not_active_points_map_sorted = sorted(
    not_active_points_map.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

not_active_points_total = 0
not_active_points_list_total = []
for key, value in not_active_points_map_sorted:
    not_active_points_total += value
    not_active_points_list_total.append((key, not_active_points_total))

basic_plot(data_list=not_active_points_list_total, x_axis="Date", y_axis="Points", title="Points that are not active in the system", save_name="non_active_points")


get_total_active_points = data.get("get_total_active_points", {})
evaluation_points_date_map = data.get("evaluation_points_date_map")
evaluation_points_date_list = sorted(
    evaluation_points_date_map.items(),
    key=lambda x: datetime.fromisoformat(x[0])
)

evaluation_points_date_list_precise = []
for key, value in evaluation_points_date_list[::-1]:
    evaluation_points_date_list_precise.append((key, get_total_active_points))
    get_total_active_points -= value

evaluation_points_date_list_precise.sort(key=lambda x: x[0])

basic_plot(data_list=evaluation_points_date_list_precise, x_axis="Date", y_axis="Points per day", save_name="points_over_time", title="Evaluation Points In the System Over Time")

data_lists=[
    (evaluation_points_date_list_precise, "Total Active Points"),
    (not_active_points_list_total, "Non Active Points"),
]

multiplot(data_lists, x_axis="Date", y_axis="Points per day", save_name="points_over_time_vs_non_active_points", title="Total vs Non Active Points")


monthly_evals_data = defaultdict(int)
for date_str, count in evals_per_day_map.items():
    dt = datetime.fromisoformat(date_str)
    key = dt.strftime("%Y-%m-01")
    monthly_evals_data[key] += count

evals_per_month_list_sorted = sorted(
    monthly_evals_data.items(),
    key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")
)

basic_plot(data_list=evals_per_month_list_sorted, x_axis="Month", y_axis="Eval Count", title="Evals per Month", save_name="evals_per_month_count")


