import re
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional, List

SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~"


def validate_password_strength(password: str) -> str:
    errors = []
    if not re.search(r"[A-Z]", password):
        errors.append("one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("one digit")
    if not re.search(f"[{re.escape(SPECIAL_CHARS)}]", password):
        errors.append("one special character")
    if re.search(r"\s", password):
        raise ValueError("Password must not contain spaces")
    if errors:
        raise ValueError("Password must contain at least " + ", ".join(errors))
    return password


class UserCreateModel(BaseModel):
    username: str = Field(min_length=3, max_length=8)
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=8, max_length=72)

    first_name: Optional[str] = Field(max_length=40, default=None)
    last_name: str = Field(max_length=50, default="")

    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)
    @model_validator(mode="after")
    def check_and_set_defaults(self):
        if self.username.lower() in self.password.lower():
            raise ValueError("Password must not contain the username")
        if not self.first_name:
            self.first_name = self.username
        return self
class AdminCreateModel(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: EmailStr = Field(max_length=50)
    password: str = Field(min_length=8, max_length=72)  
    first_name : str  = Field(min_length = 4 , max_length = 72)
    last_name : str = Field(min_length = 4 , max_length = 72) 
    role : str
    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        return validate_password_strength(value)

    
    @field_validator("role")
    def check_role(cls, value : str) -> str | None:
        if value.lower() == "admin":
            return "admin"

class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(max_length=72)


class EmailModel(BaseModel):
    addresses: List[EmailStr]