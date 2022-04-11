import os

from sqlalchemy import Integer, String, Column, Date, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

DB_URL = os.getenv("DB_URL", "mysql+pymysql://root:pass@localhost:3306/pp_web_project")

engine = create_engine(DB_URL, convert_unicode=True, connect_args=dict(use_unicode=True))

SessionFactory = sessionmaker(bind=engine)

Session = scoped_session(SessionFactory)

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'user'
    user_id=Column(Integer, primary_key=True)
    username=Column(String(255))
    first_name=Column(String(255))
    last_name=Column(String(255))
    email=Column(String(255))
    password=Column(String(255))
    role_id=Column(Integer, ForeignKey('role.role_id'))
    role = relationship("Role")


class Role(Base):
    __tablename__ = "role"
    role_id=Column(Integer, primary_key=True)
    role=Column(String(255))


class Article(Base):
    __tablename__ = 'article'
    article_id = Column(Integer, primary_key=True)
    title = Column(String(255))
    text = Column(String(8000))
    date = Column(Date)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    moderator_id = Column(Integer, ForeignKey('user.user_id'))
    status_id=Column(Integer, ForeignKey('status.status_id'))
    user = relationship("User", foreign_keys=[user_id])
    moderator = relationship("User", foreign_keys=[moderator_id])
    status = relationship("Status")


class Status(Base):
    __tablename__ = "status"
    status_id = Column(Integer, primary_key=True)
    status = Column(String(255))
