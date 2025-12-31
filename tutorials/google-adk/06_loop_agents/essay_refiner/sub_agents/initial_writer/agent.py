from google.adk.agents import Agent
from .prompts import INITIAL_WRITER_INSTRUCTION

initial_writer = Agent(
    name="InitialWriter",
    model="gemini-2.5-flash",
    description="Writes the first draft of an essay",
    instruction=INITIAL_WRITER_INSTRUCTION,
    output_key="current_essay"  # Saves to state
)
