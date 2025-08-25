"""Controller for defining routes with CRUD functionality for books table"""

from flask import (
    Blueprint,  # For registering blueprints in main
    request,  # Used for HTTP requests
    jsonify,  # Serializes data to json
)
from werkzeug.exceptions import abort  # Used to raise HTTP exceptions
from extensions import db  # SQLAlchemy instance
from models import Book, Name, Author, BookAuthor  # Table models
from schemas import book_schema, books_schema  # Book schemas
from utils import (
    handle_errors,
    fetch_or_create_author,
)  # Error handling decorator function

# Allows importing routes to main via blueprints
books = Blueprint("books", __name__, url_prefix="/books")


@books.route("", methods=["POST"])
@handle_errors  # Adds function as decorator to run error handling
def create_book():
    """
    Create a new book instance, and associated book_authors instance(s), checking for existing
    authors by matching names, and creating new authors if no existing instance, from POST request.
    """

    data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not data:  # Validate that request contains data
        abort(400, description="Json data is missing or invalid")

    book_data = book_schema.load(data)  # Validate/deserialize with schema
    authors_data = book_data.pop("authors")  # Separate nested author data

    book = Book(**book_data)
    db.session.add(book)
    db.session.flush()

    for author_dict in authors_data:  # Iterate over attached list of authors
        author = fetch_or_create_author(author_dict)  # Return existing or new author
        # Create book_author instance using new or existing author instance per author
        book_author = BookAuthor(book_id=book.id, author_id=author.id)
        db.session.add(book_author)

    db.session.commit()

    # Returns the created book as JSON with 201 status
    return jsonify(book_schema.dump(book)), 201


@books.route("", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_books():
    """Fetch all book instances from db using GET request."""

    stmt = db.select(Book)  # Create SQL SELECT object for querying book table
    # Get books as list of scalar objects
    books_list = db.session.scalars(stmt).all()
    data = books_schema.dump(books_list)  # Deserialize to dict with schema

    return jsonify(data), 200  # Return Json of all book instances


@books.route("/<int:book_id>", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_book(book_id):
    """Fetch single book instance from db using GET request."""

    # Check book_id is positive integer
    if book_id < 1:
        abort(400, description="Book ID must be a positive integer")

    book = db.session.get(Book, book_id)  # Get book instance

    if not book:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Book with ID {book_id} not found")

    data = book_schema.dump(book)
    return jsonify(data), 200  # Return json of single book instance


@books.route("/<int:book_id>", methods=["PUT", "PATCH"])
@handle_errors  # Adds function as decorator to run error handling
def update_book(book_id):
    """Fetch and update book instance using PUT/PATCH request"""

    # Check book_id is positive integer
    if book_id < 1:
        abort(400, description="Book ID must be a positive integer")

    book = db.session.get(Book, book_id)  # Get book instance

    if not book:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Book with ID {book_id} not found")

    json_data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not json_data:
        abort(400, description="Json data is missing or invalid")

    true_if_patch = request.method == "PATCH"  # True if PATCH else False

    # Deserialize and validate with schema
    updated_book = book_schema.load(
        json_data,  # Passes Json data from HTTP request
        partial=true_if_patch,  # Ignores missing fields if PATCH
        session=db.session,  # Allows validation of FK relationships
    )

    if "authors" in updated_book:  # Update  values if included
        updated_authors = updated_book["authors"]  # Get list of authors from json
        current_authors = book.authors  # List of current authors

        for i, author_dict in enumerate(updated_authors):  # Iterate list items & index
            name_data = author_dict["name"]  # Nested dict of name values
            if i < len(current_authors):  # Check index less than length of authors list
                author = current_authors[i]  # Replace current author attributes
                for field, value in name_data.items():
                    setattr(author.name, field, value)
            else:  # If index not less than author list new author is created
                # Function returns existing author if name matches else creates new author instance
                author = fetch_or_create_author(author_dict)
                book_author = db.session.get(  # If existing author, should be existing book_author
                    BookAuthor, {"book_id": book.id, "author_id": author.id}
                )
                if not book_author:  # Only create new book_author if new author
                    book_author = BookAuthor(book_id=book.id, author_id=author.id)
                    db.session.add(book_author)

    # Update instance attributes and validate with model before commit
    for field, value in updated_book.items():
        if field != "authors":  # Skip nested fields
            setattr(book, field, value)

    db.session.commit()

    return jsonify(book_schema.dump(book)), 200


@books.route("/<int:book_id>", methods=["DELETE"])
@handle_errors  # Adds function as decorator to run error handling
def delete_book(book_id):
    """Delete single book instance from db using DELETE request."""

    # Check book_id is positive integer
    if book_id < 1:
        abort(400, description="Book ID must be a positive integer")

    book = db.session.get(Book, book_id)  # Get book instance

    if not book:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Book with ID {book_id} not found")

    for book_author in book.book_authors.copy():  # Copy to not change iterator
        db.session.delete(book_author)  # Delete associated book_author instances
    db.session.flush()  # Update FK relationships after delete

    for author in book.authors.copy():  # Copy to not change iterator
        author_books = len(author.book_authors)  # Count book_author instances
        if author_books == 0:  # Delete orphaned author and name if no book_author
            db.session.delete(author)
            db.session.delete(author.name)
    db.session.flush()

    db.session.delete(book)  # Delete book instance from database
    db.session.commit()

    return (jsonify(book_schema.dump(book)), 200)  # Return json of deleted book
