"""
database.py
-----------
This file sets up our database connection and defines the tables.

We use SQLAlchemy, which is a popular Python library that lets us talk to a
database (Postgres, MySQL, or SQLite) using normal Python classes instead of
writing raw SQL by hand.

By default this runs on SQLite (a tiny file-based database that needs ZERO
setup) so you can test immediately. To meet the assignment requirement of using
Postgres, just set DATABASE_URL in your .env file (see .env.example) and it will
switch automatically.
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()  # read the .env file

# If DATABASE_URL is set (e.g. a Postgres URL), use it. Otherwise fall back to a
# local SQLite file so the project runs out of the box.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hcp_crm.db")

# SQLite needs one extra argument; other databases do not.
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
