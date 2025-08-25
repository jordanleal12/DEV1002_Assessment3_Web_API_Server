"""Model for creating Orderitem instances with model level validation."""

from typing import Any
from sqlalchemy import (
    CheckConstraint,
    Connection,
    ForeignKey,
    Integer,
    UniqueConstraint,
    delete,
    event,
    select,
)
from sqlalchemy.orm import Mapper, mapped_column, Mapped, relationship, validates
from extensions import db  # Allows use of SQLAlchemy in model
from models import Order, Book
from utils import checks_input


class OrderItem(db.Model):
    """
    Model for instance of order_items table, a junction table between books and orders.
    using a composite primary key of book_id and order_id
    """

    __tablename__ = "order_items"
    book_id: Mapped[int] = mapped_column(  # Composite key of book_id and order_id
        ForeignKey("books.id", ondelete="RESTRICT"), primary_key=True
    )  # RESTRICT prevents deletion of books associated with orders
    order_id: Mapped[int] = mapped_column(  # Composite key of book_id and order_id
        ForeignKey("orders.id", ondelete="CASCADE"), primary_key=True
    )  # CASCADE deletes order_item if order deleted
    # Check constraint on quantity so it cant be zero
    quantity: Mapped[int] = mapped_column(
        Integer, CheckConstraint("quantity >= 0"), default=1
    )
    # One to one relationship with books
    book: Mapped["Book"] = relationship(  # Links relationship with book
        back_populates="order_items", overlaps="orders,books"
    )  # Silences warning about overlapping foreign key columns
    # One to one relationship with orders
    order: Mapped["Order"] = relationship(  # Links relationship with order
        back_populates="order_items", overlaps="orders,books"
    )  # Silences warning about overlapping foreign key columns

    # Combination of book_id and order_id must be unique for use as composite key
    __table_args__ = (UniqueConstraint("book_id", "order_id"),)

    @validates("book_id")
    def validate_book_id(self, key: str, value: Any) -> int | None:
        """
        Validates book_id is a positive integer. no validation of uniqueness or existence
        as that logic occurs in routes/business logic validation
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "book_id", data_type=int)
        if value is not None and value < 1:
            raise ValueError("book_id must be a positive integer")
        return value

    @validates("order_id")
    def validate_order_id(self, key: str, value: Any) -> int | None:
        """
        Validates order_id is a positive integer. no validation of uniqueness or existence
        as that logic occurs in routes/business logic validation
        """

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "order_id", data_type=int)
        if value is not None and value < 1:
            raise ValueError("order_id must be a positive integer")
        return value

    @validates("quantity")
    def validate_quantity(self, key: str, value: Any) -> int | None:
        """Validates is int, is not null & not negative"""

        # Passes column name, value and model constraints to checks_input function
        value = checks_input(value, "quantity", data_type=int, min_val=1)
        return value


# Decorator function listens for order_item delete, deletes associated order if no other order_items
@event.listens_for(OrderItem, "after_delete")
def delete_orphaned_order(
    orm_mapper: Mapper, db_conn: Connection, deleted_order_item: OrderItem
) -> None:
    """
    Triggers on the deletion of order_item instance. Checks for associated order instance,
    and if that order instance has no more remaining associated order_items, deletes it.
    """

    stmt = (  # Select max 1 order_item associated with order_id
        select(1).where(OrderItem.order_id == deleted_order_item.order_id).limit(1)
    )
    exists = db_conn.scalar(stmt)  # Will be truthy if stmt = 1 else false

    if not exists:  # If no order_items associated to order
        db_conn.execute(  # Create SQL statement to delete order by id
            delete(Order).where(Order.id == deleted_order_item.order_id)
        )
