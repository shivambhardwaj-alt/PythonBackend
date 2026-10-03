import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.schema import BookCreateModel, BookUpdateModel
from src.database.model import Book


class BookService:
    

   
    async def get_all_books(self, db: AsyncSession):
        try:
            statement = select(Book).order_by(desc(Book.createdAt))
            result = await db.execute(statement)

            
            return result.scalars().all()

        except HTTPException:
            raise
        except Exception as e:
            print("get_all_books failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            ) from e

  
    async def get_book(self, book_uid: str, db: AsyncSession):
        try:
            book_uuid = uuid.UUID(str(book_uid))        
            statement = select(Book).where(Book.uid == book_uuid)
            result = await db.execute(statement)
            book = result.scalars().first()             

            if book is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Result not found",
                )
            return book

        except ValueError:                              
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Result not found",
            )
        except HTTPException:
            raise
        except Exception as e:
            print("get_book failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            ) from e

   
    async def create_book(self, data: BookCreateModel, db: AsyncSession):
        try:
            new_book = Book(**data.model_dump())       

            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)
            return new_book

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()                        
            print("create_book failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            ) from e

    
    async def update_book(self, book_uid: str, data: BookUpdateModel, db: AsyncSession):
        try:
           
            book_to_update = await self.get_book(book_uid, db)

            update_data = data.model_dump(exclude_unset=True)   
            for key, value in update_data.items():
                setattr(book_to_update, key, value)

            book_to_update.updatedAt = datetime.now()

            db.add(book_to_update)
            await db.commit()
            await db.refresh(book_to_update)
            return book_to_update

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            print("update_book failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            ) from e

    
    async def delete_book(self, book_uid: str, db: AsyncSession):
        try:
            book_to_delete = await self.get_book(book_uid, db)   

            await db.delete(book_to_delete)
            await db.commit()
            return True

        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            print("delete_book failed:", repr(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            ) from e