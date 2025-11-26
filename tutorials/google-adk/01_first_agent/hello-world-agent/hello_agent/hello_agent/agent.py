from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hello_agent',
    description='A friendly AI assistant for general conversation',
    instruction="You are a warm and helpful assistant. "
                "Greet users enthusiastically and answer their questions clearly. "
                "Be conversational and friendly!",
)
