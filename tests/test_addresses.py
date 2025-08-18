"""Test cases for Address model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask.testing import FlaskClient  # Used for type hints
from conftest import AddressFields  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from sqlalchemy.orm import scoped_session  # Raised when validation fails on schema
from models import Address  # Used for model validation
from schemas import address_schema  # Used for schema tests


# Test model level validation
# ==================================================================================================


def test_address_creation(db_session: scoped_session[Session]) -> None:
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
def test_model_required_fields(
    field: AddressFields, value: str | None, address_instance: Address
) -> None:
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
        ("postcode", ("a" * 1)),  # Under min length (2)
        ("postcode", ("a" * 11)),  # Exceeds max length (10)
    ],
)
def test_model_column_length(
    field: AddressFields, value: str, address_instance: Address
) -> None:
    """Test that max column character length is enforced by model."""

    # address_instance is a pytest fixture containing a pre-made address instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(address_instance, field, value)  # Replace address_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", "12"),  # Alpha characters only
        ("country_code", 12),  # String only
        ("state_code", "123"),  # Alpha characters only
        ("state_code", 123),  # String only
        ("city", 123),  # String only
        ("street", 123),  # String only
        ("postcode", "123@#$"),  # Alphanumeric characters, whitespace and hyphens only
        ("postcode", 123456),  # String only
    ],
)
def test_model_valid_char(
    field: AddressFields, value: str | int, address_instance: Address
) -> None:
    """Test that invalid character/type is enforced by model."""

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
def test_schema_required_fields(
    address_json: dict[str, str], field: AddressFields, value: None | str
) -> None:
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
        ("postcode", "1"),  # Under min length (2)
        ("postcode", ("1" * 11)),  # Exceeds max length (10)
    ],
)
def test_schema_column_length(
    address_json: dict[str, str], field: AddressFields, value: str
) -> None:
    """Test schema enforces min and max column length."""

    data = address_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        address_schema.load(address_json)


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("country_code", "12"),  # Alpha characters only
        ("country_code", 12),  # String only
        ("state_code", "123"),  # Alpha characters only
        ("state_code", 123),  # String only
        ("city", 123),  # String only
        ("street", 123),  # String only
        ("postcode", "123@#$"),  # Alphanumeric characters, whitespace and hyphens only
        ("postcode", 123456),  # String only
    ],
)
def test_schema_valid_char(
    address_json: dict[str, str], field: AddressFields, value: str | int
) -> None:
    """Test that invalid character/type is enforced by schema."""

    data = address_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        address_schema.load(address_json)


# Test integration
# ==================================================================================================


def test_create_address(client: FlaskClient, address_json: dict[str, str]) -> None:
    """Test CRUD integration by creating a new address from
    a fake json POST request using the test client."""

    response = client.post(  # Retrieve fake json data from Flask test client
        "/addresses",
        json=address_json,  # A fixture that returns a dict containing address fields
    )
    assert response.status_code == 201  # Response for successful creation
    assert response.json["street"] == "123 Test St"  # Check correct values in response


def test_get_address(client: FlaskClient, address_instance: Address) -> None:
    """Test CRUD integration by asserting address instance is in database
    using a fake GET request using the test client."""

    addr_id = address_instance.id  # Assign address id based on id of instance in db
    response = client.get(f"/addresses/{addr_id}")  # Simulate get request using client
    assert response.status_code == 200  # Assert successful request
    assert response.json["country_code"] == "US"  # Assert data matches expected value


def test_get_addresses(
    db_session: scoped_session[Session], client: FlaskClient, address_instance: Address
) -> None:
    """Test CRUD integration by asserting multiple address instances are in database
    using a fake GET request using the test client."""

    addr2 = Address(  # Create second Address instance
        country_code="AU",
        state_code="NSW",
        city="Sydney",
        street="42 Wallaby Way",
        postcode="2000",
    )
    db_session.add(addr2)
    db_session.commit()  # Commit second Address to db

    response = client.get("/addresses")  # Simulate GET request for all addresses
    assert response.status_code == 200  # Assert successful request
    assert len(response.json) == 2  # Assert expected number of address instances


def test_update_address(
    db_session: scoped_session[Session], client: FlaskClient, address_instance: Address
) -> None:
    """Test CRUD integration by asserting address instance is updated in database
    using a fake PUT request using the test client."""

    address_id = address_instance.id  # Assign address id based on id of instance in db
    new_data = {"street": "69 Oxford St"}
    response = client.patch(f"/addresses/{address_id}", json=new_data)  # Simulate Patch

    assert response.status_code == 200  # Assert successful request
    assert response.json["street"] == "69 Oxford St"  # Assert new value in response
    db_session.refresh(address_instance)  # Refresh db
    assert address_instance.street == "69 Oxford St"  # Assert db instance updated


def test_delete_address(
    db_session: scoped_session[Session], client: FlaskClient, address_instance: Address
) -> None:
    """Test CRUD integration by asserting address instance is deleted in database
    using a fake DELETE request using the test client."""

    addr_id = address_instance.id  # Assign address id based on id of instance in db
    response = client.delete(f"/addresses/{addr_id}")  # Simulate DELETE request
    assert response.status_code == 204  # Assert successful deletion
    assert db_session.get(Address, addr_id) is None  # Check Address instance deleted
