from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, default=generate_uuid)
    student_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="student")
    
    consent_date = Column(DateTime, nullable=True)
    pdpa_version = Column(String, nullable=True)
    withdrawn_date = Column(DateTime, nullable=True)

    # Profile statistics
    weak_topics = Column(Text, default="[]") # JSON list of strings
    missed_findings = Column(Text, default="[]") # JSON list of strings
    retention_scores = Column(Text, default="{}") # JSON dict
    session_count = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    last_active = Column(DateTime, nullable=True)
    learning_velocity = Column(String, default="stable")
    checkin_done_today = Column(Boolean, default=False)

    # Relationships
    sessions = relationship("Session", back_populates="student")
    flashcards = relationship("Flashcard", back_populates="student")
    case_results = relationship("CaseResult", back_populates="student")
    image_results = relationship("ImageResult", back_populates="student")


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    topic = Column(String, nullable=False)
    token_count = Column(Integer, default=0)
    model_used = Column(String, default="mock")
    created_at = Column(DateTime, default=utc_now)
    
    # Store messages as JSON string
    messages = Column(Text, default="[]")

    student = relationship("Student", back_populates="sessions")


class Flashcard(Base):
    __tablename__ = "flashcards"

    card_id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=True)
    
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    topic_tag = Column(String, nullable=False)
    
    # SM-2 / spaced repetition fields
    interval = Column(Integer, default=0)
    repetition = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    next_due_date = Column(DateTime, default=utc_now)
    created_at = Column(DateTime, default=utc_now)

    student = relationship("Student", back_populates="flashcards")


class CaseResult(Base):
    __tablename__ = "case_results"

    result_id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    case_id = Column(String, nullable=False)
    
    history_score = Column(Integer, default=0)
    investigations_score = Column(Integer, default=0)
    diagnosis_score = Column(Integer, default=0)
    management_score = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    
    history_feedback = Column(Text, nullable=True)
    investigations_feedback = Column(Text, nullable=True)
    diagnosis_feedback = Column(Text, nullable=True)
    management_feedback = Column(Text, nullable=True)
    overall_feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)

    student = relationship("Student", back_populates="case_results")


class ImageResult(Base):
    __tablename__ = "image_results"

    result_id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False)
    image_id = Column(String, nullable=False)
    
    score = Column(Integer, default=0)
    correct_findings = Column(Text, default="[]") # JSON list
    missed_findings = Column(Text, default="[]") # JSON list
    incorrect_findings = Column(Text, default="[]") # JSON list
    diagnosis_correct = Column(Boolean, default=False)
    feedback = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)

    student = relationship("Student", back_populates="image_results")
