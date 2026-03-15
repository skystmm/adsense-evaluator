"""
用户认证服务
提供用户注册、登录、Token 验证等功能
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.database import User
import os

# 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    认证用户
    :param db: 数据库会话
    :param email: 用户邮箱
    :param password: 密码
    :return: 用户对象或 None
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问 Token
    :param data: Token 数据（通常包含 user_id 和 email）
    :param expires_delta: 过期时间增量
    :return: JWT Token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码访问 Token
    :param token: JWT Token
    :return: Token 数据或 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def register_user(db: Session, email: str, password: str, full_name: Optional[str] = None) -> Optional[User]:
    """
    注册新用户
    :param db: 数据库会话
    :param email: 用户邮箱
    :param password: 密码
    :param full_name: 用户全名（可选）
    :return: 创建的用户对象或 None（如果邮箱已存在）
    """
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return None
    
    # 创建新用户
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    根据 ID 获取用户
    :param db: 数据库会话
    :param user_id: 用户 ID
    :return: 用户对象或 None
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    根据邮箱获取用户
    :param db: 数据库会话
    :param email: 用户邮箱
    :return: 用户对象或 None
    """
    return db.query(User).filter(User.email == email).first()
