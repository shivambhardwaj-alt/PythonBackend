from sqlmodel import SQLModel, Field,Column
from datetime import datetime , date
import uuid
import sqlalchemy.dialects.postgresql as pg


class Book(SQLModel, table=True):

    __tablename__ = "books"

    uid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language : str
    createdAt : datetime = Field(sa_column=Column(pg.TIMESTAMP , default = datetime.now))
    updatedAt : datetime = Field(sa_column = Column(pg.TIMESTAMP , default = datetime.now))
    