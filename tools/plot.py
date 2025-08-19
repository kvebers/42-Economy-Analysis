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


def basic_plot(data_list, title="default", x_axis="default", y_axis="default", save_name="default"):
    dates = [datetime.fromisoformat(d) for d, _ in data_list]
    counts = [c for _, c in data_list]
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


def multiplot(datasets: list, title="default", x_axis="default", y_axis="default", save_name="default"):
    plt.figure(figsize=(10, 5))
    all_dates = []
    for data_list, label in datasets:
        dates = [datetime.fromisoformat(d) for d, _ in data_list]
        counts = [c for _, c in data_list]
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