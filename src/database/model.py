import uuid
from datetime import datetime , date
from enum import Enum 
from typing import List

from pydantic import BaseModel , ConfigDict , Field , field_validator , model_validator , computed_field 


class LanguageEnum(str, Enum):
    ENGLISH  = "en"
    HINDI = "hi"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    
class Book(BaseModel):
    model_config = ConfigDict(from_attributes = True)
    uuid : uuid.UUID
    title : str
    author : str 
    isbn : str
    published:str
    page_count : int 
    language: LanguageEnum
    createdAt:datetime
    upatedAt : datetime
    @computed_field
    @property
    def years_since_publication(self) -> int:
        return date.today().year()  - self.published.year()
    


class BookCreateModel(BaseModel):
    title : str  = Field(min_length = 1, max_length = 200)
    author: str = Field(min_length = 1 , max_length = 200)
    publisher : str = Field(min_length = 1, max_length = 200)
    published_date : date 
    isbn: str = Field(pattern=r"^(97(8|9))?\d{9}(\d|X)$")
    page_count : int  = Field(gt = 0 , le = 2000)
    language  : LanguageEnum
    
    @field_validator("title" , "author" , "publisher")
    @classmethod
    def strip_and_check_not_blank(cls , v : str) -> str:
        v = v.strip()
        if not v :
            raise ValueError("Field Cannot be blank whitespace")
        return v

        