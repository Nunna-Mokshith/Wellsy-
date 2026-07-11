"""
Wellsy Tools — System Control
Volume, brightness, battery, system info.
"""
import psutil
from datetime import datetime
from langchain_core.tools import tool


@tool
def get_system_info() -> str:
    """Get current system stats — CPU, RAM, disk usage, battery."""
    cpu_pct = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk_c = psutil.disk_usage('C:\\')
    disk_d = None
    try:
        disk_d = psutil.disk_usage('D:\\')
    except FileNotFoundError:
        pass

    battery = psutil.sensors_battery()

    lines = [
        f"⚡ CPU: {cpu_pct}%",
        f"🧠 RAM: {ram.percent}% used ({ram.used // (1024**3):.1f}/{ram.total // (1024**3):.1f} GB)",
        f"💾 C: Drive: {disk_c.percent}% used ({disk_c.free // (1024**3)} GB free)",
    ]

    if disk_d:
        lines.append(f"💾 D: Drive: {disk_d.percent}% used ({disk_d.free // (1024**3)} GB free)")

    if battery:
        plug_status = "🔌 plugged in" if battery.power_plugged else "🔋 on battery"
        lines.append(f"🔋 Battery: {battery.percent}% ({plug_status})")
        if not battery.power_plugged and battery.secsleft > 0:
            hours = battery.secsleft // 3600
            mins = (battery.secsleft % 3600) // 60
            lines.append(f"⏱️ Time remaining: ~{hours}h {mins}m")

    lines.append(f"🕐 Time: {datetime.now().strftime('%I:%M %p, %B %d')}")

    return "\n".join(lines)


@tool
def get_running_processes(sort_by: str = "memory") -> str:
    """List top processes by CPU or memory usage. sort_by: 'cpu' or 'memory'."""
    procs = []
    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_info']):
        try:
            info = proc.info
            if info['name'] and info['memory_info']:
                procs.append({
                    'name': info['name'],
                    'cpu': info['cpu_percent'] or 0,
                    'mem_mb': info['memory_info'].rss / (1024 * 1024),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if sort_by == "cpu":
        procs.sort(key=lambda x: x['cpu'], reverse=True)
    else:
        procs.sort(key=lambda x: x['mem_mb'], reverse=True)

    lines = []
    for p in procs[:15]:
        lines.append(f"  {p['name']:<30} CPU: {p['cpu']:>5.1f}%  RAM: {p['mem_mb']:>7.1f} MB")

    header = f"Top 15 processes by {'CPU' if sort_by == 'cpu' else 'Memory'}:\n"
    return header + "\n".join(lines)


@tool
def set_volume(level: int) -> str:
    """Set system volume to a specific level (0-100)."""
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        import ctypes

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

        # pycaw uses scalar 0.0-1.0
        scalar = max(0, min(100, level)) / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)
        return f"Volume set to {level}% 🔊"
    except ImportError:
        return "Volume control isn't available right now — pycaw might need to be installed."
    except Exception as e:
        return f"Couldn't change the volume: {e}"


@tool
def set_brightness(level: int) -> str:
    """Set screen brightness (0-100)."""
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(max(0, min(100, level)))
        return f"Brightness set to {level}% ☀️"
    except ImportError:
        return "Brightness control isn't available — screen_brightness_control might need to be installed."
    except Exception as e:
        return f"Couldn't change brightness: {e}"


SYSTEM_TOOLS = [get_system_info, get_running_processes, set_volume, set_brightness]
