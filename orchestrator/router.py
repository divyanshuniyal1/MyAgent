# orchestrator/router.py
# Uses agno (https://github.com/agno-agi/agno) for agentic orchestration.
# Each sub-agent is wrapped as an agno Tool that dispatches via A2A protocol.

import os
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from shared.a2a_client import call_agent


def _build_agent(user_id: str) -> Agent:
    """Build a fresh agno Agent per request so user_id is bound into each tool."""

    @tool(name="call_math_agent", description="Handle math / arithmetic queries")
    async def _math(message: str) -> str:
        return await call_agent("math", message, user_id)

    @tool(name="call_text_agent", description="Handle text processing / general queries")
    async def _text(message: str) -> str:
        return await call_agent("text", message, user_id)

    @tool(name="call_expense_agent", description="Handle expense tracking queries")
    async def _expense(message: str) -> str:
        return await call_agent("expense", message, user_id)

    @tool(name="call_time_agent", description="Handle time / date queries")
    async def _time(message: str) -> str:
        return await call_agent("time", message, user_id)

    return Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
        tools=[_math, _text, _expense, _time],
        instructions=(
            "You are an orchestration agent. Route user queries to the correct "
            "sub-agent tools. You may call multiple tools when the query has "
            "multiple intents. After receiving tool results, compose a final answer."
        ),
        markdown=False,
    )


async def run_orchestrator(user_id: str, message: str, history: list) -> dict:
    """Run the agno agent and return response + list of agents called."""
    agent = _build_agent(user_id)

    # Prepend recent history as context
    prompt = message
    if history:
        ctx = "\n".join(f"{h['role'].upper()}: {h['content']}" for h in history[-6:])
        prompt = f"[Conversation history]\n{ctx}\n\n[New message]\n{message}"

    run_response = await agent.arun(prompt)

    # Collect which agents were actually invoked
    agents_called = []
    if run_response.messages:
        for m in run_response.messages:
            tool_calls = getattr(m, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    fn = getattr(tc, "function", tc)
                    name = getattr(fn, "name", None)
                    if name:
                        key = name.replace("call_", "").replace("_agent", "")
                        if key not in agents_called:
                            agents_called.append(key)

    return {"response": run_response.content, "agents_called": agents_called}