from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class ModuleMetadata(Base):
    __tablename__ = "ModuleMetadata"

    module_id = Column(String, primary_key=True, index=True)
    source_document = Column(String, nullable=False)
    source = Column(String, nullable=False)
    domain_tags_json = Column(Text, nullable=False)
    warning_text = Column(Text, nullable=False)


class FlashcardPages(Base):
    __tablename__ = "FlashcardPages"

    page_id = Column(String, primary_key=True, index=True)
    module_id = Column(String, nullable=False, index=True)
    sequence_number = Column(Integer, nullable=False)
    page_title = Column(String, nullable=False)
    domain_tag = Column(String, nullable=False)
    page_content_json = Column(Text, nullable=False)


class SprintSessions(Base):
    __tablename__ = "SprintSessions"

    sprint_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=True)
    module_id = Column(String, nullable=False, index=True)
    start_timestamp = Column(String, nullable=True)
    end_timestamp = Column(String, nullable=True)
    remaining_time = Column(Integer, nullable=True)
    tab_switch_count = Column(Integer, default=0)
    is_paused = Column(Integer, default=0)
    completion_status = Column(String, nullable=True)


class LearningJourneyMap(Base):
    __tablename__ = "LearningJourney_Map"

    journey_id = Column(String, primary_key=True, index=True)
    sprint_id = Column(String, nullable=False, index=True)
    quiz_session_id = Column(String, nullable=True)