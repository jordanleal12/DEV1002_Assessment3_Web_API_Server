"""Test cases for Order model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask.testing import FlaskClient
from sqlalchemy import insert  # Used for type hints
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session  # Raised when validation fails on schema
from conftest import OrderFields  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from models import Order, OrderItem, Customer, Book  # Used for model validation

from schemas import order_schema  # Used for schema tests


# Test model level validation
# ==================================================================================================


def test_order_creation(
    db_session: scoped_session[Session],
    customer_instance: Customer,
    book_instance: Book,
) -> None:
    """Test the model by creating a new order instance."""

    # Create order instance using Order model
    order = Order(
        customer_id=customer_instance.id,
        price_total=24.99,
    )

    order_item = OrderItem(book_id=book_instance.id, quantity=1)
    order.order_items.append(order_item)  # Associate order_item with order

    db_session.add(order)  # Adds order to db fixture session from conftest.py
    db_session.commit()

    assert order.id is not None  # Test order instance has been created in database
    assert db_session.get(Order, 1).customer_id == customer_instance.id  # Check values
    assert order.order_items[0].book.title == book_instance.title  # Check relationship


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("customer_id", None),
        ("customer_id", ""),
        ("customer_id", "  "),  # Whitespace only should fail
        ("price_total", None),
        ("price_total", ""),
        ("price_total", "   "),  # Whitespace only should fail
    ],
)
def test_order_model_required_fields(
    field: OrderFields, value: str | None, order_instance: Order
) -> None:
    """Test that required fields are enforced in the Order model."""

    # order_instance is a pytest fixture containing a pre-made order instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(order_instance, field, value)  # Replace order_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("customer_id", "1"),  # Numeric characters only
        ("customer_id", -1),  # Positive int only
        ("price_total", -1.0),  # Positive float only
        ("price_total", "1.0"),  # Float only
    ],
)
def test_order_model_valid_char(
    field: OrderFields, value: str | int, order_instance: Order
) -> None:
    """Test that invalid character/type is enforced by model."""

    # order_instance is a pytest fixture containing a pre-made order instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(order_instance, field, value)  # Replace order_instance fields with
        # invalid data per each iteration


# # Test schema level validation
# # ==================================================================================================


def test_order_schema_load(
    order_json: dict[str, str], customer_instance: Customer, book_instance: Book
) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = order_schema.load(order_json)  # Load json into dictionary
    assert data["customer_id"] == customer_instance.id  # Check expected data in field
    # Check nesting
    assert data["order_items"][0]["book_id"] == book_instance.id


def test_order_schema_dump(order_instance: Order, customer_instance: Customer) -> None:
    """Test serialization of python object into json data using schema."""

    data = order_schema.dump(order_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["customer_id"] == customer_instance.id  # Check expected data in field
    # Check nesting
    assert data["order_items"][0]["book"]["title"] == "The Name Of The Wind"


# Ensures only required keys are deleted in below test
REQUIRED_KEYS = [
    "customer_id",
    "price_total",
]


def test_order_missing_schema_key(order_json: dict[str, str]) -> None:
    """Test deserialization while missing one key: value pair per iteration."""

    for key in REQUIRED_KEYS:  # Iterates once per key
        data = order_json.copy()  # Create fresh copy to not effect order_json
        del data[key]  # Delete subsequent key per iteration

        with pytest.raises(ValidationError):  # Check error is raised per missing key
            order_schema.load(data)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("customer_id", None),
        ("customer_id", ""),
        ("customer_id", "  "),  # Whitespace should be stripped
        ("price_total", None),
    ],
)
def test_order_schema_required_fields(
    order_json: dict[str, str], field: OrderFields, value: None | str
) -> None:
    """Test schema enforces Null and empty string values for required fields."""

    data = order_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        order_schema.load(order_json)


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("customer_id", -1),  # Positive int only
        ("price_total", -1),  # Positive float only
        ("price_total", 10000.99),  # Max 6 digits
    ],
)
def test_order_schema_valid_char(
    order_json: dict[str, str], field: OrderFields, value: str | int
) -> None:
    """Test that invalid character/type is enforced by schema."""

    data = order_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        order_schema.load(order_json)


# Test integration/routes
# ==================================================================================================


def test_create_order(
    client: FlaskClient,
    order_json: dict[str, str],
    customer_instance: Customer,
    book_instance: Book,
) -> None:
    """Test CRUD integration by creating a new order from
    a fake json POST request using the test client."""

    response = client.post(  # Retrieve fake json data from Flask test client
        "/orders",
        json=order_json,  # A fixture that returns a dict containing order fields
    )
    print(response.get_data(as_text=True))
    assert response.status_code == 201  # Response for successful creation
    assert response.json["customer_id"] == customer_instance.id  # Check response
    # Assert nesting matches expected response
    assert response.json["order_items"][0]["book_id"] == book_instance.id


def test_get_order(
    client: FlaskClient,
    order_instance: Order,
    customer_instance: Customer,
    book_instance: Book,
) -> None:
    """Test CRUD integration by asserting order instance is in database
    using a fake GET request using the test client."""

    order_id = order_instance.id  # Assign order id based on id of instance in db
    response = client.get(f"/orders/{order_id}")  # Simulate get request using client
    assert response.status_code == 200  # Assert successful request
    assert response.json["customer_id"] == customer_instance.id  # Check response
    # Assert nesting matches expected response
    assert response.json["order_items"][0]["book_id"] == book_instance.id


def test_get_orders(
    db_session: scoped_session[Session],
    client: FlaskClient,
    order_instance: Order,
    order2_instance: Order,
) -> None:
    """Test CRUD integration by asserting multiple order instances are in database
    using a fake GET request using the test client."""

    response = client.get("/orders")  # Simulate GET request for all orders
    assert response.status_code == 200  # Assert successful request
    assert len(response.json) == 2  # Assert expected number of order instances


def test_patch_update_order(
    db_session: scoped_session[Session],
    client: FlaskClient,
    order_instance: Order,
    book_instance: Book,
    book2_instance: Book,
) -> None:
    """Test CRUD integration by asserting order instance is updated in database
    using a fake PUT request using the test client."""

    order_id = order_instance.id  # Assign order id based on id of instance in db
    new_data = {
        "order_items": [
            {"book_id": book_instance.id, "quantity": 3},  # Update quantity for book1
            {"book_id": book2_instance.id, "quantity": 2},  # Update quantity for book2
        ]
    }
    response = client.patch(f"/orders/{order_id}", json=new_data)  # Simulate Patch

    expected_price = float(3 * book_instance.price + 2 * book2_instance.price)
    db_session.refresh(order_instance)  # Refresh db
    assert response.status_code == 200  # Assert successful request
    assert response.json["order_items"][0]["book_id"] == book_instance.id
    assert response.json["price_total"] == expected_price  # Check price total


def test_put_update_order(
    db_session: scoped_session[Session],
    client: FlaskClient,
    order_instance: Order,
    book2_instance: Book,
) -> None:
    """Test CRUD integration by asserting order instance is updated in database
    using a fake PUT request using the test client."""

    order_id = order_instance.id  # Assign order id based on id of instance in db

    new_data = {
        "customer_id": order_instance.customer_id,  # Include the customer_id
        "order_items": [
            {"book_id": book2_instance.id, "quantity": 5},  # Only one book now
        ],
        "price_total": float(0),
    }

    response = client.put(f"/orders/{order_id}", json=new_data)  # Simulate Patch

    db_session.refresh(order_instance)  # Refresh db
    assert response.status_code == 200  # Assert successful request
    assert len(order_instance.order_items) == 1  # Check missing order instance deleted
    assert order_instance.order_items[0].book_id == book2_instance.id
    assert order_instance.price_total == 5 * book2_instance.price


def test_delete_order(
    db_session: scoped_session[Session], client: FlaskClient, order_instance: Order
) -> None:
    """Test CRUD integration by asserting order instance is deleted in database
    using a fake DELETE request using the test client."""

    order_id = order_instance.id  # Assign order id based on id of instance in db
    book_ids = [
        book.id for book in order_instance.books
    ]  # Store order_items for later check

    response = client.delete(f"/orders/{order_id}")  # Simulate DELETE request
    assert response.status_code == 200  # Assert successful deletion
    assert db_session.get(Order, order_id) is None  # Check Order instance deleted
    for book_id in book_ids:  # Check order_items deleted
        assert db_session.get(OrderItem, (order_id, book_id)) is None


def test_bad_json_create_order(client: FlaskClient) -> None:
    """Test CRUD exception handling by creating a new order from
    an invalid json POST request using the test client."""

    resp = client.post("/orders")  # Missing json request
    assert resp.status_code == 400  # Expected error


def test_missing_field_create_order(client: FlaskClient, order_json: dict) -> None:
    """Test CRUD exception handling by updating an order from
    an invalid POST request with missing field using the test client."""

    order_json.pop("customer_id")  # Remove isbn field from json
    response = client.post("/orders", json=order_json)  # Attempt invalid POST

    assert response.status_code == 400

    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_invalid_field_create_order(client: FlaskClient, order_json: dict) -> None:
    """Test CRUD exception handling by updating an order from
    an invalid POST request with invalid data using the test client."""

    order_json["price_total"] = "fifty"  # Invalid value
    response = client.post("/orders", json=order_json)  # Attempt invalid POST

    assert response.status_code == 400  # Expected error
    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_get_invalid_order(client: FlaskClient) -> None:
    """Test CRUD exception handling by fetching an order from
    a GET request with invalid order_id using the test client."""

    response = client.get("/orders/999")  # Attempt invalid order_id

    assert response.status_code == 404  # Expected Error
    body = response.get_json()  # Retrieve error response
    assert "not found" in body["message"]  # Check for correct response


# Test database level validation
# ==================================================================================================


@pytest.mark.parametrize(
    "field, value",
    [
        ("customer_id", None),
        ("order_date", None),
        ("price_total", None),
    ],
)
def test_order_database_not_null(
    db_session: scoped_session[Session],
    order_json: dict[str, str],
    field: OrderFields,
    value: None,
) -> None:
    """
    Use an insert statement to bypass model validation and insert NULL value into a NOT NULL
    enforced column in the database, raising IntegrityError
    """

    data = order_json
    del data["order_items"]  # Nested authors cannot be passed to database directly
    data[field] = value  # Replace each fields value with None per iteration
    # Create SQL insert statement, bypassing model validation
    stmt = insert(Order).values(data)

    with pytest.raises(IntegrityError):  # Expected error
        db_session.execute(stmt)  # Error should trigger on execute, commit not required


# Test relationship handling
# ==================================================================================================


def test_delete_order_author_nulls_author_fk(
    db_session: scoped_session[Session],
    order_instance: Order,
) -> None:
    """Test Order relationship with order_items, check deleting all order_items deletes order."""

    order_id = order_instance.id  # Store order id before delete
    book_ids = [book.id for book in order_instance.books]

    for order_item in order_instance.order_items:
        db_session.delete(order_item)  # Delete all order_items

    db_session.commit()

    for book_id in book_ids:  # Check order_items deleted
        assert db_session.get(OrderItem, (order_id, book_id)) is None
    assert db_session.get(Order, order_id) is None  # Check order instance deleted
