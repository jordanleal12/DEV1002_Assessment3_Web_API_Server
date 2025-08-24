"""Model for creating BookAuthor instances with model level validation."""

from sqlalchemy import Connection, ForeignKey, UniqueConstraint, delete, select, event
from sqlalchemy.orm import Mapper, mapped_column, Mapped, relationship
from extensions import db  # Allows use of SQLAlchemy in model
from models import Author, Book


class BookAuthor(db.Model):
    """
    Model for instance of book_authors table, a junction table between books and authors.
    using a composite primary key of book_id and author_id
    """

    __tablename__ = "book_authors"
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )  # Composite primary key of book_id and author_id
    author_id: Mapped[int] = mapped_column(
        ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True
    )  # Cascade on delete so deletion of attached book or attached author deletes book_author

    # Links relationship with book
    book: Mapped["Book"] = relationship(
        back_populates="book_authors", overlaps="authors,books"
    )  # Silences warning about overlapping foreign key columns
    # Links relationship with author
    author: Mapped["Author"] = relationship(
        back_populates="book_authors", overlaps="authors,books"
    )  # Silences warning about overlapping foreign key columns

    # Combination of book_id and author_id must be unique for use as composite key
    __table_args__ = (UniqueConstraint("book_id", "author_id"),)
    __mapper_args__ = {"confirm_deleted_rows": False}  # Silences expected delete
    # warning as expects cascade delete but we manually delete in business logic


# Decorator function listens for customer delete, deletes associated author if no other books
@event.listens_for(BookAuthor, "after_delete")
def delete_orphaned_author(
    orm_mapper: Mapper, db_conn: Connection, deleted_book_author: BookAuthor
) -> None:
    """
    Triggers on the deletion of a book_authors instance. Checks for associated author instance,
    and if that author instance has no more remaining associated books, deletes it.
    """

    author_stmt = (  # Select max 1 book_author instance associated with author_id
        select(1).where(BookAuthor.author_id == deleted_book_author.author_id).limit(1)
    )
    author_exists = db_conn.scalar(author_stmt)  # Will be truthy if stmt = 1 else false

    if not author_exists:  # If no book_author instances associated to author.
        db_conn.execute(  # Create SQL statement to delete author by id
            delete(Author).where(Author.id == deleted_book_author.author_id)
        )

    book_stmt = (  # Select max 1 book_author instance associated with book_id
        select(1).where(BookAuthor.book_id == deleted_book_author.book_id).limit(1)
    )
    book_exists = db_conn.scalar(book_stmt)  # Will be truthy if stmt = 1 else false

    if not book_exists:  # If no book_author instances associated to book.
        db_conn.execute(  # Create SQL statement to delete book by id
            delete(Book).where(Book.id == deleted_book_author.book_id)
        )
