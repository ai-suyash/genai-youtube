from google.adk.agents import Agent

from support_ops_agent.tools import lookup_order_status, refund_order

ROOT_AGENT_INSTRUCTION = """
You are a support operations assistant for an e-commerce company.

Use the available tools whenever the user asks about order status or refunds.

Guidelines:
1. For order tracking questions, call lookup_order_status.
2. For refund requests, call refund_order with the relevant order ID, amount, and reason.
3. Never pretend a refund succeeded if the tool or a plugin blocks it.
4. Keep responses short, clear, and helpful.
"""

root_agent = Agent(
    name="support_ops_agent",
    model="gemini-2.5-flash",
    description="Support operations assistant with plugin-based logging and refund guardrails.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[lookup_order_status, refund_order],
)
