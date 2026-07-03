import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base
from app.db.models import User, LegalCase, Document, AgentLog, Citation
from app.core.logging import get_logger

logger = get_logger(__name__)


async def init_db():
    """Initialize database tables"""
    logger.info("Creating database tables...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Drop all tables (only for development)
        if settings.DEBUG:
            await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    logger.info("Database tables created successfully")


if __name__ == "__main__":
    asyncio.run(init_db())
