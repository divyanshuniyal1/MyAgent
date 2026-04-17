# shared/config.py

import os

# Base URLs
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8000")
MCP_URL = os.getenv("MCP_URL", "http://localhost:9000")

AGENT_URLS = {
    "math": os.getenv("MATH_AGENT_URL", "http://localhost:8001"),
    "text": os.getenv("TEXT_AGENT_URL", "http://localhost:8002"),
    "expense": os.getenv("EXPENSE_AGENT_URL", "http://localhost:8003"),
    "time": os.getenv("TIME_AGENT_URL", "http://localhost:8004"),
}