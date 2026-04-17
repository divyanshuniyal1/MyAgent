# orchestrator/chat.py

from orchestrator.router import run_orchestrator
from memory.memory_service import save_message, get_last_messages


async def handle_chat(user_id: str, message: str) -> dict:
    save_message(user_id, message, "user", "orchestrator")

    history = get_last_messages(user_id)

    result = await run_orchestrator(user_id, message, history)

    save_message(user_id, result["response"], "assistant", "orchestrator")

    return result