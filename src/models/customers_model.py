"""Model for creating Customer instances with model level validation."""

# from typing import Any  # Allows use of Any type hint
from typing import Any
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from sqlalchemy import (
    Connection,
    String,
    ForeignKey,
    UniqueConstraint,
    event,
    select,
    delete,
)
from sqlalchemy.orm import Mapper, mapped_column, Mapped, relationship, validates
from extensions import db  # Allows use of SQLAlchemy in model
from models import Address
from utils import checks_input

# from utils import checks_input  # Used with validates decorators to validate input


class Customer(db.Model):
    """Model for storing customers of customers."""

    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    email: Mapped[str] = mapped_column(String(254), unique=True)  # RFC 5321 max length
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Allow None
    name_id: Mapped[int] = mapped_column(
        ForeignKey("names.id", ondelete="RESTRICT"), unique=True
    )  # on_delete=RESTRICT will prevent deletion of name instance if associated to customer
    address_id: Mapped[int | None] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL"), nullable=True
    )  # Set address_id to null if address deleted instead of deleting customer

    name: Mapped["Name"] = relationship(
        back_populates="customer",  # links relationship with names
        cascade="all, delete-orphan",  # Deletes name when customer is deleted
        single_parent=True,  # Required for one to one relationship
    )
    address: Mapped["Address"] = relationship(back_populates="customers")

    __table_args__ = (UniqueConstraint("email", "name_id"),)

    @validates("email")
    def validates_email(self, key: str, value: Any) -> str | None:
        """
        Validates email exists, is string and correct length using checks_input.
        Uses validate_email python library to check valid email address
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "email", str, min_len=3, max_len=254)
        try:
            # test_environment becomes check_deliverability=True on deployment to check valid domain
            # Validates email using email_validator library
            email_info = validate_email(value, test_environment=True)
            return email_info.normalized  # Returns normalized version of address
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}") from e

    @validates("phone")
    def validate_phone(self, key: str, value: Any) -> str | None:
        """Validates phone has correct formatting, expecting E.164 formatted number"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "phone", required=False, min_len=7, max_len=20)

        if value:  # Verify number using phonenumbers library
            try:
                number = phonenumbers.parse(value, None)  # E.164 doesn't require region

            except phonenumbers.NumberParseException as e:  # Error if can't be parsed
                raise ValueError(f"Invalid phone number: {e}") from e

            if not phonenumbers.is_possible_number(number):  # Checks correct format
                raise ValueError("Invalid number format: Ensure E.164 formatting")

            if not phonenumbers.is_valid_number(number):  # Checks number in use
                raise ValueError("Number not in use: Valid format but not in use")

            return phonenumbers.format_number(
                number,
                phonenumbers.PhoneNumberFormat.E164,  # Ensures number is saved to database as E.164
            )
        return value  # Return None if value is None

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

    @validates("address_id")
    def validate_address_id(self, key: str, value: Any) -> int | None:
        """
        Validates address_id is a positive integer. no validation of uniqueness or existence
        as that logic occurs in routes/business logic validation. Nullable allowed.
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "address_id", required=False, data_type=int)
        if value is not None and value < 1:
            raise ValueError("name_id must be a positive integer")
        return value

    def __repr__(self) -> str | None:
        """String representation of Customer instances useful for debugging."""

        # Return formatted string with street, city and country code
        return f"<Customer with email: {self.email}>"


# Decorator function listens for customer delete, deletes associated address if no other customers
@event.listens_for(Customer, "after_delete")
def delete_orphaned_address(
    orm_mapper: Mapper, db_conn: Connection, deleted_customer: Customer
) -> None:
    """
    Triggers on the deletion of a customer instance. Checks for associated address instance,
    and if that address instance has no more remaining associated customers, deletes it.
    """

    if deleted_customer.address_id:  # Skips if customer has no associated address
        stmt = (  # Select max 1 customer associated with address_id
            select(1).where(Customer.address_id == deleted_customer.address_id).limit(1)
        )
        exists = db_conn.scalar(stmt)  # Will be truthy if stmt = 1 else false

        if not exists:  # If no customers associated to address
            db_conn.execute(  # Create SQL statement to delete address by id
                delete(Address).where(Address.id == deleted_customer.address_id)
            )
