import pytest_asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from httpx import AsyncClient
import httpx

from thaitravel.main import app
from thaitravel.models import get_session

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# ✅ Engine และ Session สำหรับทดสอบ
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncTestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# ✅ สร้าง DB ก่อนใช้งาน
@pytest_asyncio.fixture(scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# ✅ Fixture session ที่จะ override `get_session`
@pytest_asyncio.fixture
async def session(prepare_database):  # ← 👈 เพิ่ม fixture นี้
    async with AsyncTestingSessionLocal() as session:
        yield session


# ✅ Fixture client ที่ใช้ session override
@pytest_asyncio.fixture
async def client(session):  # ← ใช้ session ที่ประกาศไว้ด้านบน
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000"
    ) as client:
        yield client

    app.dependency_overrides.clear()
