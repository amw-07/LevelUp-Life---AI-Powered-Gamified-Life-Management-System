import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.database import Base, get_db
from app.redis_client import get_redis
from unittest.mock import AsyncMock

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(setup_db):
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture
async def db_session(setup_db):
    async with TestSessionLocal() as session:
        yield session


class FakeRedis:
    def __init__(self):
        self._store: dict = {}

    async def get(self, key: str):
        return self._store.get(key)

    async def setex(self, key: str, ttl: int, value):
        self._store[key] = value
        return True

    async def delete(self, *keys):
        for key in keys:
            self._store.pop(key, None)
        return len(keys)

    async def incr(self, key: str):
        current = int(self._store.get(key, 0))
        self._store[key] = str(current + 1)
        return current + 1

    async def expire(self, key: str, ttl: int):
        return True


@pytest_asyncio.fixture
async def client(setup_db):
    async def override_get_db():
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    fake_redis_instance = FakeRedis()

    def override_get_redis():
        return fake_redis_instance

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
