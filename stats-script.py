import psutil
import rich
import subprocess
import os
import time
import sys
from rich.panel import Panel
from rich.pretty import Pretty
from rich.live import Live
from rich.layout import Layout

# opening a new terminal window:
if "--child" not in sys.argv:
    subprocess.Popen(
        [sys.executable, "stats-script.py", "--child"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    sys.exit()


# system functions:
# cpu usage:
def get_cpu_usage():
    cpu_core_count = psutil.cpu_count()
    total_cpu_usage = psutil.cpu_percent(interval=1)
    per_core_usage = psutil.cpu_percent(percpu=True)

    data = {
        "CPUs: ": cpu_core_count,
        "Total CPU Usage: ": f"{total_cpu_usage}%",
        "Per Core Usage: ": [f"{usage}%" for usage in per_core_usage],
    }

    return Panel(Pretty(data, expand_all=True), title="CPU", border_style="red")


# memory usage:
def get_memory_usage():
    mem = psutil.virtual_memory()
    data = {
        "Total Memory: ": f"{mem.total / (1024 ** 3):.2f} GB",
        "Used Memory: ": f"{mem.used / (1024 ** 3):.2f} GB",
        "Available Memory: ": f"{mem.available / (1024 ** 3):.2f} GB",
        "Memory Usage: ": f"{mem.percent}%",
    }
    return Panel(Pretty(data, expand_all=True), title="Memory", border_style="blue")


# disk usage:
def get_disk_usage():
    disk = psutil.disk_usage("/")
    data = {
        "Total Disk: ": f"{disk.total / (1024 ** 3):.2f} GB",
        "Used Disk: ": f"{disk.used / (1024 ** 3):.2f} GB",
        "Free Disk: ": f"{disk.free / (1024 ** 3):.2f} GB",
        "Disk Usage: ": f"{disk.percent}%",
    }
    return Panel(Pretty(data, expand_all=True), title="Disk", border_style="green")


# top processes:
def get_top_processes(n=10):
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    top_processes = processes[:n]
    return Panel(
        Pretty(top_processes, expand_all=True),
        title="Top Processes",
        border_style="yellow",
    )


# build layout:
def layout():

    layout = Layout()

    layout.split_column(Layout(name="top", ratio=1), Layout(name="bottom", ratio=1))

    layout["top"].split_row(Layout(name="cpu"), Layout(name="memory"))

    layout["bottom"].split_row(Layout(name="disk"), Layout(name="procs"))

    layout["cpu"].update(get_cpu_usage())
    layout["memory"].update(get_memory_usage())
    layout["disk"].update(get_disk_usage())
    layout["procs"].update(get_top_processes())

    return layout


# live update:
with Live(layout(), refresh_per_second=1, screen=True) as live:
    while True:
        time.sleep(1)
        live.update(layout())
