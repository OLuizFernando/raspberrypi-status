import time
import datetime
import psutil
import subprocess
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


def classify_overall_score(score: float) -> str:
    if score <= 20:
        return "very idle"
    elif score <= 40:
        return "idle"
    elif score <= 60:
        return "normal"
    elif score <= 75:
        return "busy"
    elif score <= 90:
        return "high"
    else:
        return "stressed"


@app.get("/")
def get_root():
    return RedirectResponse("/docs")


@app.get("/status")
def get_status():
    cpu_percent = psutil.cpu_percent(interval=1)
    ram_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent

    # CPU:  50%
    # RAM:  30%
    # DISK: 20%
    score = cpu_percent * 0.5 + ram_percent * 0.3 + disk_percent * 0.2

    return {
        "overall": {"score": score, "status": classify_overall_score(score)},
        "cpu_percent": cpu_percent,
        "cpu_temp": psutil.sensors_temperatures()["cpu_thermal"][0][1],
        "ram_percent": ram_percent,
        "swap_percent": psutil.swap_memory().percent,
        "disk_percent": disk_percent,
        "uptime_seconds": time.time() - psutil.boot_time(),
    }


@app.get("/status/cpu")
def get_cpu_status():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_per_core": psutil.cpu_percent(interval=1, percpu=True),
        "cpu_temp": psutil.sensors_temperatures()["cpu_thermal"][0][1],
    }


@app.get("/status/memory")
def get_memory_status():
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    
    return {
        "ram": vm._asdict(),
        "swap": sm._asdict()
    }


@app.get("/status/disk")
def get_disk_status():
    partitions = psutil.disk_partitions()
    usage = {p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict() for p in partitions}
    
    return usage


@app.get("/status/network")
def get_network_status():
    return {iface: counters._asdict() for iface, counters in psutil.net_io_counters(pernic=True).items()}


@app.get("/status/uptime")
def get_uptime_status():
    seconds = time.time() - psutil.boot_time()
    human = str(datetime.timedelta(seconds=int(seconds)))
    return {"uptime_seconds": seconds, "uptime_human": human}
