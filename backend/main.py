from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import evaluate, reports, history, auth, export
from models.database import init_db
import uvicorn

app = FastAPI(
    title="AdSense Evaluator API",
    description="Google AdSense 网站评估 API",
    version="2.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://adsense-evaluator.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(evaluate.router, prefix="/api/evaluate", tags=["评估"])
app.include_router(reports.router, prefix="/api/reports", tags=["报告"])
app.include_router(history.router, prefix="/api/history", tags=["历史记录"])
app.include_router(export.router, prefix="/api/export", tags=["导出"])

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {
        "message": "AdSense Evaluator API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
