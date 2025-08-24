"""Schema for Book using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    ValidationError,
    fields,
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import Length, Regexp, Range  # Used to validate in auto_field
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from utils import validate_publication_year, validate_bool
from models import Book  # Books model


class BookSchema(SQLAlchemyAutoSchema):
    """Schema for Book model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Book
        load_instance = False  # Prevent automatic deserialization, which can trigger
        # Model level validation and skip schema validation
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests

    authors = fields.Nested("AuthorSchema", many=True, required=True)  # Nested authors

    @pre_load  # Calls below method to process data before being validated/deserialized by schema
    def strip_data(self, data: Any, **kwargs) -> Any:
        """Iterate over key-value pairs, strip whitespace from value and return"""

        if not isinstance(data, dict):  # Skips non dict data (i.e nested schemas)
            return data
        for key, value in data.items():  # Split into key-value pairs and iterate over
            value = value.strip() if isinstance(value, str) else value  # Strip strings
            data[key] = None if value == "" else value  # Replace empty string with None
            if key == "isbn" and isinstance(value, str):  # Replace '-' and whitespace
                data[key] = value.replace("-", "").replace(" ", "")
            if key == "discontinued" and not isinstance(value, bool):
                raise ValidationError(  # Prevent 1 or 0 passing as boolean value
                    {"required": "discontinued is required as boolean value"}
                )
        return data  # Replace each value with a stripped version if exists

    id = auto_field(dump_only=True)  # Lets PK be viewed but not changed from routes

    isbn = auto_field(  # Validates isbn on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce Length and return custom error message when violated
            Length(min=10, max=13, error="isbn must be 10 or 13 characters."),
            Regexp(r"^\d+$", error="isbn must contain only digits"),
        ],  # Regexp enforces numeric characters only
        error_messages={  # Override default error message, when field is empty and required
            "required": "isbn is required"
        },
    )

    series = auto_field(  # Validates series on schema deserialization
        required=False,  # Does not require field
        allow_none=True,  # If field is provided, allows None value
        validate=[Length(max=255, error="series cannot exceed 255 characters")],
    )

    publication_year = auto_field(  # Validates publication_year on deserialization
        required=True,  # Requires field with value
        # Custom function checks between 1000 and current year
        validate=[validate_publication_year],
        strict=True,  # Reject floats
        error_messages={"required": "publication_year is required"},
    )

    discontinued = auto_field(  # Validates discontinued on schema deserialization
        required=True,  # Requires field with value
        validate=[validate_bool],  # Custom function checks is instance bool
        error_messages={"required": "discontinued is required as boolean value"},
    )

    price = fields.Float(  # Validates price on schema deserialization
        required=True,  # Requires field with value
        validate=[Range(min=0, max=999.99, error="price must be between 0 and 999.99")],
        error_messages={"required": "price is required, 0 if discontinued"},
    )

    quantity = auto_field(  # Validates quantity on schema deserialization
        required=True,  # Requires field with value
        validate=[Range(min=0, error="quantity cannot be negative")],
        strict=True,  # Reject floats
        error_messages={"required": "quantity is required, 0 if no stock"},
    )


book_schema = BookSchema()  # Instance of schema for single book
books_schema = BookSchema(many=True)  # Instance of schema for multiple books
