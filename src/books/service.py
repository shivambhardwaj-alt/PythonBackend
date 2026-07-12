from sqlmodel import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.books.schema import BookCreateModel, BookUpdateModel
from src.database.model import Book


class BookService:

    async def get_all_books(self, db: AsyncSession):
        statement = select(Book).order_by(desc(Book.createdAt))
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_book(self, book_uid: str, db: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await db.execute(statement)
        return result.scalars().first()

    async def create_book(
        self,
        data: BookCreateModel,
        db: AsyncSession,
    ):
        book_data = data.model_dump()

        new_book = Book(**book_data)

        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)

        return new_book

    async def update_book(
        self,
        book_uid: str,
        data: BookUpdateModel,
        db: AsyncSession,
    ):
        book_to_update = await self.get_book(book_uid, db)

        if book_to_update is None:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(book_to_update, key, value)

        db.add(book_to_update)
        await db.commit()
        await db.refresh(book_to_update)

        return book_to_update

    async def delete_book(
        self,
        book_uid: str,
        db: AsyncSession,
    ):
        book_to_delete = await self.get_book(book_uid, db)

        if book_to_delete is None:
            return None

        await db.delete(book_to_delete)
        await db.commit()

        return True