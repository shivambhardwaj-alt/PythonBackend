from pydantic import BaseModel, Field, model_validator
from typing import Optional, List

class UserCreateModel(BaseModel):
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)

    first_name: Optional[str] = Field(max_length=40, default=None)
    last_name: str = Field(max_length=50, default="")

    @model_validator(mode="after")
    def set_default_first_name(self):
        if not self.first_name:
            self.first_name = self.username
        return self
class UserLogin(BaseModel):
    email : str  = Field(max_length = 40)
    password : str  = Field(max_length = 72)
class EmailModel(BaseModel):
    addresses : List[str]
    
    