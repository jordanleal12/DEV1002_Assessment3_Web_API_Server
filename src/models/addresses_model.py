"""Model for creating Address instances with model level validation."""

from sqlalchemy.orm import (
    validates,
)  # @validates decorator provides model level validation
from extensions import db  # Allows use of SQLAlchemy in model


class Address(db.Model):
    """Model for storing addresses of customers."""

    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False)  # Enforces max length of 2
    state_code = db.Column(db.String(3), nullable=False)  # Enforces max length of 3
    city = db.Column(db.String(50))  # Optional as not all addresses have city
    street = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)  # Max length of postcodes is 10

    @validates("country_code")
    def validate_country_code(self, key, value) -> str:
        """Validates country_code is 2 alphabetical characters long for IS0 3166 country codes."""

        # Return ValueError if null, not string or len != 2, else return uppercase value
        if not isinstance(value, str) or len(value) != 2:
            raise ValueError("ISO 3166 country code must be 2 alphabetical characters")
        return value.upper()  # Convert to uppercase for consistency

    @validates("state_code")
    def validate_state_code(self, key, value) -> str:
        """Validates state_code is 2-3 alphabetical characters long for ISO 3166-2 state codes."""

        # Return ValueError if null, not string or len not 2 or 3, else return uppercase value
        if not isinstance(value, str) or len(value) not in (2, 3):
            raise ValueError(
                "ISO 3166-2 subdivision code must be 2 or 3 alphabetical characters"
            )
        return value.upper()  # Convert to uppercase for consistency

    @validates("city")
    def validate_city(self, key, value) -> str | None:
        """Validates is string and max character length enforced unless null"""

        # Return None if null, ValueError if not string or len > 50, else return titlecase value
        if value:
            if not isinstance(value, str) or len(value) > 50:
                raise ValueError(
                    "If City is not null, must be a string of no more than 50 characters"
                )
            return value.title()
        return None

    @validates("street")
    def validate_street(self, key, value) -> str:
        """Validates is string, is not null & max character length is enforced"""

        # Return ValueError if null, not string or len > 100, else return titlecase value
        if not isinstance(value, str) or len(value) > 100:
            raise ValueError("Street must be a string of no more than 100 characters")
        return value.title()

    @validates("postcode")
    def validate_postcode(self, key, value):
        """Validates is string, is not null & max character length is enforced"""

        # Return ValueError if null, not string or len > 10, else return titlecase value
        if not isinstance(value, str) or len(value) > 10:
            raise ValueError("Postcode must be a string of no more than 10 characters")
        return value

    def __repr__(self) -> str:
        """String representation of Address instances useful for debugging."""

        # Shorten street output if too long
        shortened_street = (
            self.street[:25] + "..." if len(self.street) > 25 else self.street
        )
        # Return formatted string with street, city and country code
        return f"<Address {shortened_street}, {self.city}, {self.country_code}>"
