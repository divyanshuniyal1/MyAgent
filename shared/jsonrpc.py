# shared/jsonrpc.py

import uuid


def build_request(method: str, params: dict) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,
        "params": params,
    }


def parse_response(data: dict):
    if "error" in data:
        raise Exception(f"JSON-RPC error {data['error']['code']}: {data['error']['message']}")
    return data.get("result")