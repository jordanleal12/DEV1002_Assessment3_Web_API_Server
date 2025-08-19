"""Model for creating Customer instances with model level validation."""

# from typing import Any  # Allows use of Any type hint
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship  # , validates
from extensions import db  # Allows use of SQLAlchemy in model

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
    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL")
    )  # Set address_id to null if address deleted instead of deleting customer

    name: Mapped["Name"] = relationship(
        back_populates="customer",  # links relationship with names
        single_parent=True,  # Required for one to one relationship
    )
    address: Mapped["Address"] = relationship(back_populates="customers")

    __table_args__ = (UniqueConstraint("email", "name_id"),)

    def __repr__(self) -> str | None:
        """String representation of Customer instances useful for debugging."""

        # Return formatted string with street, city and country code
        return f"<Customer with email: {self.email}>"
