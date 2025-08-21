import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


def get_engine():
    url = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def get_session(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine)()
