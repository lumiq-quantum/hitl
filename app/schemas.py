from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AgentBase(BaseModel):
    name: str
    type: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class AgentOut(AgentBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class ContextBase(BaseModel):
    name: str
    description: Optional[str] = None

class ContextCreate(ContextBase):
    pass

class ContextOut(ContextBase):
    id: int
    class Config:
        orm_mode = True

class QuestionBase(BaseModel):
    question_text: str
    answer_type: str
    possible_answers: Optional[List[str]] = None

class QuestionCreate(QuestionBase):
    agent_id: int

class QuestionOut(QuestionBase):
    id: int
    agent_id: int
    created_at: datetime
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    persona: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

class ChannelBase(BaseModel):
    name: str
    type: str  # e.g., whatsapp, slack, email, sms, teams
    config: Optional[dict] = None  # credentials/settings for the channel

class ChannelCreate(ChannelBase):
    pass

class ChannelOut(ChannelBase):
    id: int
    class Config:
        from_attributes = True

class UserChannelBase(BaseModel):
    user_id: int
    channel_id: int
    contact_details: dict  # e.g., phone, email, slack_id, etc
    is_preferred: Optional[bool] = False

class UserChannelCreate(UserChannelBase):
    pass

class UserChannelOut(UserChannelBase):
    id: int
    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    external_session_id: Optional[str] = None
    user_id: Optional[int] = None

class SessionCreate(SessionBase):
    pass

class SessionOut(SessionBase):
    id: UUID
    current_step: int
    status: str
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True

class SessionQuestionBase(BaseModel):
    session_id: UUID
    question_id: int
    channel_id: int

class SessionQuestionCreate(SessionQuestionBase):
    pass

class SessionQuestionOut(SessionQuestionBase):
    id: int
    sent_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None
    response: Optional[str] = None
    status: str
    class Config:
        orm_mode = True

class ReminderBase(BaseModel):
    session_question_id: int
    channel_id: int

class ReminderCreate(ReminderBase):
    pass

class ReminderOut(ReminderBase):
    id: int
    reminder_sent_at: Optional[datetime] = None
    rerouted: bool
    class Config:
        orm_mode = True

class HITLLogBase(BaseModel):
    session_id: UUID
    event_type: str
    payload: Any

class HITLLogCreate(HITLLogBase):
    pass

class HITLLogOut(HITLLogBase):
    id: int
    timestamp: datetime
    class Config:
        orm_mode = True