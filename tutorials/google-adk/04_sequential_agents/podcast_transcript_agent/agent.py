from google.adk.agents import SequentialAgent
from .sub_agents.podcast_topics import podcast_topics_agent
from .sub_agents.podcast_episode_planner import podcast_episode_planner_agent
from .sub_agents.podcast_transcript_writer import (
    podcast_transcript_writer_agent,
)

podcast_transcript_agent = SequentialAgent(
    name="podcast_transcript_agent",
    description="Executes a sequence of podcast generation steps",
    sub_agents=[
        podcast_topics_agent,
        podcast_episode_planner_agent,
        podcast_transcript_writer_agent,
    ],
)

root_agent = podcast_transcript_agent