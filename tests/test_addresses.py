"""Test cases for Address model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Raised when validation fails on schema
from models import Address  # Used for model validation
from schemas import address_schema  # Must be written to pass schema tests

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
    assert db_session.get(Address, 1).street == "123 Test St"  # Check values in db


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", None),
        ("country_code", ""),
        ("state_code", None),
        ("state_code", ""),
        ("street", None),
        ("street", ""),
        ("postcode", None),
        ("postcode", ""),
    ],
)
def test_model_required_fields(field, value, address_instance) -> None:
    """Test that required fields are enforced in the Address model."""

    # address_instance is a pytest fixture containing a pre-made address instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(address_instance, field, value)  # Replace address_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", "USA"),  # Exceeds max length (2)
        ("country_code", "U"),  # Under min length (2)
        ("state_code", "Perth"),  # Exceeds max length (3)
        ("state_code", "p"),  # Under min length (2)
        ("city", ("a" * 51)),  # Exceeds max length (50)
        ("street", ("a" * 101)),  # Exceeds max length (100)
        ("postcode", ("a" * 11)),  # Exceeds max length (10)
    ],
)
def test_model_column_length(field, value, address_instance):
    """Test that max column character length is enforced by model."""

    # address_instance is a pytest fixture containing a pre-made address instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(address_instance, field, value)  # Replace address_instance fields with
        # invalid data per each iteration


# Test schema level validation
# ==================================================================================================


def test_schema_load(address_json: dict[str, str]) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = address_schema.load(address_json)  # Load json into dictionary
    assert data["country_code"] == "US"  # Check expected data in field


def test_schema_dump(address_instance: Address) -> None:
    """Test serialization of python object into json data using schema."""

    data = address_schema.dump(address_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["country_code"] == "US"  # Check dict key has expected value


# Ensures only required keys are deleted in below test
REQUIRED_KEYS = ["country_code", "state_code", "street", "postcode"]


def test_missing_schema_key(address_json: dict[str, str]) -> None:
    """Test deserialization while missing one key: value pair per iteration."""

    for key in REQUIRED_KEYS:  # Iterates once per key
        data = address_json.copy()  # Create fresh copy to not effect address_json
        del data[key]  # Delete subsequent key per iteration

        with pytest.raises(ValidationError):  # Check error is raised per missing key
            address_schema.load(data)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", None),
        ("country_code", ""),
        ("state_code", None),
        ("state_code", ""),
        ("street", None),
        ("street", ""),
        ("postcode", None),
        ("postcode", ""),
    ],
)
def test_schema_required_fields(address_json: dict[str, str], field, value):
    """Test schema enforces Null and empty string values for required fields."""

    data = address_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        address_schema.load(address_json)


# Allow iteration of test cases, replacing each value with invalid length string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", "USA"),  # Exceeds max length (2)
        ("country_code", "U"),  # Under min length (2)
        ("state_code", "Perth"),  # Exceeds max length (3)
        ("state_code", "p"),  # Under min length (2)
        ("city", ("a" * 51)),  # Exceeds max length (50)
        ("street", ("a" * 101)),  # Exceeds max length (100)
        ("postcode", ("a" * 11)),  # Exceeds max length (10)
    ],
)
def test_schema_column_length(address_json: dict[str, str], field, value):
    """Test schema enforces min and max column length."""

    data = address_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        address_schema.load(address_json)
