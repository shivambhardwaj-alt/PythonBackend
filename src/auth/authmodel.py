from sqlmodel import SQLModel ,Field ,Column
import  sqlalchemy.dialects.postgresql  as pg
import uuid
from datetime import datetime

class UserModel(SQLModel , table = True):
    __tablename__ : str = 'users'
    uid  :uuid.UUID = Field(sa_column=Column(pg.UUID , nullable = False , primary_key= True, default = uuid.uuid4))
    username : str
    email : str 
    first_name : str 
    last_name : str 
    role : str  = Field(sa_column = Column(pg.VARCHAR , server_default  = "user"))
    password_hash : str = Field(exclude= True) 
    is_verified : bool = Field(default = False)
    createdAt : datetime  = Field(sa_column = Column(pg.TIMESTAMP ,default= datetime.now))
    updatedAt : datetime = Field(sa_column= Column(pg.TIMESTAMP , default  = datetime.now))

    def __repr__(self):
        return f'User <{self.username}>'
    
    