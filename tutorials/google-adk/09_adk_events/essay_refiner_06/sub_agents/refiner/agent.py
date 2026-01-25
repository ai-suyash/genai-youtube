from google.adk.agents import Agent
from ...tools import exit_loop
from .prompts import REFINER_INSTRUCTION

refiner = Agent(
    name="Refiner",
    model="gemini-2.5-pro",
    tools=[exit_loop],  # Provide exit tool!
    description="Improves essay based on critique or signals completion",
    instruction=REFINER_INSTRUCTION,
    output_key="current_essay"  # Overwrites essay with improved version!
)
