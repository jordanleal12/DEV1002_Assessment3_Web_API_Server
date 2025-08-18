"""Schema for Address using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import Length, Regexp  # Used to validate in auto_field
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import Address  # Addresses model


class AddressSchema(SQLAlchemyAutoSchema):
    """Schema for Address model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Address
        load_instance = False  # Prevent automatic deserialization, which can trigger
        # Model level validation and skip schema validation
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests
        # Relationships to be defined later when Customer model is created

    @pre_load  # Calls below method to process data before being validated/deserialized by schema
    def strip_data(self, data: Any, **kwargs) -> Any:
        """Iterate over key-value pairs, strip whitespace from value and return"""

        if not isinstance(data, dict):  # Skips non dict data (i.e nested schemas)
            return data
        for key, value in data.items():  # Split into key-value pairs and iterate over
            value = value.strip() if isinstance(value, str) else value  # Strip strings
            data[key] = None if value == "" else value  # Replace empty string with None
        return data  # Replace each value with a stripped version if exists

    id = auto_field(dump_only=True)  # Lets PK be viewed but not changed from routes

    country_code = auto_field(  # Validates country_code on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce Length and return custom error message when violated
            Length(equal=2, error="country_code must be exactly 2 characters"),
            Regexp(r"^[A-Za-z]+$", error="country_code must contain only letters"),
        ],  # Regexp enforces alpha characters only
        error_messages={  # Override default error message, when field is empty and required
            "required": "country_code is required"
        },
    )

    state_code = auto_field(  # Validates state_code on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce length & alpha characters
            Length(min=2, max=3, error="state_code must be 2-3 characters"),
            Regexp(r"^[A-Za-z]+$", error="state_code must contain only letters"),
        ],
        error_messages={"required": "state_code is required"},  # Change default message
    )

    city = auto_field(  # Validates city on schema deserialization
        required=False,  # Does not require field
        allow_none=True,  # If field is provided, allows None value
        validate=[Length(max=50, error="city name cannot exceed 50 characters")],
    )

    street = auto_field(  # Validates street on schema deserialization
        required=True,  # Requires field with value
        validate=[Length(max=100, error="street cannot exceed 100 characters")],
        error_messages={"required": "street is required"},  # Change default message
    )

    postcode = auto_field(  # Validates postcode on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce length and valid postcode characters
            Length(min=2, max=10, error="postcode must be 2-10 characters"),
            Regexp(r"^[a-zA-Z0-9\s\-*]+$", error="must be valid postcode"),
        ],
        error_messages={"required": "postcode is required"},  # Change default message
    )


address_schema = AddressSchema()  # Instance of schema for single address
addresses_schema = AddressSchema(many=True)  # Instance of schema for multiple addresses
