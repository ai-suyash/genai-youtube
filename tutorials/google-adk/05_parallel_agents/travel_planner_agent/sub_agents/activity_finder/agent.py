from google.adk.agents import Agent
from .prompts import ACTIVITY_FINDER_INSTRUCTION

activity_finder = Agent(
    name="activity_finder",
    model="gemini-2.5-flash",
    description="Finds activities and attractions",
    instruction=ACTIVITY_FINDER_INSTRUCTION,
    output_key="activity_options"  # Saves to state
)
