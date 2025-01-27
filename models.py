from sqlalchemy import Column, Integer, String, Float,DATETIME
from database import  Base

class Blog(Base):
    __tablename__ = "blog"
    id = Column(Integer, primary_key=True, index=True)
    title = Column("title",String)
    content = Column("content",String)
    created_at = Column("created_at", DATETIME)
