import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def locator_and_formater(span):
    if span <= 31:
        locator = mdates.DayLocator(interval=1)
        formatter = mdates.DateFormatter("%m-%d")
    elif span <= 365:
        locator = mdates.MonthLocator(interval=1)
        formatter = mdates.DateFormatter("%Y-%m")
    else:
        locator = mdates.YearLocator()
        formatter = mdates.DateFormatter("%Y")
    return locator, formatter


def basic_plot(data_list, title="default", x_axis="default", y_axis="default", save_name="default", start_date="2021-06-01"):
    if start_date:
        start_date = datetime.fromisoformat(start_date)    
    filtered_data = [(datetime.fromisoformat(d), c) for d, c in data_list
                     if not start_date or datetime.fromisoformat(d) >= start_date]
    dates, counts = zip(*filtered_data)
    if len(dates) > 1:
        dates = dates[:-1]
        counts = counts[:-1]
    span = (max(dates) - min(dates)).days
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker=".")
    ax = plt.gca()
    locator, formatter = locator_and_formater(span=span)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=30)
    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.tight_layout()
    plt.savefig(f"img/{save_name}.png", dpi=300)


def multiplot(datasets: list, title="default", x_axis="default", y_axis="default", save_name="default", start_date="2021-06-01"):
    plt.figure(figsize=(10, 5))
    all_dates = []
    
    if start_date:
        start_date_dt = datetime.fromisoformat(start_date)
    else:
        start_date_dt = None
    
    for data_list, label in datasets:
        filtered_data = [(datetime.fromisoformat(d), c) for d, c in data_list
                        if not start_date_dt or datetime.fromisoformat(d) >= start_date_dt]
        dates, counts = zip(*filtered_data)
        if len(dates) > 1:
            dates = dates[:-1]
            counts = counts[:-1]
        all_dates.extend(dates)
        plt.plot(dates, counts, label=label, marker=".")
    
    span = (max(all_dates) - min(all_dates)).days
    locator, formatter = locator_and_formater(span=span)
    ax = plt.gca()
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(rotation=30)
    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"img/{save_name}.png", dpi=300)


def plot_projects(data, title="default", save_name="default", x_axis="default", y_axis="default"):
    projects = list(data.keys())
    values = list(data.values())
    plt.figure(figsize=(12, 6))
    plt.bar(projects, values)
    plt.xticks(rotation=40, ha="right")
    plt.ylabel(y_axis)
    plt.xlabel(x_axis)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f"img/{save_name}", dpi=300)