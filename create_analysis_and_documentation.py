from collections import defaultdict
import json
from datetime import datetime
from tools.plot import basic_plot, multiplot, plot_projects


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


total_active_users_per_date
not_active_points_map

delta_points = []
for key, value in evaluation_points_date_list_precise:
    active_user = 1
    not_active_point = 0
    if key in not_active_points_map:
        not_active_point = not_active_points_map[key]
    if key in total_active_users_per_date:
        active_user = total_active_users_per_date[key]
    if active_user == 0:
        active_user = 1
    new_value = (value - not_active_point) / active_user
    delta_points.append((key, new_value))

basic_plot(data_list=delta_points, x_axis="Day", y_axis="Points", title="Points per Active User over Time", save_name="points_per_user_in_economy_over_time")


project_count_map = data.get("project_count_map", {})
just_common_core = {}
for key, value in project_count_map.items():
    if "inner-circle" in key:
        name = key.split("inner-circle/")
        just_common_core[name[1]] = value // 2


plot_projects(just_common_core, save_name="inner_circle", title="Inner-Circle Evaluations", x_axis="Projects", y_axis="Amount of evaluations done")


just_common_core = {}
for key, value in project_count_map.items():
    if "outer-circle" in key:
        name = key.split("outer-circle/")
        just_common_core[name[1]] = value // 2


plot_projects(just_common_core, save_name="outer_circle", title="Outer-Circle Evaluations", x_axis="Projects", y_axis="Amount of evaluations done")



just_common_core = {}
for key, value in project_count_map.items():
    if "germany-basecamp/basecamp-" in key:
        name = key.split("germany-basecamp/basecamp-")
        if name[1] not in just_common_core:
            just_common_core[name[1]] = value // 2
        else:
            just_common_core[name[1]] += value // 2
    if "c-piscine/" in key:
        name = key.split("c-piscine/")
        if name[1] not in just_common_core:
            just_common_core[name[1]] = value // 2
        else:
            just_common_core[name[1]] += value // 2


plot_projects(just_common_core, save_name="piscine", title="Piscine Evaluations", x_axis="Projects", y_axis="Amount of evaluations done")
