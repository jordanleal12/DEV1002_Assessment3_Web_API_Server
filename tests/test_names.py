"""Test cases for Name model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask.testing import FlaskClient
from sqlalchemy import insert  # Used for type hints
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session  # Raised when validation fails on schema
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from models import Name, Customer  # Used for model validation
from schemas import name_schema  # Used for schema tests
from conftest import NameFields  # Used for type hints

# Test model level validation
# ==================================================================================================


def test_name_creation(db_session: scoped_session[Session]) -> None:
    """Test the model by creating a new name instance."""

    # Create name instance using Name model
    name = Name(
        first_name="John",
        last_name="Smith",
    )

    db_session.add(name)  # Adds name to db fixture session from conftest.py
    db_session.commit()

    assert name.id is not None  # Test name instance has been created in database
    assert db_session.get(Name, 1).first_name == "John"  # Check values in db


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", None),
        ("first_name", ""),
        ("first_name", "    "),  # Whitespace only should fail
    ],
)
def test_name_model_required_fields(
    field: NameFields, value: str | None, name_instance: Name
) -> None:
    """Test that required fields are enforced in the Name model."""

    # name_instance is a pytest fixture containing a pre-made name instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(name_instance, field, value)  # Replace name_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", ("a" * 51)),  # Exceeds max length (50)
        ("first_name", "aa"),  # Under min length (3)
        ("last_name", ("a" * 51)),  # Exceeds max length (50)
    ],
)
def test_name_model_column_length(
    field: NameFields, value: str, name_instance: Name
) -> None:
    """Test that max column character length is enforced by model."""

    # name_instance is a pytest fixture containing a pre-made name instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(name_instance, field, value)  # Replace name_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", 123),  # String only
        ("first_name", ["first", "name"]),  # String only
        ("first_name", {"first": "name"}),  # String only
        ("last_name", 123),  # String only
        ("last_name", ["last", "name"]),  # String only
        ("last_name", {"last": "name"}),  # String only
    ],
)
def test_name_model_valid_char(
    field: NameFields, value: str | int, name_instance: Name
) -> None:
    """Test that invalid character/type is enforced by model."""

    # name_instance is a pytest fixture containing a pre-made name instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(name_instance, field, value)  # Replace name_instance fields with
        # invalid data per each iteration


# Test schema level validation
# ==================================================================================================


def test_name_schema_load(name_json: dict[str, str]) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = name_schema.load(name_json)  # Load json into dictionary
    assert data["first_name"] == "John"  # Check expected data in field


def test_name_schema_dump(name_instance: Name) -> None:
    """Test serialization of python object into json data using schema."""

    data = name_schema.dump(name_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["first_name"] == "John"  # Check dict key has expected value


def test_name_missing_schema_key(name_json: dict[str, str]) -> None:
    """Test deserialization while missing required field(s)."""

    del name_json["first_name"]  # Delete required field

    with pytest.raises(ValidationError):  # Check error is raised for missing fields
        name_schema.load(name_json)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", None),
        ("first_name", ""),
        ("first_name", "    "),  # Whitespace should be stripped
    ],
)
def test_name_schema_required_fields(
    name_json: dict[str, str], field: NameFields, value: None | str
) -> None:
    """Test schema enforces Null and empty string values for required fields."""

    data = name_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        name_schema.load(name_json)


# Allow iteration of test cases, replacing each value with invalid length string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", ("a" * 51)),  # Exceeds max length (50)
        ("first_name", "aa"),  # Under min length (3)
        ("last_name", ("a" * 51)),  # Exceeds max length (50)
    ],
)
def test_name_schema_column_length(
    name_json: dict[str, str], field: NameFields, value: str
) -> None:
    """Test schema enforces min and max column length."""

    data = name_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        name_schema.load(name_json)


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", 123),  # String only
        ("first_name", ["first", "name"]),  # String only
        ("first_name", {"first": "name"}),  # String only
        ("last_name", 123),  # String only
        ("last_name", ["last", "name"]),  # String only
        ("last_name", {"last": "name"}),  # String only
    ],
)
def test_name_schema_valid_char(
    name_json: dict[str, str], field: NameFields, value: str | int
) -> None:
    """Test that invalid character/type is enforced by schema."""

    data = name_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        name_schema.load(name_json)


# Test database level validation (no integration tests as name accessed through customers/authors)
# ==================================================================================================


def test_name_database_not_null(
    db_session: scoped_session[Session],
    name_json: dict[str, str],
) -> None:
    """
    Use an insert statement to bypass model validation and insert NULL value into a NOT NULL
    enforced column in the database, raising IntegrityError
    """

    name_json["first_name"] = None  # Replace required field value with None
    # Create SQL insert statement, bypassing model validation
    stmt = insert(Name).values(name_json)

    with pytest.raises(IntegrityError):  # Expected error
        db_session.execute(stmt)  # Error should trigger on execute, commit not required


# Test relationship handling
# ==================================================================================================


def test_customer_name_relationship(
    name_instance: Name, customer_instance: Customer
) -> None:
    """Test that Name is correctly linked to Customer model,
    and that name data can be linked through the relationship."""

    name = name_instance  # Assign conftest.py name fixture to name
    customer = customer_instance  # Assign conftest.py customer fixture to customer

    # Check that name can be accessed through customer
    assert customer.name.first_name == name_instance.first_name
    # Check that customer can be accessed through name
    assert name.customer.email == customer_instance.email


def test_delete_customer_deletes_name(
    db_session: scoped_session[Session],
    name_instance: Name,
    customer_instance: Customer,
) -> None:
    """Test Name relationship with customers, asserting deleting customer deletes associated name"""

    customer = customer_instance
    name_id = name_instance.id  # Save ID before delete
    db_session.delete(customer)  # Delete customer linked to name
    db_session.commit()

    assert db_session.get(Customer, customer.id) is None  # Check customer deleted
    assert db_session.get(Name, name_id) is None  # Check name instance deleted


def test_direct_name_delete_fails(
    db_session: scoped_session[Session],
    name_instance: Name,
    customer_instance: Customer,
) -> None:
    """Deleting a Name directly should be blocked while a Customer references it."""

    with pytest.raises(IntegrityError):
        db_session.delete(name_instance)  # Should raise error
        db_session.commit()

    db_session.rollback()  # Clears error before asserting name exists
    assert db_session.get(Name, name_instance.id) is not None


def test_delete_name_fk_fails(
    db_session: scoped_session[Session],
    name_instance: Name,
    customer_instance: Customer,
) -> None:
    """
    Test Name relationship with customers, asserting deleting name_id in customers
    raises integrity error and doesn't delete name
    """

    with pytest.raises(IntegrityError):
        customer_instance.name_id = None  # Should raise error
        db_session.commit()

    db_session.rollback()  # Clears error before asserting

    assert db_session.get(Customer, customer_instance.name_id)  # Check name_id present
    assert db_session.get(Name, name_instance.id)  # Check name instance not deleted
