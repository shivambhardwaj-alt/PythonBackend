from pydantic import BaseModel

class UserUpdateModel(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    username: str | None = None