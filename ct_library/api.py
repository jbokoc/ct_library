from typing import Annotated, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.params import Header
from fastapi.responses import Response

from ct_library.serializers import (
    AuthorInSerializer,
    AuthorOutSerializer,
    BookFilterParams,
    BookInSerializer,
    BookLeaseLogInSerializer,
    BookLeaseLogOutSerializer,
    BookOutSerializer,
)

router = APIRouter()


@router.get("/")
async def root(request: Request):
    """
    Root endpoint for the API.
    """
    return {"books": "books"}


@router.get("/books/")
@inject
def books_list(
    filter_params: Annotated[BookFilterParams, Query()],
    book_service=Depends(Provide["book_service"]),
) -> List[BookOutSerializer]:
    """
    Retrieves a list of all books.
    """
    # for o in book_service.get_all(filter_params):
    #     print(type(o))
    #     print(o)
    #
    # return []
    #
    return [
        BookOutSerializer.model_validate(book)
        for book in book_service.get_all(filter_params)
    ]


@router.post("/authors/{author_id}/books/")
@inject
def create_book(
    author_id: int,
    book: BookInSerializer,
    book_service=Depends(Provide["book_service"]),
) -> BookOutSerializer:
    """
    Creates a new book entry.
    """
    book = book_service.create(book, author_id)
    return BookOutSerializer.model_validate(book)


@router.get("/authors/{author_id}/books/")
@inject
def books_list_by_author(
    author_id: int, book_service=Depends(Provide["book_service"])
) -> List[BookOutSerializer]:
    """
    Retrieves a list of books by a specific author.
    """
    books = book_service.get_by_author_id(author_id)
    return [BookOutSerializer.model_validate(book) for book in books]


@router.get("/books/{book_id}")
@inject
def book_get(
    book_id: int, book_service=Depends(Provide["book_service"])
) -> BookOutSerializer:
    """
    Retrive book detail
    """
    book = book_service.get_by_id(book_id)
    return BookOutSerializer.model_validate(book)


@router.get("/authors/")
@inject
def authors_list(
    author_service=Depends(Provide["author_service"]),
) -> List[AuthorOutSerializer]:
    """
    Retrieves a list of authors.
    """
    authors = author_service.get_all()
    return [AuthorOutSerializer.model_validate(author) for author in authors]


@router.post("/authors/", status_code=201)
@inject
def authors_create(
    author_serializer: AuthorInSerializer,
    author_service=Depends(Provide["author_service"]),
) -> AuthorOutSerializer:
    """
    Creates a new author entry.
    """
    author = author_service.create(author_serializer)

    return AuthorOutSerializer.model_validate(author)


@router.get("/authors/{author_id}")
@inject
def authors_get(
    author_id: int,
    author_service=Depends(Provide["author_service"]),
) -> AuthorOutSerializer:
    """
    Retrieves a specific author by ID.
    """
    author = author_service.get_by_id(author_id)

    return AuthorOutSerializer.model_validate(author)


@router.delete("/authors/{author_id}", status_code=204)
@inject
def authors_delete(
    author_id: int,
    author_service=Depends(Provide["author_service"]),
) -> None:
    """
    Deletes an author by ID.
    """
    author = author_service.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    author_service.delete_by_id(author_id)


@router.put(
    "/books/{book_id}/leases/",
    response_model=BookLeaseLogOutSerializer,
    responses={
        201: {"model": BookLeaseLogOutSerializer},
        200: {"model": BookLeaseLogOutSerializer},
    },
)
@inject
def put_book_lend(
    book_id: int,
    book_lease_log: BookLeaseLogInSerializer,
    user_id: Annotated[str | None, Header()] = None,
    x_user_id: Annotated[str | None, Header()] = None,
    book_lease_service=Depends(Provide["book_lease_log_service"]),
) -> Response:
    """
    Lease or return book.
    """

    if not user_id and not x_user_id:
        raise HTTPException(
            status_code=400, detail="Either user-id or x-user-id header is required"
        )
    book_lease = book_lease_service.lease_or_return_book(
        book_id=book_id, user_id=user_id or x_user_id, book_lease_log=book_lease_log
    )

    status_code = 200 if book_lease.returned_at else 201
    return Response(
        status_code=status_code,
        content=BookLeaseLogOutSerializer.model_validate(book_lease).model_dump_json(),
        media_type="application/json",
    )


@router.get("/books/{book_id}/leases/")
@inject
def get_book_leases(
    book_id: int,
    book_lease_service=Depends(Provide["book_lease_log_service"]),
) -> List[BookLeaseLogOutSerializer]:
    """
    Get the lend status of a book.
    :param book_id: The ID of the book to get the lend status for.
    :return: The lend status of the book.
    """
    book_leases = book_lease_service.get_by_book_id(book_id)
    return [
        BookLeaseLogOutSerializer.model_validate(book_lease)
        for book_lease in book_leases
    ]
