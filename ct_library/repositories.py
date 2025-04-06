from contextlib import AbstractContextManager
from typing import Callable, Sequence

from sqlalchemy.sql import delete, select
from sqlmodel import Session

from ct_library.models import Author, Book, BookLeaseLog


class BaseRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory


class AuthorRepository(BaseRepository):
    def get_all(self) -> Sequence[Author]:
        with self.session_factory() as session:
            # return session.execute(select(Author).order_by(Author.name)).all()

            return session.execute(select(Author).order_by(Author.name)).scalars().all()

    def get_by_id(self, author_id) -> Author:
        with self.session_factory() as session:
            return session.query(Author).where(Author.id == author_id).one()

    def create(self, author: Author) -> Author:
        with self.session_factory() as session:
            session.add(author)
            session.commit()
            session.refresh(author)
            return author

    def delete_by_id(self, author_id) -> None:
        with self.session_factory() as session:
            session.execute(delete(Author).where(Author.id == author_id))
            session.commit()


class BookRepository(BaseRepository):
    def get_all(self) -> Sequence[Book]:
        with self.session_factory() as session:
            return session.query(Book).order_by(Book.title).all()

    def get_by_id(self, book_id) -> Book:
        with self.session_factory() as session:
            return session.query(Book).where(Book.id == book_id).one()

    def create(self, book: Book) -> Book:
        with self.session_factory() as session:
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def update_book(self, book_id, book_data):
        pass

    def delete_by_id(self, book_id) -> None:
        with self.session_factory() as session:
            session.execute(delete(Book).where(Book.id == book_id))
            session.commit()


class BookLendLogRepository(BaseRepository):
    def get_last_lease_log(self, book_id) -> BookLeaseLog:
        with self.session_factory() as session:
            return (
                session.query(BookLeaseLog)
                .where(Book.id == book_id)
                .order_by(BookLeaseLog.created_at.desc())
                .limit(1)
                .one()
            )

    def get_by_id(self, book_id) -> BookLeaseLog:
        with self.session_factory() as session:
            return session.query(BookLeaseLog).where(Book.id == book_id).one()

    def get_by_author_id(self, author_id) -> Sequence[BookLeaseLog]:
        with self.session_factory() as session:
            return (
                session.execute(select(BookLeaseLog).where(Book.author_id == author_id))
                .scalars()
                .all()
            )

    def save(self, book: BookLeaseLog) -> BookLeaseLog:
        with self.session_factory() as session:
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def get_by_book_id(self, book_id) -> Sequence[BookLeaseLog]:
        with self.session_factory() as session:
            return session.query(BookLeaseLog).where(Book.id == book_id).all()

    #
    # def return_book(self, book: Book, user_id: int) -> Book:
    #     with self.session_factory() as session:
    #         session.add(book)
    #         session.commit()
    #         session.refresh(book)
    #         return book
