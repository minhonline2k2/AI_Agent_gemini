"""
main.py - Entry point cua FastAPI backend
Day la file chay dau tien khi backend khoi dong
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db

# Import tat ca API routers
from api.v1 import (
    auth, ingest, incidents, rca, agent,
    system_info, knowledge, chat, dashboard, governance, health
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Chay khi app khoi dong va tat"""
    # Khoi dong: tao bang trong DB neu chua co
    await init_db()
    print(f"[STARTUP] {settings.APP_NAME} v{settings.APP_VERSION} started")
    yield
    # Tat: cleanup
    print("[SHUTDOWN] App shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Cho phep frontend goi API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production nen gioi han domain cu the
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dang ky tat ca routers
app.include_router(health.router,      prefix="/api/v1", tags=["Health"])
app.include_router(auth.router,        prefix="/api/v1/auth", tags=["Auth"])
app.include_router(ingest.router,      prefix="/api/v1/ingest", tags=["Ingestion"])
app.include_router(incidents.router,   prefix="/api/v1/incidents", tags=["Incidents"])
app.include_router(rca.router,         prefix="/api/v1/rca", tags=["RCA"])
app.include_router(agent.router,       prefix="/api/v1/agent", tags=["Agent"])
app.include_router(system_info.router, prefix="/api/v1/system-info", tags=["SystemInfo"])
app.include_router(knowledge.router,   prefix="/api/v1/knowledge", tags=["Knowledge"])
app.include_router(chat.router,        prefix="/api/v1/chat", tags=["Chat"])
app.include_router(dashboard.router,   prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(governance.router,  prefix="/api/v1/governance", tags=["Governance"])
