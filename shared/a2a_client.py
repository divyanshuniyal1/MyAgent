# shared/a2a_client.py

import uuid

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.client.helpers import create_text_message_object
from a2a.types import SendMessageRequest, MessageSendParams
from shared.config import AGENT_URLS


async def call_agent(agent_name: str, message: str, user_id: str, history: list = None) -> str:
    if agent_name not in AGENT_URLS:
        raise ValueError(f"Unknown agent: {agent_name}")

    base_url = AGENT_URLS[agent_name]

    async with httpx.AsyncClient(timeout=30.0) as http:
        # Resolve agent card
        resolver = A2ACardResolver(http, base_url)
        agent_card = await resolver.get_agent_card()

        # Build client from card (uses JSON-RPC transport automatically)
        client = A2AClient(httpx_client=http, agent_card=agent_card)

        # Build message
        msg_obj = create_text_message_object(content=message)
        # Attach user_id in metadata
        msg_obj.metadata = {"user_id": user_id}

        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=msg_obj)
        )

        response = await client.send_message(request)

    # Extract text from response
    try:
        result = response.root.result
        # Could be a Message or Task
        if hasattr(result, "parts"):
            from a2a.utils import get_message_text
            return get_message_text(result)
        elif hasattr(result, "status") and hasattr(result.status, "message"):
            from a2a.utils import get_message_text
            return get_message_text(result.status.message)
    except Exception:
        pass
    return str(response)