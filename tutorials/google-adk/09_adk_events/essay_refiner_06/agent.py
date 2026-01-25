from google.adk.agents import LoopAgent, SequentialAgent
from .sub_agents import (critic, initial_writer, refiner)


# =====================================================
# PHASE 2: Refinement Loop (Runs REPEATEDLY)
# =====================================================

# ===== Create Refinement Loop =====
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[
        critic,   # Step 1: Evaluate
        refiner   # Step 2: Improve OR exit
    ],
    max_iterations=5  # Safety limit - stops after 5 loops max
)

# =====================================================
# COMPLETE SYSTEM: Initial Draft + Refinement Loop
# =====================================================
essay_refinement_system = SequentialAgent(
    name="EssayRefinementSystem",
    sub_agents=[
        initial_writer,    # Phase 1: Write first draft (once)
        refinement_loop    # Phase 2: Refine iteratively (loop)
    ],
    description="Complete essay writing and refinement system"
)

# MUST be named root_agent for ADK
root_agent = essay_refinement_system
