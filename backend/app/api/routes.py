from fastapi import APIRouter
from .endpoints import cases, analysis, health, knowledge_base, sessions

api_router = APIRouter()
api_router.include_router(health.router,         prefix="/health",         tags=["health"])
api_router.include_router(sessions.router,       prefix="/sessions",       tags=["sessions"])
api_router.include_router(cases.router,          prefix="/cases",          tags=["cases"])
api_router.include_router(analysis.router,       prefix="/analysis",       tags=["analysis"])
api_router.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["knowledge-base"])
