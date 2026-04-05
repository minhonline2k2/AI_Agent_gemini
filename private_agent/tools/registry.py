"""tools/registry.py - Danh sach tool cho phep (allowlist)"""

TOOL_REGISTRY = {
    "get_hostname":              {"timeout": 5,  "description": "Lay hostname"},
    "get_ip_addr":               {"timeout": 5,  "description": "Lay IP addresses"},
    "get_routes":                {"timeout": 5,  "description": "Lay routing table"},
    "get_listening_ports":       {"timeout": 10, "description": "Lay danh sach port dang listen"},
    "get_disk_usage":            {"timeout": 10, "description": "Lay disk usage"},
    "get_memory_usage":          {"timeout": 5,  "description": "Lay memory usage"},
    "get_top_cpu_processes":     {"timeout": 10, "description": "Lay top CPU processes"},
    "get_systemd_service_status":{"timeout": 10, "description": "Lay trang thai 1 systemd service"},
    "get_supervisor_status":     {"timeout": 10, "description": "Lay trang thai supervisor"},
    "nginx_config_test":         {"timeout": 10, "description": "Test nginx config"},
    "tail_log":                  {"timeout": 15, "description": "Doc N dong cuoi cua log file"},
    "http_health_check_internal":{"timeout": 10, "description": "Kiem tra health endpoint"},
}

def is_allowed(tool_name: str) -> bool:
    return tool_name in TOOL_REGISTRY

def get_timeout(tool_name: str) -> int:
    return TOOL_REGISTRY.get(tool_name, {}).get("timeout", 30)
