"""
用户认证 API
提供注册、登录、用户信息获取等接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta

from models.database import SessionLocal, User, EvaluationReport
from services import auth_service

router = APIRouter()

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic 模型
class UserRegister(BaseModel):
    """用户注册请求"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str


# 依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    :param token: JWT Token
    :param db: 数据库会话
    :return: 用户对象
    :raises: HTTPException 如果 Token 无效
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = auth_service.decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    return user


# API 端点
@router.post("/register", response_model=UserResponse, tags=["认证"])
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    - **email**: 用户邮箱（必须唯一）
    - **password**: 密码（至少 6 位）
    - **full_name**: 用户全名（可选）
    """
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为 6 位"
        )
    
    user = auth_service.register_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at.isoformat()
    )


@router.post("/login", response_model=Token, tags=["认证"])
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录
    - **username**: 用户邮箱
    - **password**: 密码
    返回 JWT Token 用于后续请求认证
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账户已被禁用"
        )
    
    access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )


@router.get("/me", response_model=UserResponse, tags=["认证"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息
    需要在请求头中携带有效的 Token: Authorization: Bearer <token>
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.post("/change-password", tags=["认证"])
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    - **old_password**: 原密码
    - **new_password**: 新密码（至少 6 位）
    """
    # 验证原密码
    if not auth_service.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少为 6 位"
        )
    
    # 更新密码
    current_user.hashed_password = auth_service.get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "密码已修改成功"}


@router.post("/logout", tags=["认证"])
async def logout(current_user: User = Depends(get_current_user)):
    """
    用户登出
    客户端需要删除本地存储的 Token
    """
    # JWT 是无状态的，登出主要由客户端处理（删除 Token）
    # 这里可以添加黑名单逻辑（可选）
    return {"message": "已成功登出"}
