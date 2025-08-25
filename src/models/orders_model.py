"""Model for creating Order instances with model level validation."""

from datetime import datetime, timezone  # Used to validate current year
from decimal import Decimal
from typing import Any, List  # Used for type hints
from sqlalchemy import DateTime, Numeric, CheckConstraint, ForeignKey, text
from sqlalchemy.orm import mapped_column, Mapped, validates, relationship
from extensions import db  # Allows use of SQLAlchemy in model
from utils import checks_input  # Used with validates decorators to validate input


class Order(db.Model):
    """Model for storing orders of orders."""

    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT")
    )  # RESTRICT stops customer deletion if associated with orders
    order_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )  # timezone allows timezone support, server_default sets current time server side
    price_total: Mapped[float] = mapped_column(
        Numeric(6, 2), CheckConstraint("price_total >= 0")
    )  # Check constraint ensures positive number

    # Define many to one relationship with order_items, deleting order_items if deleted or set null
    order_items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",  # Delete associated order_items on delete
    )
    # Define relationship with books as secondary relationship through order_items
    books: Mapped[List["Book"]] = relationship(
        secondary="order_items",
        back_populates="orders",
        overlaps="order_items",  # Silences warning about overlapping foreign key columns
    )
    # Define one to many relationship with customers
    customer: Mapped["Customer"] = relationship(back_populates="orders")

    @validates("customer_id")
    def validate_customer_id(self, key: str, value: Any) -> int | None:
        """
        Validates customer_id is a positive integer. no validation of uniqueness or existence
        as that logic occurs in routes/business logic validation
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "customer_id", data_type=int)
        if value is not None and value < 1:
            raise ValueError("customer_id must be a positive integer")
        return value

    @validates("order_date")
    def validate_order_date(self, key: str, value: Any) -> datetime | None:
        """Validates order_date."""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "order_date", data_type=datetime)
        if value > datetime.now(timezone.utc):  # Prevent future datetime in order_date
            raise ValueError("order_date cannot reference future dates")
        return value

    @validates("price_total")
    def validate_price_total(self, key: str, value: Any) -> float | None:
        """Validates is float, is not null & price_total between 0 and 10000"""

        if isinstance(value, Decimal):  # Convert Decimal to float
            value = float(value)
        # Passes column name, value and model constraints to checks_input function
        value = checks_input(
            value, "price_total", data_type=float, min_val=0, max_val=9999.99
        )
        return value

    def __repr__(self) -> str | None:
        """String representation of Order instances useful for debugging."""

        # Return formatted string with street, city and country code
        return f"<Order for customer with id: {self.customer_id}, price total: {self.price_total}>"
