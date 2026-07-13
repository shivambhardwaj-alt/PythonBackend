from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import get_db
from src.books.schema import Book ,  BookCreateModel, BookUpdateModel
from .service import BookService
from src.auth.dependencies import RefreshTokenBearer

bookRouter = APIRouter()

book_service = BookService()


access_token_bearer = RefreshTokenBearer()

@bookRouter.get("/")
async def get_all_books(db: AsyncSession = Depends(get_db) , user_details = Depends(access_token_bearer)):
    books = await book_service.get_all_books(db)
    return books


@bookRouter.post(
    "/add-book",
    status_code=status.HTTP_201_CREATED,
    response_model=BookCreateModel,
)
async def create_book(
    book_data: BookCreateModel,
    db: AsyncSession = Depends(get_db),
):
    result = await book_service.create_book(
        data=book_data,
        db=db,
    )
    return result


@bookRouter.get(
    "/{book_id}",

    status_code=status.HTTP_200_OK,
)
async def get_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await book_service.get_book(
        book_uid=book_id,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return result


@bookRouter.patch(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookUpdateModel,
)
async def update_book(
    book_id: str,
    book_update_data: BookUpdateModel,
    db: AsyncSession = Depends(get_db),
):
    result = await book_service.update_book(
        book_uid=book_id,
        data=book_update_data,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return result


@bookRouter.delete(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=bool,
)
async def delete_book(
    book_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await book_service.delete_book(
        book_uid=book_id,
        db=db,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    return result