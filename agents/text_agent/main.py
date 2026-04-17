# agents/text_agent/main.py

import os
from openai import AsyncOpenAI
from a2a.server.apps.jsonrpc import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.client.helpers import create_text_message_object
from a2a.utils import get_message_text

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class TextAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = get_message_text(context.message)

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful text assistant. Answer clearly and concisely."},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
        )
        answer = response.choices[0].message.content.strip()

        await event_queue.enqueue_event(create_text_message_object(content=answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


agent_card = AgentCard(
    name="TextAgent",
    description="Handles general text and language tasks",
    url="http://text_agent:8002/",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[AgentSkill(id="text", name="Text", description="...", tags=["text"])],
    version="1.0.0",
)

handler = DefaultRequestHandler(agent_executor=TextAgentExecutor(), task_store=InMemoryTaskStore())
app = A2AFastAPIApplication(agent_card=agent_card, http_handler=handler).build()