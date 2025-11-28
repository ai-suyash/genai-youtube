from google.adk.agents import Agent
from . import prompt
from podcast_transcript_agent.models.podcast_plan import PodcastEpisodePlan


podcast_episode_planner_agent = Agent(
    name="podcast_episode_planner_agent",
    model="gemini-2.5-flash",
    description="Plans the podcast episode based on extracted topics",
    instruction=prompt.PODCAST_EPISODE_PLANNER_PROMPT,
    output_schema=PodcastEpisodePlan,
    output_key="podcast_episode_plan"
)