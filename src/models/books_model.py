"""Model for creating Book instances with model level validation."""

from datetime import datetime  # Used to validate current year
from typing import Any, List  # Used for type hints
from sqlalchemy import Boolean, Integer, Numeric, String, CheckConstraint  # ,ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from extensions import db  # Allows use of SQLAlchemy in model
from utils import checks_input  # Used with validates decorators to validate input


class Book(db.Model):
    """Model for storing books of customers."""

    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    isbn: Mapped[str] = mapped_column(String(13))  # nullable=False by default
    title: Mapped[str] = mapped_column(String(255))  # Extremely long titles exist
    series: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Allow None
    publication_year: Mapped[int] = mapped_column(
        Integer, CheckConstraint("publication_year >= 1000")
    )  # Upper year bound not enforced at DB level as not dynamic
    discontinued: Mapped[bool] = mapped_column(Boolean, default=False)
    price: Mapped[float] = mapped_column(Numeric(5, 2), CheckConstraint("price >= 0"))
    quantity: Mapped[int] = mapped_column(Integer, CheckConstraint("quantity >= 0"))

    # Define many to one relationship with book_authors, deleting book_author if deleted or set null
    book_authors: Mapped[List["BookAuthor"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )
    # Define many to many relationship with authors as secondary relationship through book_authors
    authors: Mapped[List["Author"]] = relationship(
        secondary="book_authors",
        back_populates="books",
        overlaps="book_authors",  # Silences warning about overlapping foreign key columns
    )
    # Define many to one relationship with order_items
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="book")
    # Define many to many relationship with orders as secondary relationship through order_items
    orders: Mapped[List["Order"]] = relationship(
        secondary="order_items",
        back_populates="books",
        overlaps="order_items",  # Silences warning about overlapping foreign key columns
    )

    __mapper_args__ = {"confirm_deleted_rows": False}  # Silences expected delete
    # warning as expects cascade delete but we manually delete

    @validates("isbn")
    def validate_isbn(self, key: str, value: Any) -> str | None:
        """Validates isbn is string, exists, and is 10-13 numeric characters long."""

        # Passes column name, value and model constraints to checks_input function
        if isinstance(value, str):  # Reformat string without hyphen and whitespace
            value.replace("-", "").replace(" ", "")
        value = checks_input(value, "isbn", str, min_len=10, max_len=13)
        if not value.isnumeric():  # Raises ValueError if not numeric characters
            raise ValueError("ISBN must contain numeric characters only")
        return value

    @validates("title")
    def validate_title(self, key: str, value: Any) -> str | None:
        """Validates title is string, exists and between 1 and 255 characters."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "title", str, max_len=255)
        return value.title()  # Convert to title case for consistency

    @validates("series")
    def validate_series(self, key: str, value: Any) -> str | None:
        """Validates is string and max character length enforced unless null"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "series", required=False, max_len=255)
        return value.title() if value else None  # Convert to titlecase for consistency

    @validates("publication_year")
    def validate_publication_year(self, key: str, value: Any) -> int | None:
        """Validates is int, is not null & value between 1000 and current year"""

        current_year = datetime.now().year  # Get current year for validation
        value = checks_input(  # Passes column name, value and model constraints to checks_input
            value, "publication_year", data_type=int, min_val=1000, max_val=current_year
        )
        return value

    @validates("discontinued")
    def validate_discontinued(self, key: str, value: Any) -> bool | None:
        """Validates is bool and not none"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "discontinued", data_type=bool)
        return value

    @validates("price")
    def validate_price(self, key: str, value: Any) -> int | None:
        """Validates is int, is not null & price between 0 and 1000"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "price", data_type=float, min_val=0, max_val=999.99)
        if value == 0 and self.discontinued is True:
            raise ValueError("Price can only be 0 if discontinued")
        return value

    @validates("quantity")
    def validate_quantity(self, key: str, value: Any) -> int | None:
        """Validates is int, is not null & not negative"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "quantity", data_type=int, min_val=0)
        return value

    def __repr__(self) -> str | None:
        """String representation of Book instances useful for debugging."""

        shortened_title = (  # Shorten title output if too long
            self.title[:25] + "..." if len(self.title) > 25 else self.title
        )
        # Return formatted string with street, city and country code
        return f"<Book title: {shortened_title}, price: {self.price}>"
