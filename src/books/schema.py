import uuid
from datetime import datetime, date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field

""" These are pydantic models to get and give data to the user and the database"""


class LanguageEnum(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"

class BookCreateModel(BaseModel):                      
    model_config = ConfigDict(use_enum_values=True)    

    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=200)
    publisher: str = Field(min_length=1, max_length=200)
    published_date: date
    page_count: int = Field(gt=0, le=2000)
    language: LanguageEnum

    @field_validator("title", "author", "publisher")
    @classmethod
    def strip_and_check_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Field cannot be blank whitespace")
        return v

class BookResponse(BaseModel):                        
    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    createdAt: datetime
    updatedAt: datetime

    @computed_field
    @property
    def years_since_publication(self) -> int:
        return date.today().year - self.published_date.year
class BookUpdateModel(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    title : str  
    author : str 
    publisher : str 
    published_date : date 
    page_count : int 
    language : str 
    