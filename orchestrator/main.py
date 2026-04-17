# orchestrator/main.py

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from shared.auth_middleware import get_current_user
from orchestrator.chat import handle_chat
from tracing.phoenix_setup import init_tracing
from memory.db import init_db

app = FastAPI()

init_db()
init_tracing()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(req: ChatRequest, user=Depends(get_current_user)):
    user_id = user["sub"]
    result = await handle_chat(user_id, req.message)
    return result