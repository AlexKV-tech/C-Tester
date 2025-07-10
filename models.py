from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table
import datetime as dt

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer,primary_key=True)
    ctest_text = Column(String, index=True)
    answers = Column(String, index=True)
    original_text = Column(String, index=True)
    # submissions = Column(Table)
    created_at = Column(DateTime, default=dt.datetime.utcnow())
    # expires_at = Column(DateTime, server_default=dt.datetime.utcnow() + dt.timedelta(days=7))