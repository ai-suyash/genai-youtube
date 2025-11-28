from pydantic import BaseModel

class SpeakerDialogue(BaseModel):
    """A model for a speaker's dialogue, including the speaker's ID and the text of the dialogue."""
    speaker_id: str
    text: str

class PodcastSegment(BaseModel):
    """A model for a podcast segment, which includes a title, start and end times of the segment (in seconds), and a list of speaker dialogues."""
    segment_title: str
    title: str
    start_time: float
    end_time: float
    speaker_dialogues: list[SpeakerDialogue]

class PodcastSpeaker(BaseModel):
    """A model for a podcast speaker, including their ID, name, and role."""
    speaker_id: str
    name: str
    role: str
    
class PodcastMetadata(BaseModel):
    """A model for the podcast's metadata, including the episode title, duration, and summary."""
    episode_title: str
    duration_seconds: int
    summary: str

class PodcastTranscript(BaseModel):
    """A model for a podcast transcript, which includes metadata, speakers, and segments."""
    metadata: PodcastMetadata  
    speakers: list[PodcastSpeaker]
    segments: list[PodcastSegment]