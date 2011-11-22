import sqlite3
from sqlalchemy import Column, Integer, MetaData, String
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
    body = Column(Text)
    create_dt = Column(DateTime)
    next_check = Column(DateTime)
    next_interval = Column(Integer)

def connect():
    c = sqlite3.connect('queue.db')
    c.text_factory = str
    return c

def initialize_db(engine=None):
    dbsession.configure(bind=engine)
    base.metadata.bind = engine
    base.metadata.create_all(engine)
    metadata = MetaData(bind=engine, reflect=True)
