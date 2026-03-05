"""
============================================
メタ広告審査チェッカー - FastAPI アプリケーション
============================================

バックエンドAPIのエントリーポイント
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .utils import setup_logging, get_logger, http_exception_handler, general_exception_handler

# 環境変数の読み込み（.env.local優先、なければ.env）
import pathlib
env_path = pathlib.Path(__file__).parent.parent / '.env.local'
if not env_path.exists():
    env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = get_logger(__name__)


# --------------------------------------------
# Lifespan Event Handler
# --------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    # Startup
    logger.info("🚀 Starting Meta Ad Review Checker API...")
    logger.info(f"Port: {os.getenv('PORT', '8432')}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # 環境変数の検証
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        logger.warning("⚠️ ANTHROPIC_API_KEY not set. AI features will be unavailable.")
    else:
        logger.info("✅ ANTHROPIC_API_KEY configured")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logger.info("✅ OPENAI_API_KEY configured (optional)")

    yield

    # Shutdown
    logger.info("👋 Shutting down Meta Ad Review Checker API...")


# --------------------------------------------
# FastAPI Application Initialization
# --------------------------------------------

# ロギング設定
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(level=log_level)

# FastAPIアプリケーション作成
app = FastAPI(
    title="メタ広告審査チェッカー API",
    description="Meta広告の審査基準に基づいた事前チェックツール",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# --------------------------------------------
# CORS設定
# --------------------------------------------

# 許可するオリジン（環境変数から取得、デフォルトはローカル開発環境）
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3247,http://127.0.0.1:3247,https://meta-ad-checker.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {allowed_origins}")


# --------------------------------------------
# Exception Handlers
# --------------------------------------------

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# --------------------------------------------
# Routes
# --------------------------------------------

from .routes import health, check

app.include_router(health.router)
app.include_router(check.router)


# --------------------------------------------
# Root Endpoint (Temporary)
# --------------------------------------------

@app.get("/")
async def root():
    """ルートエンドポイント（一時的）"""
    return {
        "message": "Meta Ad Review Checker API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health"
    }


# --------------------------------------------
# Main Entry Point (for local development)
# --------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8432))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level=log_level.lower()
    )
