from pydantic import BaseModel , Field, field_validator , ConfigDict
import re
from uuid import UUID
class UserUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    username: str | None = None
    
    
class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    uid : UUID
    first_name : str 
    last_name : str 
    email : str  
         
    
    


class ChangePassword(BaseModel):
    old_password : str = Field(min_length = 8 , max_length = 128) 
    new_password : str  = Field(min_length = 8 ,max_length = 128)
    
    @field_validator('old_password')
    @classmethod
    def validate_old_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError('Password should contain an Uppercase Letter')
        if not re.search(r'[a-z]' , value):
            raise ValueError("Password should contain an Lowercase Letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")

        if not re.search(r"[^a-zA-Z0-9]", value):
            raise ValueError("Password must contain a special character")
        return value 
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError('Password should contain an Uppercase Letter')
        if not re.search(r'[a-z]' , value):
            raise ValueError("Password should contain an Lowercase Letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain a digit")

        if not re.search(r"[^a-zA-Z0-9]", value):
            raise ValueError("Password must contain a special character")
        return value 

    