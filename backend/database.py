import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()  # read the .env file

# Read the database connection string from .env. This project uses MySQL; if
# DATABASE_URL is missing, we fall back to a local SQLite file so the app still runs.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcp_crm.db")

# SQLite needs one extra argument; MySQL and other databases do not.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class Interaction(Base):
    """One row = one logged meeting/call/email with a doctor (HCP)."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), default="")
    interaction_type = Column(String(100), default="Meeting")
    date = Column(String(50), default="")
    time = Column(String(50), default="")
    attendees = Column(String(500), default="")
    topics = Column(String(2000), default="")
    materials = Column(String(1000), default="")
    sentiment = Column(String(50), default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class FollowUp(Base):
    """A follow-up task the rep wants to remember (created by the schedule tool)."""
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), default="")
    followup_date = Column(String(50), default="")
    note = Column(String(1000), default="")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create the tables if they don't exist yet. Called once when the app starts."""
    Base.metadata.create_all(bind=engine)
