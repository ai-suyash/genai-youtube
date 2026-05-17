"""Dummy Agent Engine app for initial Terraform deployment.

This placeholder is replaced by CI/CD pipelines after initial creation.
"""

from google.adk.agents import Agent
from vertexai.agent_engines.templates.adk import AdkApp

agent = Agent(
    model="gemini-2.5-flash",
    name="dummy_agent",
    instruction="You are a placeholder agent.",
)

agent_engine = AdkApp(agent=agent)
