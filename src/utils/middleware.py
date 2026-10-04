from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import time 

def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_middleware(request : Request, call_next) :
        start_time =  time.time()
        response =  await call_next(request)
        processing_time =  time.time()
        message = f'{request.method} - {request.url} - completed after processing time'
        print(message)
        return response
    
   
    @app.middleware("http")
    async def authorization(request: Request, call_next):
        if "Authorization" not in request.headers:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "Not Authenticated",
                    "resolution": "Please provide the right credentials to proceed"
                }
            )

        return await call_next(request)