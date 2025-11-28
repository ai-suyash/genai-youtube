from google.adk.agents import Agent
from . import prompt
from podcast_transcript_agent.models.podcast_topics import PodcastTopics
    
podcast_topics_agent = Agent(
    name="podcast_topics_agent",
    model="gemini-2.5-flash",
    description="Extracts podcast topics from provided input",
    instruction= prompt.TOPIC_EXTRACTION_PROMPT,
    output_schema=PodcastTopics,
    output_key="podcast_topics"
)