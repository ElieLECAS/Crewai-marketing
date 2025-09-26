from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/crewai_marketing")

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Modèles de base de données
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(200), nullable=False)
    goal = Column(Text, nullable=False)
    backstory = Column(Text)
    enabled_tools = Column(JSON, default=list)
    max_iter = Column(Integer, default=3)
    verbose = Column(Boolean, default=True)
    memory = Column(Boolean, default=False)
    allow_delegation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    crew_agents = relationship("CrewAgent", back_populates="agent")

class Crew(Base):
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    process_type = Column(String(50), default="sequential")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    crew_agents = relationship("CrewAgent", back_populates="crew")
    campaigns = relationship("Campaign", back_populates="crew")

class CrewAgent(Base):
    __tablename__ = "crew_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    crew_id = Column(Integer, ForeignKey("crews.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    order = Column(Integer, default=0)
    
    # Relations
    crew = relationship("Crew", back_populates="crew_agents")
    agent = relationship("Agent", back_populates="crew_agents")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    problem_statement = Column(Text, nullable=False)
    company_context = Column(Text)
    crew_id = Column(Integer, ForeignKey("crews.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relations
    crew = relationship("Crew", back_populates="campaigns")
    campaign_files = relationship("CampaignFile", back_populates="campaign")

class CampaignFile(Base):
    __tablename__ = "campaign_files"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), default="pdf")
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    campaign = relationship("Campaign", back_populates="campaign_files")

class AgentOutput(Base):
    __tablename__ = "agent_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    output_content = Column(Text, nullable=False)
    output_type = Column(String(50), default="text")  # text, markdown, json
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    campaign = relationship("Campaign")

# Fonction pour créer toutes les tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour initialiser la base de données
def init_db():
    create_tables()
    print("✅ Base de données initialisée avec succès")
