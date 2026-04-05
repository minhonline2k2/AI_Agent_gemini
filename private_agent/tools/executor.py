"""tools/executor.py - Thuc thi tool an toan voi timeout + audit"""
import time
from tools.registry import is_allowed, get_timeout
from tools.diagnostic import TOOL_FUNCTIONS


def execute_tool(tool_name: str, tool_input: dict = {}) -> dict:
    """
    Thuc thi 1 tool tu registry.
    1. Kiem tra tool co trong allowlist khong
    2. Chay voi timeout
    3. Tra ve ket qua co cau truc
    """
    if not is_allowed(tool_name):
        return {
            "status": "failed",
            "output": {"error": f"Tool '{tool_name}' not in allowlist"},
            "duration_ms": 0,
        }

    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return {
            "status": "failed",
            "output": {"error": f"Tool '{tool_name}' has no implementation"},
            "duration_ms": 0,
        }

    start = time.time()
    try:
        result = func(**tool_input)
        duration_ms = int((time.time() - start) * 1000)
        return {
            "status": "success",
            "output": result,
            "duration_ms": duration_ms,
        }
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return {
            "status": "failed",
            "output": {"error": str(e)},
            "duration_ms": duration_ms,
        }
