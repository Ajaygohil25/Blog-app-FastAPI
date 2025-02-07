from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Relationships
    blogs = relationship("Blog", back_populates="user")
    likes = relationship("Likes", back_populates="user")
    comments = relationship(
                "Comments",
                foreign_keys="[Comments.commented_by]",
                back_populates="commented_by_user",
                cascade="all, delete, delete-orphan")

class Blog(Base):
    __tablename__ = "blog"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships
    user = relationship("Users", back_populates="blogs", passive_deletes=True)
    images = relationship("Images", back_populates="blog",cascade="all, delete, delete-orphan")
    likes = relationship("Likes", back_populates="blog", cascade="all, delete, delete-orphan")
    comments = relationship("Comments", back_populates="blog", cascade="all, delete, delete-orphan")

class Images(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String, nullable=False)
    blog_id = Column(Integer, ForeignKey("blog.id", ondelete="CASCADE"))

    # Relationships
    blog = relationship("Blog", back_populates="images")

class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    blog_id = Column(Integer, ForeignKey("blog.id", ondelete="CASCADE"))

    # Relationships
    blog = relationship("Blog", back_populates= "likes")
    user = relationship("Users", back_populates="likes")

class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String, nullable=False)
    reply = Column(String)
    commented_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reply_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    blog_id = Column(Integer, ForeignKey("blog.id", ondelete="CASCADE"))

    # Relationships
    blog = relationship("Blog", back_populates="comments")
    commented_by_user = relationship("Users",foreign_keys=[commented_by], back_populates="comments")
    reply_by_user = relationship("Users",foreign_keys=[reply_by])
