from google.adk.tools.tool_context import ToolContext

# ===== Exit Tool for Loop Termination =====
def exit_loop(tool_context: ToolContext):
    """
    Signal that the essay refinement is complete.
    Called by the refiner when critic approves the essay.
    """
    print(f"  [Exit Loop] Called by {tool_context.agent_name} - Essay approved!")

    tool_context.actions.escalate = True # Signal to stop looping
    
    # Return a minimal valid content part so the backend always produces a valid LlmResponse
    return {"text": "Loop exited successfully. The agent has determined the task is complete."}
