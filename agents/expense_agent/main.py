# agents/expense_agent/main.py

import os, json
from openai import AsyncOpenAI
from a2a.server.apps.jsonrpc import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.client.helpers import create_text_message_object
from a2a.utils import get_message_text
from shared.mcp_client import call_mcp_tool

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [
    {"type": "function", "function": {"name": "add_expense", "description": "Add an expense for a user", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}, "amount": {"type": "number"}, "description": {"type": "string"}}, "required": ["user_id", "amount", "description"]}}},
    {"type": "function", "function": {"name": "get_expenses", "description": "Get all expenses for a user", "parameters": {"type": "object", "properties": {"user_id": {"type": "integer"}}, "required": ["user_id"]}}},
]


class ExpenseAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = get_message_text(context.message)
        user_id = (context.message.metadata or {}).get("user_id", 1)

        messages = [
            {"role": "system", "content": "You are an expense tracking assistant. Use tools to add or retrieve expenses."},
            {"role": "user", "content": user_text},
        ]
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS, tool_choice="auto"
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            params = json.loads(tool_call.function.arguments)
            params.setdefault("user_id", user_id)
            result = await call_mcp_tool(tool_call.function.name, params)
            answer = str(result)
        else:
            answer = msg.content.strip()

        await event_queue.enqueue_event(create_text_message_object(content=answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


agent_card = AgentCard(
    name="ExpenseAgent",
    description="Tracks and retrieves user expenses",
    url="http://expense_agent:8003/",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[AgentSkill(id="expense", name="Expense", description="...", tags=["expense"])],
    version="1.0.0",
)

handler = DefaultRequestHandler(agent_executor=ExpenseAgentExecutor(), task_store=InMemoryTaskStore())
app = A2AFastAPIApplication(agent_card=agent_card, http_handler=handler).build()