from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.exc import NoResultFound

from ct_library.exceptions import Forbidden
from ct_library.models import Author, Book, BookLeaseLog
from ct_library.repositories import (
    AuthorRepository,
    BookLendLogRepository,
    BookRepository,
)
from ct_library.serializers import (
    AuthorInSerializer,
    BookFilterParams,
    BookInSerializer,
    BookLeaseLogInSerializer,
)


class AuthorService:
    """
    Service class for author operations.
    """

    def __init__(self, author_repository: AuthorRepository):
        self.author_repo = author_repository

    def create(self, author: AuthorInSerializer) -> Author:
        """
        Create a new author.
        :return: The created author.
        """
        data = author.model_dump()
        model = Author(**data)
        model = self.author_repo.create(model)
        print(model)
        return model

    def get_all(self) -> list[Author]:
        """
        Get all authors.
        :return: A list of authors.
        """
        return self.author_repo.get_all()

    def get_by_id(self, author_id: int) -> Author:
        """
        Get an author by ID.
        :return: The author with the specified ID.
        """
        return self.author_repo.get_by_id(author_id)

    def delete_by_id(self, author_id: int) -> None:
        """
        Delete an author by ID.
        :return: None
        """
        self.author_repo.delete_by_id(author_id)


class BookService:
    """
    Service class for book operations.
    """

    def __init__(
        self, book_repository: BookRepository, author_repository: AuthorRepository
    ):
        self.book_repo = book_repository
        self.author_repo = author_repository

    def create(self, book: BookInSerializer, author_id: int) -> Book:
        """
        Create a new book.
        :return: The created book.
        """
        data = book.model_dump()
        author = self.author_repo.get_by_id(author_id)

        model = Book(**data)
        model.author_id = author.id
        model = self.book_repo.create(model)
        return model

    def get_all(self, filter_params: BookFilterParams) -> Sequence[Book]:
        """
        Get all books.
        :return: A list of books.
        """
        if isinstance(filter_params.available, bool):
            # TODO: Fix this repo - DRY
            return self.book_repo.filter_by_availability(
                available=bool(filter_params.available)
            )
        else:
            return self.book_repo.get_all()

    def get_by_id(self, book_id: int) -> Book:
        """
        Get a book by ID.
        :return: The book with the specified ID.
        """
        return self.book_repo.get_by_id(book_id)

    def get_by_author_id(self, author_id: int) -> Sequence[Book]:
        """
        Get books by author ID.
        :return: A list of books by the specified author.
        """
        return self.book_repo.get_by_author_id(author_id)

    def delete_by_id(self, book_id: int) -> None:
        """
        Delete a book by ID.
        :return: None
        """
        self.book_repo.delete_by_id(book_id)


class BookLeaseService:
    """
    Service class for book lend log operations.
    """

    def __init__(
        self,
        book_lease_log_repository: BookLendLogRepository,
        book_repository: BookRepository,
    ):
        self.book_lease_log_repo = book_lease_log_repository
        self.book_repo = book_repository

    def lease_or_return_book(
        self, book_id: int, user_id: int, book_lease_log: BookLeaseLogInSerializer
    ) -> BookLeaseLog:
        """
        Create a new book lend log.
        :return: The created book lend log.
        """
        user_id = int(user_id)
        book = self.book_repo.get_by_id(book_id)

        try:
            book_lease_obj = self.book_lease_log_repo.get_last_lease_log(
                book_id=book.id
            )

            if book_lease_obj.returned_at is not None:
                book_lease_obj = BookLeaseLog(
                    book_id=book.id, user_id=user_id, returned_at=None
                )
            else:
                if book_lease_obj.user_id != user_id:
                    raise Forbidden(
                        f"Book {book.title} is already lent to another user"
                    )
                book_lease_obj.returned_at = book_lease_log.returned_at or datetime.now(
                    timezone.utc
                )

        except NoResultFound:
            book_lease_obj = BookLeaseLog(
                book_id=book.id, user_id=user_id, returned_at=None
            )

        book_lease_obj = self.book_lease_log_repo.save(book_lease_obj)
        return book_lease_obj

    def get_by_book_id(self, book_id: int) -> Sequence[BookLeaseLog]:
        """
        Get a book lend log by book ID.
        :return: The book lend log with the specified book ID.
        """
        return self.book_lease_log_repo.get_by_book_id(book_id)
