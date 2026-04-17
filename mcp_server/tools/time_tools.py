# mcp_server/tools/time_tools.py

from datetime import datetime


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")