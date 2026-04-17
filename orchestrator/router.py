# orchestrator/router.py
import os
import asyncio
import concurrent.futures
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import Toolkit
from shared.a2a_client import call_agent


class AgentTools(Toolkit):
    def __init__(self, user_id: str):
        super().__init__(name="agent_tools")
        self.user_id = user_id
        self.register(self.call_math_agent)
        self.register(self.call_text_agent)
        self.register(self.call_expense_agent)
        self.register(self.call_time_agent)

    def _run_async(self, coro):
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()

    def call_math_agent(self, message: str) -> str:
        """Handle math and arithmetic queries"""
        return self._run_async(call_agent("math", message, self.user_id))

    def call_text_agent(self, message: str) -> str:
        """Handle text processing and general queries"""
        return self._run_async(call_agent("text", message, self.user_id))

    def call_expense_agent(self, message: str) -> str:
        """Handle expense tracking queries"""
        return self._run_async(call_agent("expense", message, self.user_id))

    def call_time_agent(self, message: str) -> str:
        """Handle time and date queries"""
        return self._run_async(call_agent("time", message, self.user_id))


async def run_orchestrator(user_id: str, message: str, history: list) -> dict:
    agent = Agent(
        model=OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")),
        tools=[AgentTools(user_id=user_id)],
        instructions=(
            "You are an orchestration agent. Always use the provided tools to answer. "
            "NEVER answer math, time, expense, or text questions from your own knowledge. "
            "Always call the appropriate tool first, then return its result."
        ),
        tool_choice="auto",
        markdown=False,
    )

    prompt = message
    if history:
        ctx = "\n".join(f"{h['role'].upper()}: {h['content']}" for h in history[-6:])
        prompt = f"[Conversation history]\n{ctx}\n\n[New message]\n{message}"

    run_response = await agent.arun(prompt)

    # DEBUG - remove after confirming agents_called works
    if run_response.messages:
        for m in run_response.messages:
            print(f"MSG role={getattr(m, 'role', '?')} tool_calls={getattr(m, 'tool_calls', None)}")


    agents_called = []
    if run_response.messages:
        for m in run_response.messages:
            tool_calls = getattr(m, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    # tc is a dict, not an object
                    if isinstance(tc, dict):
                        name = tc.get("function", {}).get("name")
                    else:
                        fn = getattr(tc, "function", tc)
                        name = getattr(fn, "name", None)
                    if name:
                        key = name.replace("call_", "").replace("_agent", "")
                        if key not in agents_called:
                            agents_called.append(key)

    return {"response": run_response.content, "agents_called": agents_called}