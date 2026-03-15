"""
数据库模型和连接
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./adsense_evaluator.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EvaluationReport(Base):
    """评估报告模型"""
    __tablename__ = "evaluation_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)  # 关联用户，可为空（允许未登录用户使用）
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
