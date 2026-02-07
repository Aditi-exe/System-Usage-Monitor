import psutil
import rich, pretty

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

if __name__ == "__main__":
    cpu_usage = get_cpu_usage()
    print(f"Current CPU Usage: {cpu_usage}%")