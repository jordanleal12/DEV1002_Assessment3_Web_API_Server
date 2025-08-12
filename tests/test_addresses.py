"""Test cases for Address model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

import pytest  # Required for @parametrize decorator
from models import Address  # Address model must be created to pass tests

ONE_OH_ONE_CHARS = "a" * 101  # Constant for checking enforcement of max string length

# Test model level validation
# ==================================================================================================


def test_address_creation(db_session):
    """Test the model by creating a new address instance."""

    # Create address instance using Address model
    address = Address(
        country_code="US",
        state_code="CA",
        city="San Francisco",
        street="123 Test St",
        postcode="12345",
    )

    db_session.add(address)  # Adds address to db fixture session from conftest.py
    db_session.commit()

    assert address.id is not None  # Test address instance has been created in database
    assert (
        db_session.get(Address, 1).street == "123 Test St"
    )  # Check values saved correctly


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives value error for ISO codes instead, so we define expected errors
@pytest.mark.parametrize(
    "field, value, expected_error",
    [
        ("country_code", None, ValueError),
        ("state_code", None, ValueError),
        ("street", None, ValueError),
        ("postcode", None, ValueError),
    ],
)
def test_required_fields(db_session, field, value, expected_error, address_data):
    """Test that required fields are enforced in the Address model."""

    # address_data is a dict containing address fields defined as a fixture in conftest.py
    address_data[field] = value  # Replaces each field with None as the test iterates

    # Checks that an error is raised when a required field is None
    with pytest.raises(expected_error):
        # Uses kwargs to turn address_data dict into Address model fields
        # and replace each field with None one by one as the test iterates
        address = Address(**address_data)
        db_session.add(address)
        db_session.commit()


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", "USA"),
        ("country_code", "U"),
        ("state_code", "Perth"),
        ("state_code", "p"),
        ("city", ONE_OH_ONE_CHARS),
        ("street", ONE_OH_ONE_CHARS),
        ("postcode", ONE_OH_ONE_CHARS),
    ],
)
def test_iso_code_length(db_session, field, value, address_data):
    """Test that country_code string length is enforced."""

    # address_data is a dict containing address fields defined as a fixture in conftest.py
    # Replace each field with each tuple value per iteration
    address_data[field] = value
    # Check that the expected error defined in parametrize is raised
    with pytest.raises(ValueError):
        address = Address(
            **address_data
        )  # Uses kwargs to turn address_data into Address instance per iteration
        db_session.add(address)
