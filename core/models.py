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
    user = relationship("users", back_populates="blog")
    images = relationship("images", back_populates="blog")
    likes = relationship("likes", back_populates="blog")
    comments = relationship("comments", back_populates="blog")

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column("name",String)
    email = Column("email",String)
    password = Column("password",String)
    Blog = relationship("blog",back_populates="users")
    Like = relationship("likes", back_populates="users")
    comments = relationship("comments", back_populates="users")

class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column("blog_id", Integer, ForeignKey("blog.id"))
    blog = relationship("blog", back_populates="images")

class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("liked_by", Integer, ForeignKey("users.id"))
    blog_id = Column("blog_id", Integer, ForeignKey("blog.id"))
    blog = relationship("blog", back_populates="likes")
    user = relationship("users", back_populates="likes")

class Comments(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column("comment", String)
    reply = Column("reply", String)
    user_id = Column("commented_by", Integer, ForeignKey("users.id"))
    blog_id = Column("blog_id", Integer, ForeignKey("blog.id"))
    blog = relationship("blog", back_populates="comments")
    user = relationship("users", back_populates="comments")


