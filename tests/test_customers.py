"""Test cases for Customer model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask_sqlalchemy.session import Session  # Used for type hints
from sqlalchemy.orm import scoped_session  # Raised when validation fails on schema
from models import Customer
from models.addresses_model import Address
from models.names_model import Name


# Test model level validation
# ==================================================================================================


def test_address_creation(
    db_session: scoped_session[Session], address_instance: Address, name_instance: Name
) -> None:
    """Test the model by creating a new address instance."""

    # Create address instance using Customer model
    customer = Customer(
        name_id=name_instance.id,
        email="johnsmith@email.com",
        phone="+61412345678",
        address_id=address_instance.id,
    )

    db_session.add(customer)  # Adds address to db fixture session from conftest.py
    db_session.commit()

    assert customer.id is not None  # Test address instance has been created in database
    assert (
        db_session.get(Customer, 1).email == "johnsmith@email.com"
    )  # Check values in db
