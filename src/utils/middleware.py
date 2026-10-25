from fastapi import FastAPI , status , HTTPException
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import time 
import os 
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.utils.limiter import limiter

#variables for the middleware 
PUBLIC_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}
ENV = os.getenv("ENV", "development")
MAX_BODY_SIZE = 1_000_000


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_middleware(request : Request, call_next) :
        print("Request is in custom_middleware")
        start_time =  time.time()
        response =  await call_next(request)
        
        processing_time =  time.time()
        message = f'{request.method} - {request.url} - completed after processing time'
        print("Exiting custom_middleware")
        return response
    
   
    # @app.middleware("http")
    # async def authorization(request: Request , call_next):
    #     print("Request is in authorization middleware")
    #     path = request.url.path
    #     if path in PUBLIC_PATHS : 
    #         return await call_next(request)
    #     else:
    #         if "Authorization" not in request.headers:
    #             return JSONResponse(
                    
                    
    #                 status_code=status.HTTP_401_UNAUTHORIZED, 
    #                 content={"message" : "You are unauthorized to do this action here" , 
                             
    #                          "resolution" : "Please provide new credentials"
    #                          }
    #             )
    #             print("Exiting authorization middleware")
    #         return await call_next(request)
    @app.middleware("http")
    async def security_headers(request : Request , call_next):
        print("Request is in  security _headers  middleware")
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if ENV == "production":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        if "server" in response.headers:
            del response.headers["server"]
        print("Exiting security headers")
        return response
    @app.middleware("http")
    async def limit_body_size(request : Request , call_next):
        print("Request is in limit_body_size middelware")
        content_length =  request.headers.get("content-length")
        if content_length : 
            try : 
                if int((content_length)) > MAX_BODY_SIZE : 
                    return JSONResponse(status_code=status.HTTP_413_CONTENT_TOO_LARGE  , content = "Message Limit Exceed")
            except ValueError:
                return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST , content={"detail" : "Invalid content length header"})
        print("Exiting limit_body_size middelware")
        return await call_next(request)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore
    app.add_middleware(SlowAPIMiddleware)