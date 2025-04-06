from dependency_injector import containers, providers
from fastapi import FastAPI

from ct_library.models import engine_factory, session_factory
from ct_library.repositories import (
    AuthorRepository,
    BookLendLogRepository,
    BookRepository,
)
from ct_library.services import (
    AuthorService,
    BookLeaseService,
    BookService,
)


class Container(containers.DeclarativeContainer):
    """
    This container is used to register the dependencies for the applicatiin.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[".services", ".api", ".repositories"]
    )
    db_engine = providers.Singleton(engine_factory, db_url="sqlite:///database.db")
    db_session_factory = providers.Factory(session_factory, engine=db_engine)
    app = providers.Singleton(FastAPI)

    author_repository = providers.Factory(
        AuthorRepository, session_factory=db_session_factory
    )
    book_repository = providers.Factory(
        BookRepository, session_factory=db_session_factory
    )
    book_lease_log_repository = providers.Singleton(
        BookLendLogRepository, session_factory=db_session_factory
    )

    book_service = providers.Singleton(
        BookService,
        book_repository=book_repository,
        author_repository=author_repository,
    )
    author_service = providers.Singleton(
        AuthorService, author_repository=author_repository
    )
    book_lease_log_service = providers.Singleton(
        BookLeaseService,
        book_lease_log_repository=book_lease_log_repository,
        book_repository=book_repository,
    )
