"""Test cases for Book model, schema, and CRUD operations.
Using TDD, we will implement the tests first and then the corresponding code."""

from flask.testing import FlaskClient
from sqlalchemy import insert  # Used for type hints
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session  # Raised when validation fails on schema
from conftest import BookFields  # Used for type hints
from flask_sqlalchemy.session import Session  # Used for type hints
import pytest  # Required for @parametrize decorator
from marshmallow import ValidationError  # Expected schema validation error
from models import Book, BookAuthor, Customer, Author  # Used for model validation
from schemas import book_schema  # Used for schema tests


# Test model level validation
# ==================================================================================================


def test_book_creation(db_session: scoped_session[Session]) -> None:
    """Test the model by creating a new book instance."""

    # Create book instance using Book model
    book = Book(
        isbn="9780756404079",
        title="The Name Of The Wind",
        series="The Kingkiller Chronicles",
        publication_year=2007,
        discontinued=False,
        price=24.99,
        quantity=23,
    )

    db_session.add(book)  # Adds book to db fixture session from conftest.py
    db_session.commit()

    assert book.id is not None  # Test book instance has been created in database
    assert db_session.get(Book, 1).isbn == "9780756404079"  # Check values in db


# @parametrize decorator runs the test for each set of parameters provided as a list of tuples
# Validation check in model gives ValueError when value is None or empty string
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", None),
        ("isbn", ""),
        ("isbn", "  "),  # Whitespace only should fail
        ("title", None),
        ("title", ""),
        ("title", "   "),  # Whitespace only should fail
        ("publication_year", None),
        ("publication_year", ""),
        ("publication_year", "     "),  # Whitespace only should fail
        ("discontinued", None),
        ("discontinued", ""),
        ("discontinued", "    "),  # Whitespace only should fail
        ("price", None),
        ("price", ""),
        ("price", "  "),  # Whitespace only should fail
        ("quantity", None),
        ("quantity", ""),
        ("quantity", "  "),  # Whitespace only should fail
    ],
)
def test_book_model_required_fields(
    field: BookFields, value: str | None, book_instance: Book
) -> None:
    """Test that required fields are enforced in the Book model."""

    # book_instance is a pytest fixture containing a pre-made book instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(book_instance, field, value)  # Replace book_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", "123456"),  # Under min length (10)
        ("isbn", "12345678910123"),  # Exceeds max length (13)
        ("title", ("a" * 256)),  # Exceeds max length (255)
        ("series", ("a" * 256)),  # Exceeds max length (255)
    ],
)
def test_book_model_column_length(
    field: BookFields, value: str, book_instance: Book
) -> None:
    """Test that max column character length is enforced by model."""

    # book_instance is a pytest fixture containing a pre-made book instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(book_instance, field, value)  # Replace book_instance fields with
        # invalid data per each iteration


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", "qwertyuiop"),  # Numeric characters only
        ("isbn", 1234567890),  # String only
        ("title", 123),  # String only
        ("title", ["Name of", "The Wind"]),  # String only
        ("title", {"Name of": "The Wind"}),  # String only
        ("series", 123),  # String only
        ("series", ["Name of", "The Wind"]),  # String only
        ("series", {"Name of": "The Wind"}),  # String only
        ("publication_year", "2007"),  # Integer only
        ("publication_year", 2007.55),  # Integer only
        ("publication_year", 999),  # Must exceed 1000
        ("publication_year", 2099),  # Cant exceed current year
        ("discontinued", "True"),  # Bool only
        ("discontinued", 1),  # Bool only
        ("price", "24.99"),  # Float only
        ("price", 24),  # Float only
        ("price", (-24.99)),  # Positive float only
        ("price", 1111.11),  # Cannot exceed 5 digits
        ("quantity", "1"),  # Integer only
        ("quantity", 1.5),  # Integer only
        ("quantity", -1),  # Positive integer only
    ],
)
def test_book_model_valid_char(
    field: BookFields, value: str | int, book_instance: Book
) -> None:
    """Test that invalid character/type is enforced by model."""

    # book_instance is a pytest fixture containing a pre-made book instance
    with pytest.raises(ValueError):  # Checks error is raised with wrong input
        setattr(book_instance, field, value)  # Replace book_instance fields with
        # invalid data per each iteration


# Test schema level validation
# ==================================================================================================


def test_book_schema_load(book_json: dict[str, str]) -> None:
    """
    Test conversion of json data into python dict using schema.
    'load_instance=False' is set in schema, so data will not be deserialized.
    """

    data = book_schema.load(book_json)  # Load json into dictionary
    assert data["isbn"] == "9780756404079"  # Check expected data in field
    assert data["authors"][0]["name"]["first_name"] == "Patrick"  # Check nesting


def test_book_schema_dump(book_instance: Book) -> None:
    """Test serialization of python object into json data using schema."""

    data = book_schema.dump(book_instance)  # Serialize object into dictionary

    assert isinstance(data, dict)  # Check object was converted to dictionary
    assert data["isbn"] == "9780756404079"  # Check dict key has expected value
    assert data["authors"][0]["name"]["first_name"] == "Patrick"  # Check nesting


# Ensures only required keys are deleted in below test
REQUIRED_KEYS = [
    "isbn",
    "title",
    "publication_year",
    "discontinued",
    "price",
    "quantity",
]


def test_book_missing_schema_key(book_json: dict[str, str]) -> None:
    """Test deserialization while missing one key: value pair per iteration."""

    for key in REQUIRED_KEYS:  # Iterates once per key
        data = book_json.copy()  # Create fresh copy to not effect book_json
        del data[key]  # Delete subsequent key per iteration

        with pytest.raises(ValidationError):  # Check error is raised per missing key
            book_schema.load(data)


# Allow iteration of test cases, replacing each value with None or empty string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", None),
        ("isbn", ""),
        ("isbn", "  "),  # Whitespace should be stripped
        ("title", None),
        ("title", ""),
        ("title", "   "),  # Whitespace should be stripped
        ("publication_year", None),
        ("publication_year", ""),
        ("publication_year", "    "),  # Whitespace should be stripped
        ("discontinued", None),
        ("discontinued", ""),
        ("discontinued", "    "),  # Whitespace should be stripped
        ("price", None),
        ("price", ""),
        ("price", "    "),  # Whitespace should be stripped
        ("quantity", None),
        ("quantity", ""),
        ("quantity", "    "),  # Whitespace should be stripped
        ("authors", None),
        ("authors", ""),
        ("authors", "    "),  # Whitespace should be stripped
    ],
)
def test_book_schema_required_fields(
    book_json: dict[str, str], field: BookFields, value: None | str
) -> None:
    """Test schema enforces Null and empty string values for required fields."""

    data = book_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        book_schema.load(book_json)


# Allow iteration of test cases, replacing each value with invalid length string per test
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", "12345678910234"),  # Exceeds max length (13)
        ("isbn", "123456789"),  # Under min length (9)
        ("title", ("a" * 256)),  # Exceeds max length (255)
        ("series", ("a" * 256)),  # Exceeds max length (255)
    ],
)
def test_book_schema_column_length(
    book_json: dict[str, str], field: BookFields, value: str
) -> None:
    """Test schema enforces min and max column length."""

    data = book_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        book_schema.load(book_json)


# Create parametrize decorated function to allow iteration of test cases
@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", "qwertyuiop"),  # Numeric characters only
        ("isbn", 1234567890),  # String only
        ("title", 123),  # String only
        ("title", ["Name of", "The Wind"]),  # String only
        ("title", {"Name of": "The Wind"}),  # String only
        ("series", 123),  # String only
        ("series", ["Name of", "The Wind"]),  # String only
        ("series", {"Name of": "The Wind"}),  # String only
        ("publication_year", 2007.55),  # Integer only
        ("publication_year", 999),  # Must exceed 1000
        ("publication_year", 2099),  # Cant exceed current year
        ("discontinued", 1),  # Bool only
        ("price", (-24.99)),  # Positive float only
        ("price", 1111.11),  # Cannot exceed 5 digits
        ("quantity", "1"),  # Integer only
        ("quantity", 1.5),  # Integer only
        ("quantity", -1),  # Positive integer only
        ("authors", "Patrick Rothfus"),  # Dictionary only
    ],
)
def test_book_schema_valid_char(
    book_json: dict[str, str], field: BookFields, value: str | int
) -> None:
    """Test that invalid character/type is enforced by schema."""

    data = book_json  # Fresh dictionary for each iteration
    data[field] = value  # Replace each field with invalid data each iteration

    with pytest.raises(ValidationError):  # Schema should raise error for bad data
        book_schema.load(book_json)


# Test integration/routes
# ==================================================================================================


def test_create_book(client: FlaskClient, book_json: dict[str, str]) -> None:
    """Test CRUD integration by creating a new book from
    a fake json POST request using the test client."""

    response = client.post(  # Retrieve fake json data from Flask test client
        "/books",
        json=book_json,  # A fixture that returns a dict containing book fields
    )
    print(response.get_data(as_text=True))
    assert response.status_code == 201  # Response for successful creation
    assert response.json["isbn"] == "9780756404079"  # Check correct values in response
    # Assert nesting matches expected response
    assert response.json["authors"][0]["name"]["first_name"] == "Patrick"


def test_get_book(client: FlaskClient, book_instance: Book) -> None:
    """Test CRUD integration by asserting book instance is in database
    using a fake GET request using the test client."""

    book_id = book_instance.id  # Assign book id based on id of instance in db
    response = client.get(f"/books/{book_id}")  # Simulate get request using client
    assert response.status_code == 200  # Assert successful request
    assert response.json["isbn"] == "9780756404079"  # Assert expected value
    # Assert nesting matches expected response
    assert response.json["authors"][0]["name"]["first_name"] == "Patrick"


def test_get_books(
    db_session: scoped_session[Session],
    client: FlaskClient,
    book_instance: Book,
    book2_instance: Book,
) -> None:
    """Test CRUD integration by asserting multiple book instances are in database
    using a fake GET request using the test client."""

    response = client.get("/books")  # Simulate GET request for all books
    assert response.status_code == 200  # Assert successful request
    assert len(response.json) == 2  # Assert expected number of book instances


def test_patch_update_book(
    db_session: scoped_session[Session], client: FlaskClient, book_instance: Book
) -> None:
    """Test CRUD integration by asserting book instance is updated in database
    using a fake PUT request using the test client."""

    book_id = book_instance.id  # Assign book id based on id of instance in db
    new_data = {
        "isbn": "0756405890",
        "authors": [
            {"name": {"first_name": "Terry", "last_name": "Pratchet"}},
            {"name": {"first_name": "Neil", "last_name": "Gaiman"}},
        ],
    }
    response = client.patch(f"/books/{book_id}", json=new_data)  # Simulate Patch

    assert response.status_code == 200  # Assert successful request
    assert response.json["isbn"] == "0756405890"  # Assert new value in response
    assert response.json["authors"][0]["name"]["first_name"] == "Terry"
    assert response.json["authors"][1]["name"]["first_name"] == "Neil"
    db_session.refresh(book_instance)  # Refresh db
    assert book_instance.isbn == "0756405890"  # Assert db instance updated
    assert book_instance.authors[0].name.first_name == "Terry"


def test_put_update_book(
    db_session: scoped_session[Session],
    client: FlaskClient,
    book_instance: Book,
    book_json2: dict[str, str],
) -> None:
    """Test CRUD integration by asserting book instance is updated in database
    using a fake PUT request using the test client."""

    book_id = book_instance.id  # Assign book id based on id of instance in db
    response = client.put(f"/books/{book_id}", json=book_json2)  # Simulate Patch

    assert response.status_code == 200  # Assert successful request
    assert response.json["title"] == "Good Omens"  # Assert new value in response
    assert response.json["authors"][0]["name"]["first_name"] == "Terry"
    assert response.json["authors"][1]["name"]["first_name"] == "Neil"
    db_session.refresh(book_instance)  # Refresh db
    assert book_instance.title == "Good Omens"  # Assert db instance updated
    assert book_instance.authors[0].name.first_name == "Terry"


def test_delete_book(
    db_session: scoped_session[Session], client: FlaskClient, book_instance: Book
) -> None:
    """Test CRUD integration by asserting book instance is deleted in database
    using a fake DELETE request using the test client."""

    book_id = book_instance.id  # Assign book id based on id of instance in db
    author_id = book_instance.authors[0].id
    response = client.delete(f"/books/{book_id}")  # Simulate DELETE request
    assert response.status_code == 200  # Assert successful deletion
    assert db_session.get(Book, book_id) is None  # Check Book instance deleted
    assert db_session.get(Author, author_id) is None  # Check author deleted


def test_bad_json_create_book(client: FlaskClient) -> None:
    """Test CRUD exception handling by creating a new book from
    an invalid json POST request using the test client."""

    resp = client.post("/books")  # Missing json request
    assert resp.status_code == 400  # Expected error


def test_missing_field_create_book(client: FlaskClient, book_json: dict) -> None:
    """Test CRUD exception handling by updating an book from
    an invalid POST request with missing field using the test client."""

    book_json.pop("isbn")  # Remove isbn field from json
    response = client.post("/books", json=book_json)  # Attempt invalid POST

    assert response.status_code == 400

    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_invalid_field_create_book(client: FlaskClient, book_json: dict) -> None:
    """Test CRUD exception handling by updating an book from
    an invalid POST request with invalid data using the test client."""

    book_json["isbn"] = "1"  # Invalid value
    response = client.post("/books", json=book_json)  # Attempt invalid POST

    assert response.status_code == 400  # Expected error
    body = response.get_json()  # Retrieve error response
    assert body["error"] == "Schema Validation Failed"  # Check correct validation


def test_get_invalid_book(client: FlaskClient) -> None:
    """Test CRUD exception handling by fetching an book from
    a GET request with invalid book_id using the test client."""

    response = client.get("/books/999")  # Attempt invalid book_id

    assert response.status_code == 404  # Expected Error
    body = response.get_json()  # Retrieve error response
    assert "not found" in body["message"]  # Check for correct response


# Test database level validation
# ==================================================================================================


@pytest.mark.parametrize(
    "field, value",
    [
        ("isbn", None),
        ("title", None),
        ("publication_year", None),
        ("discontinued", None),
        ("price", None),
        ("quantity", None),
    ],
)
def test_book_database_not_null(
    db_session: scoped_session[Session],
    book_json: dict[str, str],
    field: BookFields,
    value: None,
) -> None:
    """
    Use an insert statement to bypass model validation and insert NULL value into a NOT NULL
    enforced column in the database, raising IntegrityError
    """

    data = book_json
    del data["authors"]  # Nested authors cannot be passed to database directly
    data[field] = value  # Replace each fields value with None per iteration
    # Create SQL insert statement, bypassing model validation
    stmt = insert(Book).values(data)

    with pytest.raises(IntegrityError):  # Expected error
        db_session.execute(stmt)  # Error should trigger on execute, commit not required


# Test relationship handling
# ==================================================================================================


def test_author_book_relationship(
    book_instance: Book, author2_instance: Author
) -> None:
    """Test that Book is correctly linked to Customer model,
    and that book data can be linked through the relationship."""

    book = book_instance  # Assign conftest.py book fixture to book
    author = author2_instance  # Assign conftest.py customer fixture to customer

    # Check that book can be accessed through author
    assert author.books[0].title == book_instance.title
    # Check that author can be accessed through book
    assert book.authors[0].name.first_name == author2_instance.name.first_name


def test_delete_book_author_nulls_author_fk(
    db_session: scoped_session[Session],
    book2_instance: Book,
) -> None:
    """
    Test Book relationship with customers, asserting deleting book instance sets customers
    book_id to Null and doesn't delete customer instance.
    """

    neil_book2 = Book(
        isbn="9780063070714",
        title="Stardust",
        publication_year=1998,
        price=17.99,
        quantity=9,
    )
    db_session.add(neil_book2)
    db_session.flush()

    book_author = BookAuthor(
        book_id=neil_book2.id, author_id=book2_instance.authors[0].id
    )
    db_session.add(book_author)
    db_session.commit()

    book_id = book2_instance.id  # Save ID before delete
    neil_gaiman = book2_instance.authors[0].id
    terry_pratchett = book2_instance.authors[1].id
    db_session.delete(book2_instance)  # Delete book linked to customer
    db_session.commit()

    assert db_session.get(Book, book_id) is None  # Check book instance deleted
    assert db_session.get(Author, neil_gaiman) is not None
    assert db_session.get(Author, terry_pratchett) is None


def test_delete_all_customers_deletes_book(
    db_session: scoped_session[Session],
    book2_instance: Book,
) -> None:
    """
    Test Book relationship with customers, when multiple customers are associated with a single
    book, book instance will persist unless all associated customers are deleted.
    """

    book_id = book2_instance.id  # Store book id before delete
    author1_id = book2_instance.authors[0].id
    author1 = db_session.get(Author, author1_id)
    author2_id = book2_instance.authors[1].id
    author2 = db_session.get(Author, author2_id)

    db_session.delete(author1)  # Delete author linked to book
    db_session.commit()

    assert db_session.get(Author, author1_id) is None  # Check author1 deleted
    assert db_session.get(Book, book_id) is not None  # Check book not deleted

    db_session.delete(author2)
    db_session.commit()

    assert db_session.get(Author, author2_id) is None  # Check customer 2 deleted
    assert db_session.get(Book, book_id) is None  # Check book deleted
