#!/usr/bin/env python3
"""
REAL System Monitoring - Actual System Metrics
Unlike the mock data in complete_production_app.py
"""

import os
import subprocess
import psutil

def get_real_system_metrics():
    """Get actual system metrics from the host"""

    # Real CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)

    # Real memory usage
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    memory_used_gb = memory.used / (1024**3)
    memory_total_gb = memory.total / (1024**3)

    # Real disk usage
    disk = psutil.disk_usage("/")
    disk_percent = (disk.used / disk.total) * 100
    disk_used_gb = disk.used / (1024**3)
    disk_total_gb = disk.total / (1024**3)

    # Real network I/O
    net_io = psutil.net_io_counters()

    # Real process count
    process_count = len(psutil.pids())

    # Real load average (Linux only)
    try:
        load_avg = os.getloadavg()
    except Exception:
        load_avg = [0.0, 0.0, 0.0]

    # Real uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "usage_percent": round(cpu_percent, 2),
            "count": psutil.cpu_count(),
            "load_average": {
                "1min": round(load_avg[0], 2),
                "5min": round(load_avg[1], 2),
                "15min": round(load_avg[2], 2),
            },
        },
        "memory": {
            "usage_percent": round(memory_percent, 2),
            "used_gb": round(memory_used_gb, 2),
            "total_gb": round(memory_total_gb, 2),
            "available_gb": round(memory.available / (1024**3), 2),
        },
        "disk": {
            "usage_percent": round(disk_percent, 2),
            "used_gb": round(disk_used_gb, 2),
            "total_gb": round(disk_total_gb, 2),
            "free_gb": round((disk.total - disk.used) / (1024**3), 2),
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        },
        "system": {
            "process_count": process_count,
            "uptime_seconds": int(uptime_seconds),
            "uptime_hours": round(uptime_seconds / 3600, 2),
        },
    }


def get_real_docker_stats():
    """Get real Docker container metrics if available"""
    try:
        result = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            containers = [            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 4:
                        containers.append({
                                "name": parts[0],
                                "cpu_percent": parts[1],
                                "memory_usage": parts[2],
                                "network_io": parts[3],
                            }
                        )
            return containers
        else:
            return {"error": "Docker not available or no containers running"}

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"error": "Docker not available"}


def get_real_flask_app_stats():
    """Get real stats about our Flask application"""
    try:
        # Check if our Flask app process is running
        flask_processes = [        for proc in psutil.process_iter(
            ["pid", "name", "cmdline", "cpu_percent", "memory_info"]
        ):
            try:
                if "complete_production_app.py" in " ".join(proc.info["cmdline"] or []):
                    flask_processes.append({
                            "pid": proc.info["pid"],
                            "cpu_percent": proc.info["cpu_percent"],
                            "memory_mb": round(
                                proc.info["memory_info"].rss / (1024 * 1024), 2
                            ),
                            "status": proc.status(),
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "flask_processes": flask_processes,
            "total_processes": len(flask_processes),
            "is_running": len(flask_processes) > 0,
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("🔍 REAL System Monitoring Report")
    print("=" * 50)

    # Real system metrics
    real_metrics = get_real_system_metrics()
    print("📊 Real System Metrics:")
    print("  CPU Usage: {real_metrics['cpu']['usage_percent']}%")
    print(
        "  Memory Usage: {real_metrics['memory']['usage_percent']}% ("
        "{real_metrics['memory']['used_gb']:.1f}GB/{real_metrics['memory']['total_gb']:.1f}GB)"
    )
    print(
        "  Disk Usage: {real_metrics['disk']['usage_percent']}% ("
        "{real_metrics['disk']['used_gb']:.1f}GB/{real_metrics['disk']['total_gb']:.1f}GB)"
    )
    print("  Load Average: {real_metrics['cpu']['load_average']['1min']}")
    print("  Processes: {real_metrics['system']['process_count']}")
    print("  Uptime: {real_metrics['system']['uptime_hours']:.1f} hours")

    print("\n🐳 Docker Status:")
    docker_stats = get_real_docker_stats()
    if isinstance(docker_stats, list):
        for container in docker_stats:
            print(
                "  {container['name']}: CPU {container['cpu_percent']}, "
                "Memory {container['memory_usage']}"
            )
    else:
        print("  {docker_stats}")

    print("\n🌐 Flask App Status:")
    flask_stats = get_real_flask_app_stats()
    if flask_stats["is_running"]:
        for proc in flask_stats["flask_processes"]:
            print(
                "  PID {proc['pid']}: CPU {proc['cpu_percent']}%,
                    Memory {proc['memory_mb']}MB"
            )
    else:
        print("  Flask app not running")

    print("\n📄 Full JSON Output:")
    combined_data = {
        "real_system": real_metrics,
        "docker_containers": docker_stats,
        "flask_application": flask_stats,
    }
    print(json.dumps(combined_data, indent=2))
