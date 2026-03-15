from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class HistoryItem(BaseModel):
    url: str
    score: int
    date: str

# 临时存储
history_db = []

@router.get("/", response_model=List[HistoryItem])
async def get_history():
    """
    获取评估历史
    """
    return history_db

@router.post("/clear")
async def clear_history():
    """
    清空历史记录
    """
    history_db.clear()
    return {"message": "历史记录已清空"}
