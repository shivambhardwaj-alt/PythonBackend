from fastapi import HTTPException , status 
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlmodel import select , update
from src.database.database import get_db
from src.auth.authmodel import UserModel
from typing import Any
from uuid import UUID
from src.me.schema import UserProfileResponse , UserUpdateModel


class UserProfileService:
    
    async def get_profile(self, email: str, db: AsyncSession):

        statement = select(UserModel).where(UserModel.email == email)

        result = await db.execute(statement)
        user = result.scalars().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        data = UserProfileResponse.model_validate(user)

        return data

    async def update_profile(
    self,
    email: str,
    data: UserUpdateModel,
    db: AsyncSession
):
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        statement = (
            update(UserModel)
            .where(UserModel.email == email) # type: ignore
            .values(**update_data)
        )

        result = await db.execute(statement)

        if result.rowcount == 0: # type: ignore
            raise HTTPException(status_code=404, detail="User not found")

        await db.commit()

        return {"message": "Profile updated successfully"}
        
            
    async def change_password(self,uid : UUID ,  new_password : str , db : AsyncSession):
        statement = update(UserModel).where(UserModel.uid == uid).values(UserModel.password_hash  = new_password)
        result  = await db.execute(statement)
        if result.rowcount == 0: 
            raise HTTPException(status_code = 404 , detail  = "User not found")
        await db.commit()
        
        
    
        
        
        
            
            
        