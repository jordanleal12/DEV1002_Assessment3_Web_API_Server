"""Create pytest fixtures that set up flask application, database, and test client,
passing the output of the functions to the test functions as reusable components."""

import sys  # Used to add src to path directory python can access
import os  # Used to convert relative path to src to absolute path
from typing import Any, Generator, Literal  # Used for type hints
from flask import Flask  # Used for type hints
from flask.testing import FlaskClient  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Used for pytest fixtures
from sqlalchemy.orm import scoped_session  # Used for type alias for field names

sys.path.insert(  # Allows imports from src folder
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
# Below absolute path declaration so imports happen using new path
from main import create_app  # Used to setup app instance with test configuration
from extensions import db  # To link SQLAlchemy
from models import Address, Customer, Name  # Used for pre-filled instance fixture


@pytest.fixture(scope="function")  # scope='function' ensures fixture is created once
# per function instead of per module (file) so each test uses fresh db
def app() -> Generator[Flask, Any, None]:
    """Create a Flask application for testing, using the test configuration
    (TestConfig) defined in config.py (sqlite in-memory database)."""

    app = create_app("config.TestConfig")  # Using TestConfig to setup app with sqlite
    with app.app_context():
        db.create_all()  # Creates all tables in the in-memory database
    yield app  # Passes the app instance to the test functions
    with app.app_context():
        db.drop_all()  # Drops all tables after tests are done


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test HTTP client for the Flask application, similar to insomnia,
    capable of making HTTP requests and process responses without running the server."""

    return app.test_client()


@pytest.fixture
def db_session(app: Flask) -> Generator[scoped_session[Session], Any, None]:
    """Create a database session for testing."""

    with app.app_context():
        yield db.session  # Passes the database session to test functions
        db.session.rollback()  # Undo any changes to the database after each test


# Pytest Address fixtures to pass pre-filled address instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def address_instance(db_session: scoped_session[Session]) -> Address:
    """Create instance of address as a fixture that can be passed to tests."""

    address = Address(  # Pre-filled address instance
        country_code="US",
        state_code="CA",
        city="San Francisco",
        street="123 Test St",
        postcode="12345",
    )
    db_session.add(address)
    db_session.commit()
    return address


@pytest.fixture
def address_json() -> dict[str, str]:
    """Create dictionary for address that can be passed to tests."""

    address_dict = {  # Pre-filled address dictionary
        "country_code": "US",
        "state_code": "CA",
        "city": "San Francisco",
        "street": "123 Test St",
        "postcode": "12345",
    }
    return address_dict


AddressFields = Literal["country_code", "state_code", "city", "street", "postcode"]


# Pytest Name fixtures to pass pre-filled name instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def name_instance(db_session: scoped_session[Session]) -> Name:
    """Create instance of address as a fixture that can be passed to tests."""

    name = Name(  # Pre-filled address instance
        first_name="John",
        last_name="Smith",
    )
    db_session.add(name)
    db_session.commit()
    return name


@pytest.fixture
def name2_instance(db_session: scoped_session[Session]) -> Name:
    """Create instance of address as a fixture that can be passed to tests."""

    name2 = Name(  # Pre-filled address instance
        first_name="Jack",
        last_name="Sparrow",
    )
    db_session.add(name2)
    db_session.commit()
    return name2


@pytest.fixture
def name_json() -> dict[str, str]:
    """Create dictionary for address that can be passed to tests."""

    name_dict = {  # Pre-filled address dictionary
        "first_name": "John",
        "last_name": "Smith",
    }
    return name_dict


NameFields = Literal["first_name", "last_name"]

# Pytest Customer fixtures to pass pre-filled customer instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def customer_instance(
    db_session: scoped_session[Session], address_instance: Address, name_instance: Name
) -> Customer:
    """Create instance of address as a fixture that can be passed to tests."""

    customer = Customer(
        email="johnsmith@email.com",
        phone="+61412345678",
        address_id=address_instance.id,
        name_id=name_instance.id,
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def customer2_instance(
    db_session: scoped_session[Session], address_instance: Address, name2_instance: Name
) -> Customer:
    """Create instance of address as a fixture that can be passed to tests."""

    customer2 = Customer(
        name_id=name2_instance.id,
        email="jacksparrow@email.com",
        phone="+61487654321",
        address_id=address_instance.id,
    )
    db_session.add(customer2)
    db_session.commit()
    return customer2


@pytest.fixture
def customer_json(
    db_session: scoped_session[Session], address_instance: Address
) -> dict[str, str]:
    """Create dictionary for address that can be passed to tests."""

    customer_dict = {  # Pre-filled address dictionary
        "email": "johnsmith@email.com",
        "phone": "+61412345678",
        "address_id": address_instance.id,
        "name": {"first_name": "John", "last_name": "Smith"},
    }
    return customer_dict


CustomerFields = Literal["name", "email", "phone", "address_id"]
