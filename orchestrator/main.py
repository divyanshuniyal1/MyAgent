# orchestrator/main.py
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from shared.auth_middleware import get_current_user
from orchestrator.chat import handle_chat
from tracing.phoenix_setup import init_tracing
from memory.db import init_db

app = FastAPI()
init_db()
init_tracing()


def jsonrpc_result(id: str, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def jsonrpc_error(id: str, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


@app.post("/chat")
async def chat(request: Request):
    body = await request.json()

    # Validate JSON-RPC structure
    if body.get("jsonrpc") != "2.0":
        return JSONResponse(jsonrpc_error(body.get("id"), -32600, "Invalid Request: missing jsonrpc 2.0"))

    if body.get("method") != "chat":
        return JSONResponse(jsonrpc_error(body.get("id"), -32601, "Method not found"))

    rpc_id = body.get("id", str(uuid.uuid4()))
    params = body.get("params", {})
    message = params.get("message")

    if not message:
        return JSONResponse(jsonrpc_error(rpc_id, -32602, "Invalid params: 'message' is required"))

    # Auth — extract Bearer token manually since we're not using Depends
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(jsonrpc_error(rpc_id, -32000, "Unauthorized: missing token"))

    from auth.jwt_utils import decode_token
    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    if payload is None:
        return JSONResponse(jsonrpc_error(rpc_id, -32000, "Unauthorized: invalid or expired token"))

    user_id = payload["sub"]

    try:
        result = await handle_chat(user_id, message)
        return JSONResponse(jsonrpc_result(rpc_id, result))
    except Exception as e:
        return JSONResponse(jsonrpc_error(rpc_id, -32603, str(e)))