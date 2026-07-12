from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine,async_sessionmaker,create_async_engine,AsyncSession
from sqlalchemy import create_engine , text 
from config import Config

from sqlalchemy.orm import DeclarativeBase
engine = create_async_engine(
    Config.DATABASE_URL or "",
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


class Base(DeclarativeBase):
    pass



async def get_db():
    print("Creating database session...")
    async with AsyncSessionLocal() as session:
        print("Database session created:", session)
        yield session
    print("Database session closed...")