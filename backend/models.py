from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
Base=declarative_base()
class roilog(Base):
    __tablename__ = "roilog"
    id=Column(Integer,primary_key=True,index=True)
    time=Column(DateTime,default=datetime)
    #roi coordinates
    x1=Column(Integer,nullable=False)
    y1=Column(Integer,nullable=False)
    x2=Column(Integer,nullable=False)
    y2=Column(Integer,nullable=False)