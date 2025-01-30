from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from .database import  Base

class Blog(Base):
    __tablename__ = "blog"
    id = Column(Integer, primary_key=True, index=True)
    title = Column("title",String)
    content = Column("content",String)
    created_at = Column("created_at", DATETIME)
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    user = relationship("Users", back_populates="Blog")

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column("name",String)
    email = Column("email",String)
    password = Column("password",String)
    Blog = relationship("Blog",back_populates="user")