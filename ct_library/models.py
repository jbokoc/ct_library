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
    desc,
    null,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    configure_mappers,
    declarative_base,
    mapped_column,
    relationship,
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
    lease_logs = relationship("BookLeaseLog", back_populates="book", lazy="immediate")

    @hybrid_property
    def available(self):
        if not self.lease_logs:
            return True
        print("Lease logs:", self.lease_logs)
        latest_log = max(self.lease_logs, key=lambda log: log.created_at)
        return latest_log.returned_at is not None

    @available.expression
    def available(cls):
        subquery = (
            select(BookLeaseLog.returned_at)
            .where(BookLeaseLog.book_id == cls.id)
            .order_by(desc(BookLeaseLog.created_at))
            .group_by(BookLeaseLog.book_id)
            .scalar_subquery()
        ).label("latest_returned_at")  # Give the subquery a label
        return subquery.isnot(null())


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
    book = relationship("Book", back_populates="lease_logs", lazy="immediate")


configure_mappers()
