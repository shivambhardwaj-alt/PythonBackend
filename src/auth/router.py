from fastapi import APIRouter , Depends , status ,HTTPException

from src.auth.schema import UserCreateModel , UserLogin
from src.database.database import get_db
from src.auth.service import UserService  
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.utils import generate_access_token  ,verify_password 
from src.auth.dependencies import RefreshTokenBearer  , AccessTokenBearer
from datetime import timedelta , datetime
from fastapi.responses import JSONResponse
from src.database.redis import add_jti_to_blocklist 
auth_router  = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRY = 1

@auth_router.post("/signup" )
async def create_user_account(data : UserCreateModel  , db : AsyncSession =  Depends(get_db)):
    email  = data.email 
    user_exists = await user_service.user_exists(email , db)
    if user_exists : 
        raise HTTPException(status.HTTP_403_FORBIDDEN , detail = "User with email already exists")
    new_user =  await user_service.create_user(data , db)
    return new_user

@auth_router.get("/get-user")
async def get_user(email : str , db : AsyncSession =  Depends(get_db)):
    result = await user_service.get_user(email , db)
    if not result : 
        raise HTTPException(status.HTTP_404_NOT_FOUND , detail  = "User not Found")
    return result
    
    
   
@auth_router.post('/login')
async def login_user(data : UserLogin , db : AsyncSession = Depends(get_db)):
    user  =  await  user_service.get_user(data.email ,db)
    
    if  user is not None :
        valid_password = verify_password(data.password, user.password_hash)  
        if valid_password : 
            access_token = generate_access_token(
                user_data = {"email"  : data.email , "user_uid" : str(user.uid) ,"role" : user.role}
            )
            refresh_token  = generate_access_token(
                user_data = {"email" : data.email , "user_uid" : str(user.uid) ,"role" : user.role},
                refresh  = True, 
                expiry = timedelta(days = REFRESH_TOKEN_EXPIRY)
            )
            return JSONResponse(
                {
                    "content" : "LoginSuccessful" ,
                    "access_token" : access_token,
                    "refresh_token" : refresh_token,
                    "user" : {
                        "user_uid" : str(user.uid),
                        "user.email" : user.email,
                        "user.role" : user.role
                    }
                }
            )
            
            
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN , detail  = "Password not correct")
    else:
        raise HTTPException(status.HTTP_403_FORBIDDEN , detail = "User not Found")
    
@auth_router.post("/refresh-token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer())
):

    user_data = token_details["user"]

    new_access_token = generate_access_token(
        user_data=user_data
    )

    return JSONResponse(
        content={
            "access_token": new_access_token
        }
    )
    
    
@auth_router.post("/logout")
async def logout(token_details   : dict = Depends(AccessTokenBearer)) :
    print(token_details)
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)
    return JSONResponse(content="Logout successfully" , status_code= status.HTTP_200_OK)




@auth_router.patch("/change-password")
async def changePassword(db : AsyncSession = Depends(get_db) , token_details  : dict  =  Depends(AccessTokenBearer)):
    print(token_details)
    return JSONResponse(content = "Changed Successfully" , status_code= status.HTTP_200_OK)
    

async def forgotPassword(db:AsyncSession =  Depends(get_db)):
    pass

async def verifyEmail( email : str , db : AsyncSession  =  Depends(get_db)):
    pass
