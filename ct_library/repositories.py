from contextlib import AbstractContextManager
from typing import Callable, Sequence

from sqlalchemy import func
from sqlalchemy.orm import aliased
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
            return (
                session.query(Book)
                .join(BookLeaseLog, isouter=True)
                .order_by(Book.title, BookLeaseLog.created_at.desc())
                .all()
            )

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

    def get_by_author_id(self, author_id) -> Sequence[Book]:
        with self.session_factory() as session:
            return session.query(Book).where(Book.author_id == author_id).all()

    def filter_by_availability(self, available: bool) -> Sequence[Book]:
        with self.session_factory() as session:
            LatestLog = aliased(BookLeaseLog)

            query = (
                select(Book)
                .outerjoin(
                    LatestLog,
                    (Book.id == LatestLog.book_id)
                    & (
                        LatestLog.created_at
                        == (
                            select(func.max(BookLeaseLog.created_at))
                            .where(BookLeaseLog.book_id == Book.id)
                            .scalar_subquery()
                        )
                    ),
                )
                .where(
                    (LatestLog.id.is_(None)) | (LatestLog.returned_at.isnot(None))
                    if available
                    else LatestLog.returned_at.is_(None) & (LatestLog.id.isnot(None))
                )
            )
            return session.scalars(query).all()


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
            return session.query(BookLeaseLog).where(Book.author_id == author_id).all()

    def save(self, book: BookLeaseLog) -> BookLeaseLog:
        with self.session_factory() as session:
            session.add(book)
            session.commit()
            session.refresh(book)
            return book

    def get_by_book_id(self, book_id) -> Sequence[BookLeaseLog]:
        with self.session_factory() as session:
            return session.query(BookLeaseLog).where(Book.id == book_id).all()
