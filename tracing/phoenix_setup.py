# tracing/phoenix_setup.py

import os
from phoenix.otel import register
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def init_tracing():
    # Register with org-hosted Phoenix dashboard
    register(
        project_name=os.getenv("PHOENIX_PROJECT_NAME", "MyAgent"),
        auto_instrument=True,
        batch=True,
        api_key=os.getenv("PHOENIX_API_KEY"),
        endpoint=os.getenv("PHOENIX_ENDPOINT", "https://phoenix-new.infoapps.io/v1/traces"),
    )

    # Instrument OpenAI calls
    OpenAIInstrumentor().instrument()

    # Instrument HTTP calls (A2A + MCP)
    HTTPXClientInstrumentor().instrument()

    print("Tracing initialized → sending to org Phoenix dashboard")
