import uuid
from sqlmodel import SQLModel , Field 
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from sqlalchemy import Column, UniqueConstraint, CheckConstraint

class BookRatings(SQLModel , table = True):
    __tablename__ :str = "book_ratings"
    __table_args__ = (
        UniqueConstraint(
            "user_uid",
            "book_uid",
            name="unique_user_book_rating"
        ),
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="valid_book_rating"
        )
    )
    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            default=uuid.uuid4
        )
    )
    user_uid : uuid.UUID  = Field(foreign_key = "users.uid")
    book_uid : uuid.UUID = Field(foreign_key =  "books.uid")
    rating : float 
    createdAt :datetime  =  Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            default=datetime.now,
            onupdate=datetime.now
        )
    )    
    