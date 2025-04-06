import datetime
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declarative_base,
    mapped_column,
    sessionmaker,
)


def engine_factory(db_url: str) -> Engine:
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
    return engine


def session_factory(engine) -> Callable[..., AbstractContextManager[Session]]:
    """
    Create a session factory for the database.
    :param engine: The database engine.
    :return: A session factory.
    """
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return session


def create_database(engine: Engine) -> None:
    """
    Create the database tables. For tests only
    :param engine: The database engine.
    """
    Base.metadata.create_all(engine)


declarative_base = declarative_base()


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    #    books: Mapped[List["Book"]] = relationship(back_populates="author")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True
    )


class Book(Base):
    __tablename__ = "book"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(
        ForeignKey("author.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True
    )


class BookLeaseLog(Base):
    __tablename__ = "book_lease_log"
    __table_args__ = (
        UniqueConstraint("book_id", "returned_at", name="_uq_book_lease_log"),  # type: ignore
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    user_id: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=False,
    )
    returned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=None, nullable=True
    )
