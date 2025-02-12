from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    english = Column(String, unique=True, nullable=False)
    transcription = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    selected = Column(Boolean, default=False)
    repetition_count = Column(Integer, default=0)
    translations = relationship(
        'Translation', back_populates='word', cascade='all, delete-orphan'
    )
    description = Column(String, nullable=True)
    audio_name = Column(String, nullable=True)
    api_status = Column(Integer, nullable=True)
    remember = Column(Boolean, default=True)

    def has_audio(self) -> bool:
        """Check if word has audio file"""
        return bool(self.audio_name)


class Translation(Base):
    __tablename__ = 'translations'

    id = Column(Integer, primary_key=True)
    russian = Column(String, nullable=False)
    word_id = Column(Integer, ForeignKey('words.id', ondelete='CASCADE'))
    word = relationship('Word', back_populates='translations')


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
