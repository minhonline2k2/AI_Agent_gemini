"""
database.py - Ket noi va quan ly database PostgreSQL
Su dung SQLAlchemy 2.x voi async support
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Tao engine ket noi database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # In cau SQL ra log khi DEBUG=true
    pool_size=20,
    max_overflow=10,
)

# Factory tao session (moi request dung 1 session)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Base class cho tat ca models
class Base(DeclarativeBase):
    pass


async def get_db():
    """
    Dependency injection cho FastAPI
    Moi API endpoint can DB se goi ham nay
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Tao tat ca bang trong DB (dung khi khoi dong lan dau)"""
    # Import tat ca models de SQLAlchemy biet
    import models.incident
    import models.rca
    import models.agent
    import models.system_info
    import models.knowledge
    import models.audit
    import models.user

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] All tables created/verified")
