from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.books.schema import BookCreateModel, BookUpdateModel, BookResponse
from src.auth.dependencies import RoleChecker
from .service import BookService

bookRouter = APIRouter()
book_service = BookService()


admin_only = Depends(RoleChecker(["admin"]))
any_user = Depends(RoleChecker(["admin", "user"]))


@bookRouter.get(
    "/",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[any_user],
)
async def get_all_books(db: AsyncSession = Depends(get_db)):
    return await book_service.get_all_books(db)



@bookRouter.post(
    "/add-book",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[admin_only],
)
async def create_book(
    book_data: BookCreateModel,
    db: AsyncSession = Depends(get_db),
):
    return await book_service.create_book(data=book_data, db=db)


@bookRouter.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[any_user],
)
async def get_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    return await book_service.get_book(book_uid=book_id, db=db)



@bookRouter.patch(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[admin_only],
)
async def update_book(
    book_id: str,
    book_update_data: BookUpdateModel,
    db: AsyncSession = Depends(get_db),
):
    return await book_service.update_book(
        book_uid=book_id,
        data=book_update_data,
        db=db,
    )



@bookRouter.delete(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[admin_only],
)
async def delete_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    await book_service.delete_book(book_uid=book_id, db=db)
    return {"message": "Book deleted successfully"}