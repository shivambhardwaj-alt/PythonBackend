from fastapi import APIRouter , Depends , status ,HTTPException , Request , BackgroundTasks
from src.utils.limiter import limiter
from src.auth.schema import UserCreateModel , UserLogin , EmailModel , AdminCreateModel , SendOtpRequest , VerifyOTP
from src.database.database import get_db
from src.auth.service import UserService  
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.utils import generate_access_token  ,verify_password ,generate_refresh_token
from src.auth.dependencies import RefreshTokenBearer  , AccessTokenBearer
from datetime import timedelta , datetime
from fastapi.responses import JSONResponse
from src.database.redis import add_jti_to_blocklist 
from src.auth.otp import generate_otp, store_top, can_send_otp, check_otp
from src.utils.mail import mail , create_message
auth_router  = APIRouter()
user_service = UserService()
REFRESH_TOKEN_EXPIRY = 1

"""
sign up for the user here ..

"""
@auth_router.post("/signup" )
async def create_user_account(data : UserCreateModel  , db : AsyncSession =  Depends(get_db)):
    email  = data.email 
    user_exists = await user_service.user_exists(email , db)
    if user_exists : 
        raise HTTPException(status.HTTP_403_FORBIDDEN , detail = "User with email already exists")
    new_user =  await user_service.create_user(data , db)

    if not new_user:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR , detail  = "Internal Server Error")
    access_token = generate_access_token(user_data = { "email"  : data.email , "user_uid" : str(new_user.uid) ,"role" : new_user.role } , type =  "access")
    refresh_token = generate_refresh_token(user_data = { "email"  : data.email , "user_uid" : str(new_user.uid) ,"role" : new_user.role } , type =  "refresh")
    return JSONResponse(status_code= 201 , content = {"access_token"  : access_token , "refresh_token" : refresh_token , "user_id" : str(new_user.uid), "email" : new_user.email , "role" : new_user.role  })


""""
Sign up for the admin creation here

"""
@auth_router.post("/admin-create")
async def create_admin_user(data : AdminCreateModel , db: AsyncSession  = Depends(get_db)):
    try: 
        print("request is in create_admin_user method ")
        print(f"data is {data}")
        email = data.email 
        user_exists = await user_service.user_exists(email , db)
        print(f"user_exists is : {user_exists}")
        if user_exists:
            raise HTTPException(status.HTTP_403_FORBIDDEN , detail = "Admin with email already exists")
        new_user = await user_service.create_user(data,  db) # type: ignore
        
        if not new_user:
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR , detail  = "Internal Server Error")
        access_token = generate_access_token(user_data = { "email"  : data.email , "user_uid" : str(new_user.uid) ,"role" : new_user.role } , type =  "access")
        refresh_token = generate_refresh_token(user_data = { "email"  : data.email , "user_uid" : str(new_user.uid) ,"role" : new_user.role } , type =  "refresh")
        return JSONResponse(status_code= 201 , content = {"access_token"  : access_token , "refresh_token" : refresh_token , "user_id" : str(new_user.uid), "email" : new_user.email , "role" : new_user.role  })
    except :
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR , detail  = "Internal Sever Error.Please try again later...")

"""Getting the profile by email here  """

@auth_router.get("/get-user")
async def get_user(email : str , db : AsyncSession =  Depends(get_db)):
    result = await user_service.get_user(email , db)
    if not result : 
        raise HTTPException(status.HTTP_404_NOT_FOUND , detail  = "User not Found")
    return result
    
""" Logging Route handler """

@auth_router.post('/login')
async def login_user(data : UserLogin , db : AsyncSession = Depends(get_db)):
    user  =  await  user_service.get_user(data.email ,db)
    print(f'User is : {user}')
    
    if  user is not None :
        valid_password = verify_password(data.password, user.password_hash)  
        if valid_password : 
            access_token = generate_access_token(
                user_data = { "email"  : data.email , "user_uid" : str(user.uid) ,"role" : user.role } , type =  "access"
            )
            refresh_token  = generate_access_token(
                user_data = {"email" : data.email , "user_uid" : str(user.uid) ,"role" : user.role }, 
                type = "refresh"
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
    
"""
Route handler for generating new access token on the basis of refresh token here

"""

@auth_router.post("/refresh-token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer())
):
   
    
    
    user_data = {
        "user_uid" : token_details['sub'],
        "email":token_details['email'],
        "role" : token_details['role'],
        
    }

    new_access_token = generate_access_token(
        user_data=user_data, 
        type  = "access"
    )

    return JSONResponse(
        content={
            "access_token": new_access_token
        }
    )
    
    
    
    
    """
    Route handler for the logout here 
    
    """
    
@auth_router.post("/logout")
async def logout(token_details   : dict = Depends(AccessTokenBearer())) :
    print(f'Token details are : {token_details}')
    jti = token_details['jti']
    await add_jti_to_blocklist(jti , exp_timestamp=token_details['exp'])
    return JSONResponse(content="Logout successfully" , status_code= status.HTTP_200_OK)

"""

Route handler for the change password here

"""


@auth_router.patch("/change-password")
async def changePassword(db : AsyncSession = Depends(get_db) , token_details  : dict  =  Depends(AccessTokenBearer)):
    return JSONResponse(content = "Changed Successfully" , status_code= status.HTTP_200_OK)

"""route & handler for sending otp """
@auth_router.post("/send-otp")
@limiter.limit("5/minute")
async def sendOtp(
    request: Request,
    body: SendOtpRequest,
      background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
  
):
    
        generic_reply = {"message" : "If this email is registered, a code has been sent"}
        
        user =  await user_service.get_user_by_email(body.email , db=db)
        if user is None or user.is_verified:
            return generic_reply 
        if not await can_send_otp(body.email):
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS , detail = "Too many requests..")
        otp = generate_otp() 
        await store_top(body.email, otp)
        messages = create_message(
            recipients=[body.email], 
            subject= "Your bookly Verification code", 
            body  = f"<p>Your verification code is <b>{otp}</b>.</p><p>It expires in 10 minutes.</p>", 
        )
        background_tasks.add_task(mail.send_message, messages)
        return generic_reply
    
    
@auth_router.post("/verify-otp")
@limiter.limit("10/minute")
async def verifyOtp(request : Request , body : VerifyOTP , db:AsyncSession =  Depends(get_db)):
    result = await check_otp(body.email, body.otp)
    if result  == "expired":
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST , detail  =  "Code expired or not found")
    if result  == "too many":
        raise HTTPException(status_code =  status.HTTP_429_TOO_MANY_REQUESTS , detail = "too many Request")
    if result == "invalid":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Incorrect code")

    user = await user_service.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Code expired or not found. Request a new one")
    user.is_verified = True
    db.add(user)
    await db.commit()
    return {"message": "Email verified"}
    
    
    
