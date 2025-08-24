"""Model for creating Author instances with model level validation."""

from typing import Any, List  # Allows use of Any type hint
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from extensions import db  # Allows use of SQLAlchemy in model
from utils import checks_input

# from utils import checks_input  # Used with validates decorators to validate input


class Author(db.Model):
    """Model for storing authors of authors."""

    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    name_id: Mapped[int] = mapped_column(
        ForeignKey("names.id", ondelete="RESTRICT"), unique=True
    )  # on_delete=RESTRICT will prevent deletion of name instance if associated to author

    name: Mapped["Name"] = relationship(
        back_populates="author",  # links relationship with names
        cascade="all, delete-orphan",  # Deletes name when author is deleted
        single_parent=True,  # Required for one to one relationship
    )
    # Define relationship with book_authors, deleting book_author instance if deleted or set null
    book_authors: Mapped[List["BookAuthor"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )
    # Define relationship with books as secondary relationship through book_authors
    books: Mapped[List["Book"]] = relationship(
        secondary="book_authors",
        back_populates="authors",
        overlaps="book_authors",  # Silences warning about overlapping foreign key columns
    )

    __table_args__ = (UniqueConstraint("name_id"),)
    __mapper_args__ = {"confirm_deleted_rows": False}  # Silences expected delete
    # warning as expects cascade delete but we manually delete with listener event in book_authors

    @validates("name_id")
    def validate_name_id(self, key: str, value: Any) -> int | None:
        """
        Validates name_id is a positive integer. no validation of uniqueness or existence
        as that logic occurs in routes/business logic validation
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "name_id", data_type=int)
        if value is not None and value < 1:
            raise ValueError("name_id must be a positive integer")
        return value

    def __repr__(self) -> str | None:
        """String representation of Author instances useful for debugging."""

        # Return formatted string with street, city and country code
        return f"<Author with name: {self.name.first_name}>"
