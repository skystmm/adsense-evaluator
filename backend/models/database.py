"""
数据库模型和连接
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./adsense_evaluator.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EvaluationReport(Base):
    """评估报告模型"""
    __tablename__ = "evaluation_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    url = Column(String, nullable=False)
    overall_score = Column(Integer)
    pass_probability = Column(Float)
    metrics = Column(JSON)
    issues = Column(JSON)
    ai_suggestions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserHistory(Base):
    """用户历史记录模型"""
    __tablename__ = "user_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    url = Column(String, nullable=False)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)
