from google.adk.agents import Agent
from . import prompt
from podcast_transcript_agent.models.podcast_transcript import PodcastTranscript

podcast_transcript_writer_agent = Agent( 
    name="podcast_transcript_writer_agent",
    model="gemini-2.5-flash",
    description="Writes the podcast transcript based on the podcast plan",
    instruction=prompt.PODCAST_TRANSCRIPT_WRITER_PROMPT,
    output_schema=PodcastTranscript,
    output_key="podcast_episode_transcript"
 )