from src.auth.authmodel import UserModel 
# from sqlmodel.ext.asyncio.session import AsyncSession 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.database.database import get_db
from src.auth.schema import UserCreateModel
from src.auth.utils import generate_password_hash
class UserService:
    
    async def get_user(self, email : str , db : AsyncSession) :
        statement = select(UserModel).where(email == UserModel.email)
        result  = await db.execute(statement)
        user = result.scalars().first()
        return user 
    async def user_exists(self, email : str, db : AsyncSession):
        user = await self.get_user(email , db)
        return True if user is not None  else False
    async def create_user(self, data: UserCreateModel, db: AsyncSession):
        user_data_dict = data.model_dump()

       
        plain_password = user_data_dict.pop("password")
        user_data_dict["password_hash"] = generate_password_hash(plain_password)

        new_user = UserModel(**user_data_dict)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user