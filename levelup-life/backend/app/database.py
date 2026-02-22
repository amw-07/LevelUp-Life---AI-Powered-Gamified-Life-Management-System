import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


def _get_database_url() -> str:
    return os.environ.get("DATABASE_URL", settings.DATABASE_URL)


def _create_engine():
    url = _get_database_url()
    kwargs = {
        "echo": False,
        "pool_pre_ping": True,
    }
    if not url.startswith("sqlite"):
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20
    return create_async_engine(url, **kwargs)


engine = _create_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_async_session():
    return AsyncSessionLocal()
