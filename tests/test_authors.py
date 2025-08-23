"""Test cases for Author model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError  # Raised when validation fails on schema
from sqlalchemy.orm import scoped_session  # Used for type hints
from conftest import AuthorFields  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from models import Author, Name  # Used for model validation
from schemas import author_schema  # Used for schema tests

# Test model level validation
# ==================================================================================================


def test_author_creation(
    db_session: scoped_session[Session],
    name_instance: Name,
) -> None:
    """Test the model by creating a new author instance."""

    # Create author instance using Author model
    author = Author(
        name_id=name_instance.id,
    )

    db_session.add(author)  # Adds author to db fixture session from conftest.py
    db_session.commit()

    assert author.id is not None  # Test author instance created in database
    assert db_session.get(Author, 1).name.first_name == "John"  # Check values


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("name_id", None),
        ("name_id", ""),
        ("name_id", "  "),  # Whitespace only should fail
    ],
)
def test_author_model_required_fields(
    field: AuthorFields, value: str | None, author_instance: Author
) -> None:
    """Test that required fields are enforced in the Author model."""

    # author_instance is a pytest fixture containing a pre-made author instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(author_instance, field, value)  # Replace author_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("name_id", 0),  # Positive integer only
        ("name_id", "1"),  # Integer only
        ("name_id", ["1", "2"]),  # Integer only
        ("name_id", {"1", "2"}),  # Integer only
    ],
)
def test_author_model_valid_char(
    field: AuthorFields, value: str | int, author_instance: Author
) -> None:
    """Test that invalid character/type is enforced by model."""

    # author_instance is a pytest fixture containing a pre-made author instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(author_instance, field, value)  # Replace author_instance fields
        # with invalid data per each iteration


# Test schema level validation
# ==================================================================================================


def test_author_schema_load(author_json: dict[str, str]) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = author_schema.load(author_json)  # Load json into dictionary
    assert data["name"]["first_name"] == "John"  # Check expected data in field


def test_author_schema_dump(author_instance: Author) -> None:
    """Test serialization of python object into json data using schema."""

    data = author_schema.dump(author_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["name"]["first_name"] == "John"  # Check dict key has expected value


def test_author_missing_schema_key(author_json: dict[str, str]) -> None:
    """Test deserialization while missing one key: value pair per iteration."""

    data = author_json.copy()  # Create fresh copy to not effect author_json
    del data["name"]  # Delete required key

    with pytest.raises(ValidationError):  # Check error is raised for missing key
        author_schema.load(data)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("name", None),
        ("name", ""),
        ("name", "   "),  # Whitespace should be stripped
    ],
)
def test_author_schema_required_fields(
    author_json: dict[str, str], field: AuthorFields, value: None | str
) -> None:
    """Test schema enforces Null and empty string values for required fields."""

    data = author_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        author_schema.load(author_json)


# Test database level validation
# ==================================================================================================


def test_author_database_not_null(
    db_session: scoped_session[Session],
    author_json: dict[str, str],
) -> None:
    """
    Use an insert statement to bypass model validation and insert NULL value into a NOT NULL
    enforced column in the database, raising IntegrityError
    """

    data = author_json.copy()
    del data["name"]  # Remove nested name values
    # Create SQL insert statement, bypassing model validation
    stmt = insert(Author).values(data)

    with pytest.raises(IntegrityError):  # Expected error
        db_session.execute(stmt)  # Error should trigger on execute, commit not required
