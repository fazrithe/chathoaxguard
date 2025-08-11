from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database.session import Base

class LogASN(Base):
    __tablename__ = "log_asn"

    id = Column(String, primary_key=True, index=True)
    sender = Column(String, index=True)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
