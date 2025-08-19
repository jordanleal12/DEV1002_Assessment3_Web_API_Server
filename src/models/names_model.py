from sqlalchemy import String  # ,ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship  # , validates
from extensions import db  # Allows use of SQLAlchemy in model

# from utils import checks_input  # Used with validates decorators to validate input


class Name(db.Model):
    """Model for storing names of customers."""

    __tablename__ = "names"
    id: Mapped[int] = mapped_column(primary_key=True)  # Primary Key column
    first_name: Mapped[str] = mapped_column(String(50))  # Enforces max length of 50
    last_name: Mapped[str | None] = mapped_column(String(50))  # Optional, max length 50

    customer: Mapped["Customer"] = relationship(
        back_populates="name",  # Links to name in customer model
        cascade="all, delete-orphan",  # Delete name if customer is deleted
    )
