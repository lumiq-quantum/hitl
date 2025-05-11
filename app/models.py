from sqlalchemy import (
    Column, String, Integer, Boolean, ForeignKey,
    DateTime, Text, Enum, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid
import enum
from datetime import datetime

Base = declarative_base()

class ChannelEnum(enum.Enum):
    whatsapp = "WhatsApp"
    email = "Email"
    web = "Web"
    sms = "SMS"

class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("Question", back_populates="agent")

class Context(Base):
    __tablename__ = 'contexts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.id'))
    question_text = Column(Text, nullable=False)
    answer_type = Column(String(50), nullable=False)
    possible_answers = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.utcnow)
    agent = relationship("Agent", back_populates="questions")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    persona = Column(String(100), nullable=True)
    user_channels = relationship("UserChannel", back_populates="user")

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    type = Column(String(50), nullable=False)  # e.g., whatsapp, slack, email, sms, teams
    config = Column(JSONB, nullable=True)      # credentials/settings for the channel
    user_channels = relationship("UserChannel", back_populates="channel")

class UserChannel(Base):
    __tablename__ = 'user_channels'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    contact_details = Column(JSONB, nullable=False)  # e.g., phone, email, slack_id, etc
    is_preferred = Column(Boolean, default=False)
    user = relationship("User", back_populates="user_channels")
    channel = relationship("Channel", back_populates="user_channels")

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_session_id = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    current_step = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")

class SessionQuestion(Base):
    __tablename__ = 'session_questions'
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    sent_at = Column(DateTime)
    answered_at = Column(DateTime)
    response = Column(Text)
    status = Column(String(50), default="pending")
    session = relationship("Session")
    question = relationship("Question")
    channel = relationship("Channel")

class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    session_question_id = Column(Integer, ForeignKey("session_questions.id"))
    channel_id = Column(Integer, ForeignKey("channels.id"))
    reminder_sent_at = Column(DateTime)
    rerouted = Column(Boolean, default=False)
    session_question = relationship("SessionQuestion")
    channel = relationship("Channel")

class HITLLog(Base):
    __tablename__ = 'hitl_logs'
    id = Column(Integer, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"))
    event_type = Column(String(100))
    payload = Column(JSONB)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session")