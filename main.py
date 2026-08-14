from fastapi import FastAPI
from src.books.routes import bookRouter
from contextlib import asynccontextmanager
from src.database.database import get_db
from src.database.database import engine
from sqlmodel import SQLModel
from src.database.model import Book
from src.auth.router import auth_router
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
app.include_router(bookRouter , prefix = f"/api/{version}/books" , tags=['books'])
app.include_router(auth_router, prefix = f'/api/{version}/auth' , tags = ['auth'])


