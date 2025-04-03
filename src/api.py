from fastapi import APIRouter, Request

import models

router = APIRouter()


@router.get("/")
async def root(request: Request):
    return {"books": "books"}


@router.get("/books/")
def books_list():
    models.Book.get_all()

    return [
        {"name": "Lord of the rings, fellowship of the rings!", "bla": "kek"},
    ]


@router.post("/books/")
def create_book(book: dict):
    """
    Creates a new book entry.
    :param book: A dictionary containing book details.
    :return: The created book entry.
    """
    # In a real application, you would save the book to a database here.
    # For this example, we will just return the book as is.
    return {"book": book}


@router.get("/books/{book_id}")
def book_get(book_id: int):
    """
    Retrive book detail
    """
    pass


@router.get("/authors/")
def authors_list():
    pass


@router.post("/authors/")
def authors_create():
    pass
