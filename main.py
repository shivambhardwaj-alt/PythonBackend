from fastapi import FastAPI , status ,HTTPException
from fastapi.responses import JSONResponse
from src.books.routes import bookRouter
from contextlib import asynccontextmanager
from src.database.database import get_db
from src.database.database import engine
from sqlmodel import SQLModel
from src.database.model import Book
from src.auth.router import auth_router ,me_router
from src.utils.middleware import register_middleware 
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is running ...")
    print("Creating Tables...")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    print("Server has been stopped")
version = "v1"
app = FastAPI(
    version = version,
    title="Bookly",
    lifespan=life_span,
    description= "A REST api for books"

)




register_middleware(app)
app.add_middleware(
    CORSMiddleware, 
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts = ["localhost" , "127.0.0.1"]
)


@app.get("/health" , tags = ["health"])
async def health_check():
    try: 
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Version is working fine"})
    except:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR , detail = "First path is broken !")

app.include_router(bookRouter , prefix = f"/api/{version}/books" , tags=['books'])
app.include_router(auth_router, prefix = f'/api/{version}/auth' , tags = ['auth'])
app.include_router(me_router , prefix = f'/api/{version}/me' , tags = ['myself'])



