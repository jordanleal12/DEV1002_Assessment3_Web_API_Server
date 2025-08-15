"""Create pytest fixtures that set up flask application, database, and test client,
passing the output of the functions to the test functions as reusable components."""

import sys  # Used to add src to path directory python can access
import os  # Used to convert relative path to src to absolute path
import pytest  # Used for pytest fixtures

sys.path.insert(  # Allows imports from src folder
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
# Below absolute path declaration so imports happen using new path
from main import create_app  # Used to setup app instance with test configuration
from extensions import db  # To link SQLAlchemy
from models import Address  # Used for pre-filled address instance fixture


@pytest.fixture(scope="function")  # scope='function' ensures fixture is created once
# per function instead of per module (file) so each test uses fresh db
def app():
    """Create a Flask application for testing, using the test configuration
    (TestConfig) defined in config.py (sqlite in-memory database)."""

    app = create_app("config.TestConfig")  # Using TestConfig to setup app with sqlite
    with app.app_context():
        db.create_all()  # Creates all tables in the in-memory database
    yield app  # Passes the app instance to the test functions
    with app.app_context():
        db.drop_all()  # Drops all tables after tests are done


@pytest.fixture
def client(app):
    """Create a test HTTP client for the Flask application, similar to insomnia,
    capable of making HTTP requests and process responses without running the server."""

    return app.test_client()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""

    with app.app_context():
        yield db.session  # Passes the database session to test functions
        db.session.rollback()  # Undo any changes to the database after each test


# Pytest fixtures to pass pre-filled model instance or dictionary instance to tests
# ==================================================================================================


@pytest.fixture
def address_instance(db_session):
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
def address_json():
    """Create dictionary for address that can be passed to tests."""

    address_dict = {  # Pre-filled address dictionary
        "country_code": "US",
        "state_code": "CA",
        "city": "San Francisco",
        "street": "123 Test St",
        "postcode": "12345",
    }
    return address_dict
