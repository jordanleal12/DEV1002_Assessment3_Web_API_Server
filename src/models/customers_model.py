"""Model for creating Customer instances with model level validation."""

# from typing import Any  # Allows use of Any type hint
from sqlalchemy import (
    Connection,
    String,
    ForeignKey,
    UniqueConstraint,
    event,
    select,
    delete,
)
from sqlalchemy.orm import Mapper, mapped_column, Mapped, relationship  # , validates
from extensions import db  # Allows use of SQLAlchemy in model
from models import Address

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
        single_parent=True,  # Required for one to one relationship
    )
    address: Mapped["Address"] = relationship(back_populates="customers")

    __table_args__ = (UniqueConstraint("email", "name_id"),)

    def __repr__(self) -> str | None:
        """String representation of Customer instances useful for debugging."""

        # Return formatted string with street, city and country code
        return f"<Customer with email: {self.email}>"


# Decorator function listens for customer delete, deletes associated address if no other customers
@event.listens_for(Customer, "after_delete")
def delete_orphaned_address(
    orm_mapper: Mapper, db_conn: Connection, deleted_cust: Customer
) -> None:
    """
    Triggers on the deletion of a customer instance. Checks for associated address instance,
    and if that address instance has no more remaining associated customers, deletes it.
    """

    if deleted_cust.address_id:  # Skips if customer has no associated address
        # Count how many customers associated with address_id
        stmt = select(1).where(Customer.address_id == deleted_cust.address_id).limit(1)
        exists = db_conn.scalar(stmt)
        # Run the count query using the DB connection (gets a number like 0 or 1+).
        if not exists:  # If no Customers left using this address...
            # Build and run a delete: "Delete Address where id matches the old address_id".
            db_conn.execute(
                delete(Address).where(Address.id == deleted_cust.address_id)
            )
