from google.adk.agents import Agent
from .prompts import FLIGHT_FINDER_INSTRUCTION

flight_finder = Agent(
    name="flight_finder",
    model="gemini-2.5-flash",
    description="Searches for available flights",
    instruction=FLIGHT_FINDER_INSTRUCTION,
    output_key="flight_options"  # Saves to state
)
