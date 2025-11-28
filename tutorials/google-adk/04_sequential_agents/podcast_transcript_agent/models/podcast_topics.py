from pydantic import BaseModel

class Topic(BaseModel):
    """A model for a podcast topic, which includes a title, description, and key facts."""
    topic_name: str
    description: str
    key_facts: list[str]

class PodcastTopics(BaseModel):
    """A model for the main topic and sub-topics of a podcast episode."""
    main_topic: str
    sub_topics: list[Topic]