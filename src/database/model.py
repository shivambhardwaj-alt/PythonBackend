import uuid
from datetime import datetime, date
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column
from sqlmodel import SQLModel, Field

class Book(SQLModel, table=True):          
    __tablename__ = "books" # type: ignore

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    createdAt: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updatedAt: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))