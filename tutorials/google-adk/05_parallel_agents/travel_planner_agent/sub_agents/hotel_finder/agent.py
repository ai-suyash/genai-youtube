from google.adk.agents import Agent
from .prompts import HOTEL_FINDER_INSTRUCTION

hotel_finder = Agent(
    name="hotel_finder",
    model="gemini-2.5-flash",
    description="Searches for available hotels",
    instruction=HOTEL_FINDER_INSTRUCTION,
    output_key="hotel_options"  # Saves to state
)
