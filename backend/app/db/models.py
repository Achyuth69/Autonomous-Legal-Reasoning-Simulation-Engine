from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base


class CaseStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cases = relationship("LegalCase", back_populates="user")


class LegalCase(Base):
    __tablename__ = "legal_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    case_number = Column(String(100), unique=True, index=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.PENDING)
    
    # Case Details
    description = Column(Text)
    jurisdiction = Column(String(255))
    case_type = Column(String(100))  # civil, criminal, constitutional, etc.
    
    # Extracted Information
    facts = Column(JSON)  # List of facts
    parties = Column(JSON)  # Plaintiff, defendant, etc.
    timeline = Column(JSON)  # Event timeline
    legal_issues = Column(JSON)  # Identified legal issues
    
    # Analysis Results
    applicable_statutes = Column(JSON)
    relevant_precedents = Column(JSON)
    plaintiff_arguments = Column(JSON)
    defendant_arguments = Column(JSON)
    
    # Decision
    judgment = Column(Text)
    verdict = Column(String(100))
    legal_reasoning = Column(Text)
    
    # Scoring
    confidence_score = Column(Float)
    risk_score = Column(Float)
    plaintiff_strength = Column(Float)
    defendant_strength = Column(Float)
    
    # Metadata
    document_path = Column(String(500))
    processing_time = Column(Float)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    user = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case")
    agent_logs = relationship("AgentLog", back_populates="case")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt
    file_size = Column(Integer)  # bytes
    extracted_text = Column(Text)
    page_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("LegalCase", back_populates="documents")


class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(100))
    input_data = Column(JSON)
    output_data = Column(JSON)
    reasoning_trace = Column(JSON)
    execution_time = Column(Float)
    status = Column(String(50))  # success, failed, pending
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("LegalCase", back_populates="agent_logs")


class Citation(Base):
    __tablename__ = "citations"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("legal_cases.id"))
    citation_text = Column(String(500), nullable=False)
    citation_type = Column(String(50))  # statute, case_law, regulation
    jurisdiction = Column(String(255))
    year = Column(Integer)
    is_verified = Column(Integer, default=0)
    verification_source = Column(String(500))
    relevance_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
