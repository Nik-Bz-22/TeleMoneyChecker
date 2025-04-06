from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(engine, class_=AsyncSession, autocommit=False, autoflush=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        yield db
