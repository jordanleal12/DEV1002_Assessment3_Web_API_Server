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
from models import Address, BookAuthor, Customer, Name, Author, Book, Order, OrderItem


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
    """Create instance of name as a fixture that can be passed to tests."""

    name = Name(  # Pre-filled address instance
        first_name="John",
        last_name="Smith",
    )
    db_session.add(name)
    db_session.commit()
    return name


@pytest.fixture
def name2_instance(db_session: scoped_session[Session]) -> Name:
    """Create instance of name as a fixture that can be passed to tests."""

    name2 = Name(  # Pre-filled address instance
        first_name="Patrick",
        last_name="Rothfus",
    )
    db_session.add(name2)
    db_session.commit()
    return name2


@pytest.fixture
def name_json() -> dict[str, str]:
    """Create dictionary for name that can be passed to tests."""

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
    """Create instance of customer as a fixture that can be passed to tests."""

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
    """Create instance of customer as a fixture that can be passed to tests."""

    customer2 = Customer(
        name_id=name2_instance.id,
        email="patrickrothfus@email.com",
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
    """Create dictionary for customer that can be passed to tests."""

    customer_dict = {  # Pre-filled address dictionary
        "email": "johnsmith@email.com",
        "phone": "+61412345678",
        "address_id": address_instance.id,
        "name": {"first_name": "John", "last_name": "Smith"},
    }
    return customer_dict


CustomerFields = Literal["name", "email", "phone", "address_id"]

# Pytest Author fixtures to pass pre-filled author instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def author_instance(db_session: scoped_session[Session], name_instance: Name) -> Author:
    """Create instance of author as a fixture that can be passed to tests."""

    author = Author(name_id=name_instance.id)
    db_session.add(author)
    db_session.commit()
    return author


@pytest.fixture
def author2_instance(
    db_session: scoped_session[Session], name2_instance: Name
) -> Author:
    """Create instance of author as a fixture that can be passed to tests."""

    author2 = Author(name_id=name2_instance.id)
    db_session.add(author2)
    db_session.commit()
    return author2


@pytest.fixture
def author_json() -> dict[str, str]:
    """Create dictionary for author that can be passed to tests."""

    author_dict = {  # Pre-filled author dictionary
        "name": {"first_name": "John", "last_name": "Smith"},
    }
    return author_dict


AuthorFields = Literal["name"]


# Pytest Book fixtures to pass pre-filled book instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def book_instance(
    db_session: scoped_session[Session], author2_instance: Author
) -> Book:
    """Create instance of book as a fixture that can be passed to tests."""

    book = Book(
        isbn="9780756404079",
        title="The Name Of The Wind",
        series="The Kingkiller Chronicles",
        publication_year=2007,
        discontinued=False,
        price=24.99,
        quantity=23,
    )
    db_session.add(book)
    db_session.flush()  # Flush to commit book id
    # Link author to book through book_authors
    book_author = BookAuthor(book_id=book.id, author_id=author2_instance.id)

    db_session.add(book_author)
    db_session.commit()
    return book


@pytest.fixture
def book2_instance(db_session: scoped_session[Session]) -> Book:
    """Create instance of book as a fixture that can be passed to tests."""

    book2 = Book(
        isbn="9780060853976",
        title="Good Omens",
        series="The Nice and Accurate Prophecies of Agnes Nutter, Witch",
        publication_year=1990,
        discontinued=False,
        price=19.99,
        quantity=18,
    )
    db_session.add(book2)
    db_session.flush()

    name = Name(first_name="Terry", last_name="Pratchett")
    name2 = Name(first_name="Neil", last_name="Gaiman")
    db_session.add_all([name, name2])
    db_session.flush()

    author = Author(name_id=name.id)
    author2 = Author(name_id=name2.id)
    db_session.add_all([author, author2])
    db_session.flush()

    book_author = BookAuthor(book_id=book2.id, author_id=author.id)
    book_author2 = BookAuthor(book_id=book2.id, author_id=author2.id)
    db_session.add_all([book_author, book_author2])

    db_session.commit()
    return book2


@pytest.fixture
def book_json(db_session: scoped_session[Session]) -> dict[str, str]:
    """Create dictionary for book that can be passed to tests."""

    book_dict = {
        "isbn": "9780756404079",
        "title": "The Name Of The Wind",
        "series": "The Kingkiller Chronicles",
        "publication_year": 2007,
        "discontinued": False,
        "price": 24.99,
        "quantity": 23,
        "authors": [{"name": {"first_name": "Patrick", "last_name": "Rothfuss"}}],
    }
    return book_dict


@pytest.fixture
def book_json2(db_session: scoped_session[Session]) -> dict[str, str]:
    """Create dictionary for book that can be passed to tests."""

    book_dict = {  # Pre-filled address dictionary
        "isbn": "9780060853976",
        "title": "Good Omens",
        "series": "The Nice and Accurate Prophecies of Agnes Nutter, Witch",
        "publication_year": 1990,
        "discontinued": False,
        "price": 19.99,
        "quantity": 18,
        "authors": [
            {"name": {"first_name": "Terry", "last_name": "Pratchet"}},
            {"name": {"first_name": "Neil", "last_name": "Gaiman"}},
        ],
    }
    return book_dict


BookFields = Literal[
    "isbn", "title", "series", "publication_year", "discontinued", "price", "quantity"
]

# Pytest Order fixtures to pass pre-filled order instance or dictionary to tests
# ==================================================================================================


@pytest.fixture
def order_instance(
    db_session: scoped_session[Session],
    customer_instance: Customer,
    book_instance: Book,
    book2_instance: Book,
) -> Order:
    """Create instance of order as a fixture that can be passed to tests."""

    order = Order(
        customer_id=customer_instance.id,
        price_total=1.0,  # Update after creating order_items
    )

    db_session.add(order)
    db_session.flush()  # Flush to commit order id

    order_item1 = OrderItem(book_id=book_instance.id, order_id=order.id, quantity=1)
    order_item2 = OrderItem(book_id=book2_instance.id, order_id=order.id, quantity=2)
    db_session.add_all([order_item1, order_item2])

    # Calculate correct price total
    total = float(
        order_item1.quantity * book_instance.price
        + order_item2.quantity * book2_instance.price
    )
    order.price_total = total  # Update price total to correct value

    db_session.commit()
    return order


@pytest.fixture
def order2_instance(
    db_session: scoped_session[Session],
    customer2_instance: Customer,
    book_instance: Book,
) -> Order:
    """Create instance of order as a fixture that can be passed to tests."""

    order = Order(
        customer_id=customer2_instance.id,
        price_total=1.0,  # Update after creating order_items
    )

    db_session.add(order)
    db_session.flush()  # Flush to commit order id

    order_item = OrderItem(book_id=book_instance.id, order_id=order.id, quantity=3)
    db_session.add(order_item)

    # Calculate correct price total
    total = float(order_item.quantity * book_instance.price)

    order.price_total = total  # Update price total to correct value

    db_session.commit()
    return order


@pytest.fixture
def order_json(
    db_session: scoped_session[Session],
    customer_instance: Customer,
    book_instance: Book,
    book2_instance: Book,
) -> dict[str, str]:
    """Create dictionary for order that can be passed to tests."""

    order_dict = {
        "customer_id": customer_instance.id,
        "order_items": [
            {"book_id": book_instance.id, "quantity": 1},
            {"book_id": book2_instance.id, "quantity": 2},
        ],
        "price_total": float((1 * book_instance.price) + (2 * book2_instance.price)),
    }
    return order_dict


@pytest.fixture
def order_json2(
    db_session: scoped_session[Session],
    customer2_instance: Customer,
    book_instance: Book,
) -> dict[str, str]:
    """Create dictionary for order that can be passed to tests."""

    order_dict = {
        "customer_id": customer2_instance.id,
        "order_items": [
            {"book_id": book_instance.id, "quantity": 3},
        ],
        "price_total": float(3 * book_instance.price),
    }
    return order_dict


OrderFields = Literal["customer_id", "order_items", "price_total"]
