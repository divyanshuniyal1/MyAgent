# agents/math_agent/main.py

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
    {"type": "function", "function": {"name": "add_numbers",      "description": "Add two numbers",      "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "subtract_numbers", "description": "Subtract two numbers", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "multiply_numbers", "description": "Multiply two numbers", "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
    {"type": "function", "function": {"name": "divide_numbers",   "description": "Divide two numbers",   "parameters": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}, "required": ["a", "b"]}}},
]


class MathAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = get_message_text(context.message)

        messages = [
            {"role": "system", "content": "You are a math assistant. Use tools to calculate."},
            {"role": "user", "content": user_text},
        ]
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=TOOLS, tool_choice="auto"
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            params = json.loads(tool_call.function.arguments)
            result = await call_mcp_tool(tool_call.function.name, params)
            answer = str(result)
        else:
            answer = msg.content.strip()

        await event_queue.enqueue_event(create_text_message_object(content=answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


agent_card = AgentCard(
    name="MathAgent",
    description="Handles arithmetic calculations",
    url="http://math_agent:8001/",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=AgentCapabilities(streaming=False),
    skills=[AgentSkill(id="math", name="Math", description="add, subtract, multiply, divide", tags=["math"])],
    version="1.0.0",
)

handler = DefaultRequestHandler(agent_executor=MathAgentExecutor(), task_store=InMemoryTaskStore())
app = A2AFastAPIApplication(agent_card=agent_card, http_handler=handler).build()