from fastapi import APIRouter , Depends , status ,HTTPException , Request 
from fastapi.responses import JSONResponse
from src.auth.dependencies import access_token_bearer
from src.me.service import UserProfileService
from sqlalchemy.ext.asyncio import AsyncSession 
from src.database.database import get_db
from typing import Dict
from src.me.schema import UserUpdateModel

user_service = UserProfileService()


me_router = APIRouter()

"""
routes for handling a user here 

"""


@me_router.get("/me")
async def profile_getter(token_details  =  Depends(access_token_bearer) , db: AsyncSession = Depends(get_db)):
    try : 
        print("Request came into the profile_getter method handler")
        user = await user_service.get_profile(token_details["email"] , db)
        return user 
    except: 
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR , detail= "Internal Sever Error")
@me_router.patch("/update")
async def profile_update(data : UserUpdateModel, token_details = Depends(access_token_bearer) ,  db : AsyncSession = Depends(get_db)):
    try: 
        print(data.model_dump(exclude_none = True))
        res = await user_service.update_profile(
    data.model_dump(exclude_none=True),
    token_details["email"],
    db,
)
        return JSONResponse(status_code = 200 , content = res)
    except : 
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR , detail = "Internal Server Error")