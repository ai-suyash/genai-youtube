from pydantic import BaseModel

class PodcastSpeaker(BaseModel):
    """A model for a podcast speaker, including their ID, name, and role."""
    speaker_id: str
    name: str
    role: str

class Segment(BaseModel):
    """A model for a 'main_segment', which includes a title."""
    title: str
    script_points: list[str]

class PodcastEpisodePlan(BaseModel):
    """Represents the entire episode, containing a title and a list of segments."""
    episode_title: str
    speakers: list[PodcastSpeaker]
    segments: list[Segment]