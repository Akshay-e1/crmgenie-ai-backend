from sqlalchemy import Column, Integer, String
from db import Base

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String)
    topics = Column(String)
    sentiment = Column(String)
    follow_up = Column(String)
    date = Column(String)
    time = Column(String)
    outcomes = Column(String)
