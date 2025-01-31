import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# for print sql Query
logger = logging.getLogger('sqlalchemy')
logger.setLevel(logging.INFO)
DB_URL = "postgresql://postgres:admin@localhost:5432/test_db"
connect_args = {"check_same_thread": False}
engine = create_engine(DB_URL, connect_args = connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()
logger.addHandler(logging.StreamHandler())


def get_db():
    """ Get the database connection from session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()