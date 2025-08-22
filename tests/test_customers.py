"""Test cases for Customer model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask.testing import FlaskClient  # Used for type hints
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError  # Raised when validation fails on schema
from sqlalchemy.orm import scoped_session  # Used for type hints
from conftest import CustomerFields  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from models import Customer, Name, Address  # Used for model validation
from schemas import customer_schema  # Used for schema tests

# Test model level validation
# ==================================================================================================


def test_customer_creation(
    db_session: scoped_session[Session],
    address_instance: Address,
    name_instance: Name,
) -> None:
    """Test the model by creating a new customer instance."""

    # Create customer instance using Customer model
    customer = Customer(
        email="johnsmith@email.com",
        phone="+61412345678",
        name_id=name_instance.id,
        address_id=address_instance.id,
    )

    db_session.add(customer)  # Adds customer to db fixture session from conftest.py
    db_session.commit()

    assert customer.id is not None  # Test customer instance created in database
    assert db_session.get(Customer, 1).email == "johnsmith@email.com"  # Check values


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", None),
        ("email", ""),
        ("email", "  "),  # Whitespace only should fail
        ("name_id", None),
        ("name_id", ""),
        ("name_id", "  "),  # Whitespace only should fail
    ],
)
def test_customer_model_required_fields(
    field: CustomerFields, value: str | None, customer_instance: Customer
) -> None:
    """Test that required fields are enforced in the Customer model."""

    # customer_instance is a pytest fixture containing a pre-made customer instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(
            customer_instance, field, value
        )  # Replace customer_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", ("a" * 254 + "@hotmail.com")),  # Exceeds max length (254)
        ("email", "a@"),  # Under min length (3)
        ("phone", ("1" * 21)),  # Exceeds max length (20)
        ("phone", "123456"),  # Under min length (7)
    ],
)
def test_customer_model_column_length(
    field: CustomerFields, value: str, customer_instance: Customer
) -> None:
    """Test that max column character length is enforced by model."""

    # customer_instance is a pytest fixture containing a pre-made customer instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(
            customer_instance, field, value
        )  # Replace customer_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", 123456),  # String only
        ("email", "not_valid_email@invalid_domain"),
        ("email", ["john_smith", "@gmail.com"]),  # Not valid email address
        ("email", {"john_smith": "@gmail.com"}),  # String only
        ("phone", "+61412345%$#"),  # Valid regex only
        ("phone", 61412345678),  # String only
        ("phone", "+61111111111"),  # Valid phone number only
        ("phone", ["+614", "12345678"]),  # String only
        ("phone", {"+614": "12345678"}),  # String only
        ("name_id", 0),  # Positive integer only
        ("name_id", "1"),  # Integer only
        ("name_id", ["1", "2"]),  # Integer only
        ("name_id", {"1", "2"}),  # Integer only
        ("address_id", 0),  # Positive integer only
        ("address_id", "1"),  # Integer only
        ("address_id", ["1", "2"]),  # Integer only
        ("address_id", {"1", "2"}),  # Integer only
    ],
)
def test_customer_model_valid_char(
    field: CustomerFields, value: str | int, customer_instance: Customer
) -> None:
    """Test that invalid character/type is enforced by model."""

    # customer_instance is a pytest fixture containing a pre-made customer instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(customer_instance, field, value)  # Replace customer_instance fields
        # with invalid data per each iteration


# Test schema level validation
# ==================================================================================================


def test_customer_schema_load(customer_json: dict[str, str]) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = customer_schema.load(customer_json)  # Load json into dictionary
    assert data["email"] == "johnsmith@email.com"  # Check expected data in field


def test_customer_schema_dump(customer_instance: Customer) -> None:
    """Test serialization of python object into json data using schema."""

    data = customer_schema.dump(customer_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["email"] == "johnsmith@email.com"  # Check dict key has expected value


# Ensures only required keys are deleted in below test
REQUIRED_KEYS = ["email", "name"]


def test_customer_missing_schema_key(customer_json: dict[str, str]) -> None:
    """Test deserialization while missing one key: value pair per iteration."""

    for key in REQUIRED_KEYS:  # Iterates once per key
        data = customer_json.copy()  # Create fresh copy to not effect customer_json
        del data[key]  # Delete subsequent key per iteration

        with pytest.raises(ValidationError):  # Check error is raised per missing key
            customer_schema.load(data)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", None),
        ("email", ""),
        ("email", "  "),  # Whitespace should be stripped
        ("name", None),
        ("name", ""),
        ("name", "   "),  # Whitespace should be stripped
    ],
)
def test_customer_schema_required_fields(
    customer_json: dict[str, str], field: CustomerFields, value: None | str
) -> None:
    """Test schema enforces Null and empty string values for required fields."""

    data = customer_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        customer_schema.load(customer_json)


# Allow iteration of test cases, replacing each value with invalid length string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", ("a" * 254 + "@hotmail.com")),  # Exceeds max length (254)
        ("email", "a@"),  # Under min length (3)
        ("phone", ("1" * 21)),  # Exceeds max length (20)
        ("phone", "123456"),  # Under min length (7)
    ],
)
def test_customer_schema_column_length(
    customer_json: dict[str, str], field: CustomerFields, value: str
) -> None:
    """Test schema enforces min and max column length."""

    data = customer_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        customer_schema.load(customer_json)


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("email", 123456),  # String only
        ("email", "not_valid_email@invalid_domain"),
        ("email", ["john_smith", "@gmail.com"]),  # Not valid email address
        ("email", {"john_smith": "@gmail.com"}),  # String only
        ("phone", "+61412345%$#"),  # Valid regex only
        ("phone", 61412345678),  # String only
        ("phone", ["+614", "12345678"]),  # String only
        ("phone", {"+614": "12345678"}),  # String only
        ("address_id", 0),  # Positive integer only
        ("address_id", ["1", "2"]),  # Integer only
        ("address_id", {"1", "2"}),  # Integer only
    ],
)
def test_customer_schema_valid_char(
    customer_json: dict[str, str], field: CustomerFields, value: str | int
) -> None:
    """Test that invalid character/type is enforced by schema."""

    data = customer_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        customer_schema.load(customer_json)


# Test integration/routes
# ==================================================================================================


def test_create_customer(client: FlaskClient, customer_json: dict[str, str]) -> None:
    """Test CRUD integration by creating a new customer from
    a fake json POST request using the test client."""

    response = client.post(  # Retrieve fake json data from Flask test client
        "/customers",
        json=customer_json,  # A fixture that returns a dict containing customer fields
    )
    assert response.status_code == 201  # Response for successful creation
    assert response.json["email"] == "johnsmith@email.com"  # Check correct response


def test_get_customer(client: FlaskClient, customer_instance: Customer) -> None:
    """Test CRUD integration by asserting customer instance is in database
    using a fake GET request using the test client."""

    cust_id = customer_instance.id  # Assign customer id based on id of instance in db
    response = client.get(f"/customers/{cust_id}")  # Simulate get request using client
    assert response.status_code == 200  # Assert successful request
    assert response.json["email"] == "johnsmith@email.com"  # Assert expected data


def test_get_customers(
    db_session: scoped_session[Session],
    client: FlaskClient,
    customer_instance: Customer,
    customer2_instance: Customer,
) -> None:
    """Test CRUD integration by asserting multiple customer instances are in database
    using a fake GET request using the test client."""

    response = client.get("/customers")  # Simulate GET request for all customers
    assert response.status_code == 200  # Assert successful request
    assert len(response.json) == 2  # Assert expected number of customer instances


def test_patch_update_customer(
    db_session: scoped_session[Session],
    client: FlaskClient,
    customer_instance: Customer,
) -> None:
    """Test CRUD integration by asserting customer instance is updated in database
    using a fake PUT request using the test client."""

    customer_id = customer_instance.id  # Assign customer id based on instance id
    new_data = {"phone": "+61421404292"}
    response = client.patch(
        f"/customers/{customer_id}", json=new_data
    )  # Simulate Patch

    assert response.status_code == 200  # Assert successful request
    assert response.json["phone"] == "+61421404292"  # Assert new value in response
    db_session.refresh(customer_instance)  # Refresh db
    assert customer_instance.phone == "+61421404292"  # Assert db instance updated


def test_patch_update_customer_name(
    db_session: scoped_session[Session],
    client: FlaskClient,
    customer_instance: Customer,
) -> None:
    """Test CRUD integration by asserting name instance is updated in database through customer
    using a fake PUT request using the test client."""

    customer_id = customer_instance.id  # Assign customer id based on instance id
    new_data = {"name": {"first_name": "Julius", "last_name": "Randle"}}
    # Simulate Patch request and pass new data
    response = client.patch(f"/customers/{customer_id}", json=new_data)

    assert response.status_code == 200  # Assert successful request
    assert response.json["name"]["first_name"] == "Julius"  # Check value in response
    db_session.refresh(customer_instance)  # Refresh db
    assert customer_instance.name.first_name == "Julius"  # Assert db instance updated


def test_put_update_customer(
    db_session: scoped_session[Session],
    client: FlaskClient,
    customer_instance: Customer,
    address_instance: Address,
) -> None:
    """Test CRUD integration by asserting customer  and name instance is updated in database
    using a fake PUT request using the test client."""

    customer_id = customer_instance.id  # Assign customer id based on instance id
    new_data = {
        "email": "juliusrandle@example.com",
        "phone": "+61421404292",
        "address_id": address_instance.id,
        "name": {"first_name": "Julius", "last_name": "Randle"},
    }
    response = client.put(f"/customers/{customer_id}", json=new_data)  # Simulate Patch

    assert response.status_code == 200  # Assert successful request
    assert response.json["email"] == "juliusrandle@example.com"  # Check response value
    db_session.refresh(customer_instance)  # Refresh db
    assert customer_instance.phone == "+61421404292"  # Assert db instance updated
    assert customer_instance.name.first_name == "Julius"  # Assert nested name updated


def test_delete_customer(
    db_session: scoped_session[Session],
    client: FlaskClient,
    customer_instance: Customer,
) -> None:
    """Test CRUD integration by asserting customer and name instance is deleted in database
    using a fake DELETE request using the test client."""

    cust_id = customer_instance.id  # Assign customer id based on id of instance in db
    name_id = customer_instance.name_id  # Assign name id based on id of instance in db
    response = client.delete(f"/customers/{cust_id}")  # Simulate DELETE request
    assert response.status_code == 200  # Assert successful deletion
    assert db_session.get(Customer, cust_id) is None  # Check Customer instance deleted
    assert db_session.get(Name, name_id) is None  # Check Name instance deleted


def test_bad_json_create_customer(client: FlaskClient) -> None:
    """Test CRUD exception handling by creating a new customer from
    an invalid json POST request using the test client."""

    resp = client.post("/customers")  # Missing json request
    assert resp.status_code == 404  # Expected error


def test_missing_field_create_customer(
    client: FlaskClient, customer_json: dict
) -> None:
    """Test CRUD exception handling by updating an customer from
    an invalid POST request with missing field using the test client."""

    customer_json.pop("email")  # Remove email field from json
    response = client.post("/customers", json=customer_json)  # Attempt invalid POST

    assert response.status_code == 400

    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_invalid_field_create_customer(
    client: FlaskClient, customer_json: dict
) -> None:
    """Test CRUD exception handling by updating an customer from
    an invalid POST request with invalid data using the test client."""

    customer_json["email"] = "1"  # Invalid value
    response = client.post("/customers", json=customer_json)  # Attempt invalid POST

    assert response.status_code == 400  # Expected error
    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_get_invalid_customer(client: FlaskClient) -> None:
    """Test CRUD exception handling by fetching an customer from
    a GET request with invalid customer_id using the test client."""

    response = client.get("/customers/999")  # Attempt invalid customer_id

    assert response.status_code == 404  # Expected Error
    body = response.get_json()  # Retrieve error response
    assert "not found" in body["message"]  # Check for correct response


# Test database level validation
# ==================================================================================================


@pytest.mark.parametrize(
    "field, value",
    [
        ("email", None),
        ("name_id", None),
    ],
)
def test_customer_database_not_null(
    db_session: scoped_session[Session],
    customer_json: dict[str, str],
    field: CustomerFields,
    value: None,
) -> None:
    """
    Use an insert statement to bypass model validation and insert NULL value into a NOT NULL
    enforced column in the database, raising IntegrityError
    """

    data = customer_json.copy()
    del data["name"]  # Remove nested name values
    data[field] = value  # Replace each fields value with None per iteration
    # Create SQL insert statement, bypassing model validation
    stmt = insert(Customer).values(data)

    with pytest.raises(IntegrityError):  # Expected error
        db_session.execute(stmt)  # Error should trigger on execute, commit not required


# Relationship handling for customers tested in test_addresses, test_names and test_orders
# ==================================================================================================
