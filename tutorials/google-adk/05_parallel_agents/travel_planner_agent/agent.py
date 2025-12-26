from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from travel_planner_agent.sub_agents import (
    activity_finder,
    flight_finder,
    hotel_finder,
)

# ============================================================================
# FAN-OUT: PARALLEL DATA GATHERING
# ============================================================================

# Create the ParallelAgent for concurrent search
parallel_search = ParallelAgent(
    name="ParallelSearch",
    sub_agents=[
        flight_finder,
        hotel_finder,
        activity_finder
    ],  # All run AT THE SAME TIME!
    description="Searches flights, hotels, and activities concurrently"
)

# ============================================================================
# GATHER: SEQUENTIAL RESULT MERGING
# ============================================================================

# ===== Gather: Merge Results into Itinerary =====
itinerary_builder = Agent(
    name="itinerary_builder",
    model="gemini-2.5-flash",
    description="Combines all search results into a complete travel itinerary",
    instruction="""
    You are a travel planner. Create a complete, well-organized itinerary by 
    combining the search results below.

    **Available Flights:**
    {flight_options}

    **Available Hotels:**
    {hotel_options}

    **Recommended Activities:**
    {activity_options}

    Create a formatted itinerary that:
    1. Recommends the BEST option from each category (flights, hotel)
    2. Organizes activities into a day-by-day plan
    3. Includes estimated total cost
    4. Adds helpful travel tips

    Format beautifully with clear sections and markdown.

    """,
    output_key="final_itinerary"
)

# ============================================================================
# COMPLETE FAN-OUT/GATHER PIPELINE
# ============================================================================

# Combine parallel search with sequential merge
travel_planning_system = SequentialAgent(
    name="TravelPlanningSystem",
    sub_agents=[
        parallel_search,     # Step 1: Gather data in parallel (FAST!)
        itinerary_builder    # Step 2: Merge results (synthesis)
    ],
    description="Complete travel planning system with parallel search and itinerary building"
)

# MUST be named root_agent for ADK discovery
root_agent = travel_planning_system