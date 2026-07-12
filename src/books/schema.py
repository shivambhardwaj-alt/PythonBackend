from pydantic import BaseModel , ConfigDict
from datetime import date , datetime
import uuid
class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uid : uuid.UUID 
    title : str 
    author : str 
    publisher : str 
    published_date : date
    page_count : int
    language : str 
    createdAt : datetime 
    updatedAt : datetime
    
    
    
class BookCreateModel(BaseModel):
    title : str 
    author : str 
    publisher : str 
    published_date  : date
    page_count : int 
    language : str     
    

class BookUpdateModel(BaseModel):
    title : str 
    author : str 
    publisher : str 
    page_count : int 
    language : str 
 
    