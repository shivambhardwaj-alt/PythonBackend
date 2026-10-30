from fastapi import APIRouter , Depends , status ,HTTPException , Request 
from fastapi.responses import JSONResponse
from src.auth.dependencies import access_token_bearer
from src.me.service import UserProfileService
from sqlalchemy.ext.asyncio import AsyncSession 
from src.database.database import get_db
from typing import Dict
from src.me.schema import UserUpdateModel , ChangePassword
from src.auth.utils import generate_password_hash , verify_password

user_service = UserProfileService()


me_router = APIRouter()

"""
routes for handling a user here 

"""


@me_router.get("/me")
async def profile_getter(token_details  =  Depends(access_token_bearer) , db: AsyncSession = Depends(get_db)):
    try : 
        user = await user_service.get_profile(token_details["email"] , db)
        return user 
    except HTTPException : 
        raise 
    except Exception: 
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
    


@me_router.put("/change-password")
async def change_password( data : ChangePassword,  token_details =  Depends(access_token_bearer ) , db: AsyncSession  = Depends(get_db)):
    try : 
        uid = token_details['uid']
        user = await user_service.get_profile(token_details['email'] , db)
        if not user : 
            raise HTTPException(status_code = 404 , detail = "User not found")
        # now check his old password 
        
        old_password = data.old_password 
        new_password = data.old_password 
        
        verification = verify_password(old_password, user['password_hash'])
        if not verification: 
            raise HTTPException(status_code = 400 , detail = "Incorrect Password")
        
        
        
        
        
    except HTTPException:
        raise 
    except Exception : 
        raise HTTPException(status_code = 500 ,  detail= "Internal Server Error") 


@me_router.delete("/delete")
async def delete_user(token_details  = Depends(access_token_bearer)):
    try : 
    
        pass
    except HTTPException : 
        raise 
    except Exception : 
        raise HTTPException(status_code = 500 , detail = "Internal Server Error")


@me_router.get('/ratings')
# all the books i rated 
async def get_all_books(token_detials = Depends(access_token_bearer)):
    try : 
        pass 
    except HTTPException : 
        raise 
    except Exception : 
        raise HTTPException (status_code = 500 , detail = "Internal Server Error")

        
        