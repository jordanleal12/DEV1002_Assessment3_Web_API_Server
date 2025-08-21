"""Model for creating Names instances with model level validation."""

from typing import Any  # Used for type hints
from sqlalchemy import String  # ,ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, validates
from extensions import db  # Allows use of SQLAlchemy in model
from utils import checks_input  # Used with validates decorators to validate input

# from utils import checks_input  # Used with validates decorators to validate input


class Name(db.Model):
    """Model for storing names of customers."""

    __tablename__ = "names"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    first_name: Mapped[str] = mapped_column(String(50))  # Enforces max length of 50
    last_name: Mapped[str | None] = mapped_column(String(50))  # Optional, max length 50

    customer: Mapped["Customer"] = relationship(
        back_populates="name",  # Links to name in customer model
    )

    @validates("first_name")
    def validate_first_name(self, key: str, value: Any) -> str | None:
        """Validates first_name exists, is a string and is 3-50 characters."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "first_name", min_len=3, max_len=50)
        return value.title()  # Title not upper as some names hyphenated etc.

    @validates("last_name")
    def validate_last_name(self, key: str, value: Any) -> str | None:
        """Validates last_name is a string and is less than 50 characters if value provided."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "last_name", required=False, max_len=50)
        return value.title() if value else None  # Return titled last_name if given

    def __repr__(self) -> str | None:
        """String representation of Name instances useful for debugging."""

        # Return formatted string with first and last name
        if self.last_name:
            return f"<first name: {self.first_name}, last name: {self.last_name}>"
        # Return one name if no last name
        return f"<name: {self.first_name}"
