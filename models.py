import sqlite3
from sqlalchemy import Boolean, Column, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import BigInteger, DateTime, Integer, Text
from sqlalchemy.schema import Sequence

base = declarative_base()
dbsession = scoped_session(sessionmaker())

class Request(base):
    __tablename__ = 'requests'
    __table_args__ = {'sqlite_autoincrement': True}

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    blind_id_header = Column(Text)
    ip_addr = Column(String(length=32))
    body = Column(Text)
    create_dt = Column(DateTime)
    next_check = Column(DateTime)
    next_interval = Column(Integer)

class User(base):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement':True}

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(length=30), default='', unique=True)
    password = Column(String(length=100), default='')
    active_ind = Column(Boolean, default=True)
    is_authenticated = False

    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return self.active_ind

    def is_anonymous(self):
        return self.username != ""

    def get_id(self):
        return unicode(self.user_id)

def connect():
    c = sqlite3.connect('queue.db')
    c.text_factory = str
    return c

def initialize_db(engine=None):
    dbsession.configure(bind=engine)
    base.metadata.bind = engine
    base.metadata.create_all(engine)
    metadata = MetaData(bind=engine, reflect=True)
