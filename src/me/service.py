from sqlalchemy.ext.asyncio import AsyncSession 
from sqlmodel import select , update
from src.database.database import get_db
from src.auth.authmodel import UserModel




class UserProfileService:
    
    async def get_profile(self, email : str , db : AsyncSession):
        statement = select(UserModel.first_name, UserModel.last_name, UserModel.email, UserModel.username).where(UserModel.email == email)
        result  = await db.execute(statement)
        user = result.scalars().first()
        return user

    async def update_profile(self,data : dict , email : str , db : AsyncSession):
        statement = update(UserModel).where(UserModel.email == email).values(**data)
        await db.execute(statement)
        await db.commit()
        
        
        
    
        
        
    