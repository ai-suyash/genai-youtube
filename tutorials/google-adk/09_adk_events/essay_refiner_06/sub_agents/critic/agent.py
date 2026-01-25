from google.adk.agents import Agent
from .prompts import CRITIC_INSTRUCTION

critic = Agent(
    name="Critic",
    model="gemini-2.5-pro",
    description="Evaluates essay quality and provides feedback",
    instruction=CRITIC_INSTRUCTION,
    output_key="critique"  # Saves feedback to state
)
