"""Model for creating Address instances with model level validation."""

from typing import Any, List  # Used for type hints
from sqlalchemy import String  # ,ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from extensions import db  # Allows use of SQLAlchemy in model
from utils import checks_input  # Used with validates decorators to validate input


class Address(db.Model):
    """Model for storing addresses of customers."""

    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    country_code: Mapped[str] = mapped_column(String(2))  # nullable=False by default
    state_code: Mapped[str] = mapped_column(String(3))
    city: Mapped[str | None] = mapped_column(String(50), nullable=True)  # Allow None
    street: Mapped[str] = mapped_column(String(100))
    postcode: Mapped[str] = mapped_column(String(10))  # Postcodes have max length of 10

    customers: Mapped[List["Customer"]] = relationship(  # List as many to one
        back_populates="address",  # Links to address in customer model
        passive_deletes=True,  # Tells SQLAlchemy not to interfere with db for ON DELETE actions
    )

    @validates("country_code")
    def validate_country_code(self, key: str, value: Any) -> str | None:
        """Validates country_code is 2 alphabetical characters long for IS0 3166 country codes."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "country_code", str, min_len=2, max_len=2)
        if not value.isalpha():  # Raises ValueError if not alphabetical letters
            raise ValueError("country_code must contain alphabetical letters only")
        return value.upper()  # Convert to uppercase for consistency

    @validates("state_code")
    def validate_state_code(self, key: str, value: Any) -> str | None:
        """Validates state_code is 2-3 alphabetical characters long for ISO 3166-2 state codes."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "state_code", str, min_len=2, max_len=3)
        if not value.isalpha():  # Raises ValueError if not alphabetical letters
            raise ValueError("street_code must contain alphabetical letters only")
        return value.upper()  # Convert to uppercase for consistency

    @validates("city")
    def validate_city(self, key: str, value: Any) -> str | None:
        """Validates is string and max character length enforced unless null"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "city", required=False, max_len=50)
        return value.title() if value else None  # Convert to titlecase for consistency

    @validates("street")
    def validate_street(self, key: str, value: Any) -> str | None:
        """Validates is string, is not null & max character length is enforced"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "street", str, max_len=100)
        return value.title()  # Convert to titlecase for consistency

    @validates("postcode")
    def validate_postcode(self, key: str, value: Any) -> str | None:
        """Validates is string, is not null & max character length is enforced"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "postcode", str, min_len=2, max_len=10)
        value = value.replace("-", "").replace(" ", "")
        if not value.isalnum():
            raise ValueError(
                "postcode may contain only alphanumeric, whitespace or hyphen characters"
            )
        return value.upper()  # Convert to alphanumeric only uppercase for consistency

    def __repr__(self) -> str | None:
        """String representation of Address instances useful for debugging."""

        # Shorten street output if too long
        shortened_street = (
            self.street[:25] + "..." if len(self.street) > 25 else self.street
        )
        # Return formatted string with street, city and country code
        return f"<Address {shortened_street}, {self.city}, {self.country_code}>"
