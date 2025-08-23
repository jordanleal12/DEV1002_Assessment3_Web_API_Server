"""Model for creating Author instances with model level validation."""

from typing import Any  # Allows use of Any type hint
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

    __table_args__ = (UniqueConstraint("name_id"),)

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
