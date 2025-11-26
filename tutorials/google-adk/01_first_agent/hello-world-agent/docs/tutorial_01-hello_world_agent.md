## Overview

Build your first AI agent with Google Agent Development Kit (ADK). This tutorial starts from absolute zero - you'll create a simple conversational agent that can chat with users. No prior ADK experience needed!

## Prerequisites

* Python 3.9+ installed on your system
* Google API key - Get one free at [Google AI Studio](https://aistudio.google.com/app/apikey)


## Use Case

We're building a friendly AI assistant that:

* Greets users warmly
* Answers general questions conversationally
* Has no special tools yet (just pure conversation)

This is the foundation - every ADK agent starts here!

## Step-by-Step Setup

### Step 0: Setup virtual env (optional)

Create a Python virtual environment:

`python -m venv .venv`

*Note: The leading dot in .venv that indicates the folder is hidden by default*

Activate virtual env

* Windows: `.venv\Scripts\activate.bat`
* MacOS: `source .venv/bin/activate`

### Step 1: Installation

Open your terminal and install ADK:

`pip install google-adk`

This installs the complete ADK toolkit including the Dev UI, CLI tools, and all dependencies.

### Step 2: Create Project Structure

Run the adk create command to start a new agent project.

`adk create hello_agent`


The created agent project has the following structure, with the `agent.py` file containing the main control code for the agent.

```
hello_agent/
├── __init__.py    # Makes this a Python package
├── agent.py       # Your agent definition
└── .env          # Authentication credentials
```

### Step 3: Configure Authentication

Open `.env` in your text editor and add your Google AI Studio API key:

**hello_agent/.env**
```
# Using Google AI Studio (recommended for learning)
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your-api-key-here
```

Replace `your-api-key-here` with your actual API key from [Google AI Studio](https://aistudio.google.com/app/apikey).


## Step 4: Define Your Agent

Open `agent.py` and create your agent

```
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-2.5-flash',
    name='hello_assistant',
    description='A friendly AI assistant for general conversation',
    instruction=(
        "You are a warm and helpful assistant. "
        "Greet users enthusiastically and answer their questions clearly. "
        "Be conversational and friendly!"
    )
)
```

**Note** : `root_agent`: MUST use this exact variable name - ADK looks for it!


## Step 5: Run Your Agent

* Navigate to the parent directory of hello_agent:

```
cd ..  # Go up one level, so you're in the folder that contains hello_agent/
```
<br>

* Launch the interactive development interface:

```
adk web
```

This starts a web server. Open your browser to `http://localhost:8000` and:

1. **Select your agent**: Choose "hello_agent" from the dropdown in the top-left
2. **Start chatting**: Type a message in the chat box
3. **Explore Events tab**: Click "Events" on the left to see exactly what the LLM received and returned

Try these prompts:

* "Hello!"
* "What can you help me with?"


### Understanding What's Happening

When you send a message to your agent:

* `ADK packages your message` along with the agent's instructions

* `Sends it to Gemini`(the LLM specified in model)

* `Gemini generates a response` based on the instructions

* `ADK returns the response` to you

**Use the Events tab** in the Dev UI to see this flow in detail - it shows you the exact prompts and responses!

