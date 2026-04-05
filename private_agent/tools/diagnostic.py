"""tools/diagnostic.py - 12 diagnostic tools (read-only, safe)"""
import subprocess
import socket
import urllib.request
import json


def run_cmd(cmd: list, timeout: int = 10) -> str:
    """Chay lenh shell an toan voi timeout"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out"
    except Exception as e:
        return f"ERROR: {str(e)}"


def get_hostname(**kwargs):
    return {"hostname": socket.gethostname()}

def get_ip_addr(**kwargs):
    output = run_cmd(["ip", "a", "show"])
    return {"ip_info": output[:2000]}

def get_routes(**kwargs):
    output = run_cmd(["ip", "route", "show"])
    return {"routes": output[:2000]}

def get_listening_ports(**kwargs):
    output = run_cmd(["ss", "-lntp"])
    return {"ports": output[:3000]}

def get_disk_usage(**kwargs):
    output = run_cmd(["df", "-h"])
    lines = output.strip().split("\
")
    disks = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 5:
            try:
                used_pct = float(parts[4].replace("%", ""))
                disks.append({"path": parts[5] if len(parts) > 5 else parts[0], "used_pct": used_pct})
            except: pass
    return {"disks": disks, "raw": output[:2000]}

def get_memory_usage(**kwargs):
    output = run_cmd(["free", "-m"])
    return {"memory": output[:1000]}

def get_top_cpu_processes(**kwargs):
    output = run_cmd(["ps", "aux", "--sort=-%cpu"])
    lines = output.strip().split("\
")[:15]
    return {"processes": "\
".join(lines)}

def get_systemd_service_status(service_name: str = "nginx", **kwargs):
    output = run_cmd(["systemctl", "status", service_name, "--no-pager"])
    return {"service": service_name, "status": output[:2000]}

def get_supervisor_status(**kwargs):
    output = run_cmd(["supervisorctl", "status"])
    return {"supervisor": output[:2000]}

def nginx_config_test(**kwargs):
    output = run_cmd(["nginx", "-t"])
    return {"nginx_test": output[:1000]}

def tail_log(log_path: str = "/var/log/syslog", lines: int = 100, **kwargs):
    # Chi cho phep doc tu cac thu muc an toan
    ALLOWED_PREFIXES = ["/var/log/", "/opt/", "/tmp/"]
    if not any(log_path.startswith(p) for p in ALLOWED_PREFIXES):
        return {"error": f"Path not allowed: {log_path}"}
    output = run_cmd(["tail", "-n", str(min(lines, 500)), log_path], timeout=15)
    return {"log_path": log_path, "lines": output[:5000]}

def http_health_check_internal(url: str = "http://localhost:80/health", **kwargs):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"url": url, "status_code": resp.status, "body": resp.read().decode()[:1000]}
    except Exception as e:
        return {"url": url, "error": str(e)}


# Map ten tool -> function
TOOL_FUNCTIONS = {
    "get_hostname": get_hostname,
    "get_ip_addr": get_ip_addr,
    "get_routes": get_routes,
    "get_listening_ports": get_listening_ports,
    "get_disk_usage": get_disk_usage,
    "get_memory_usage": get_memory_usage,
    "get_top_cpu_processes": get_top_cpu_processes,
    "get_systemd_service_status": get_systemd_service_status,
    "get_supervisor_status": get_supervisor_status,
    "nginx_config_test": nginx_config_test,
    "tail_log": tail_log,
    "http_health_check_internal": http_health_check_internal,
}
