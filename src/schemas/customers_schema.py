"""Schema for Customer using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    fields,
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import (
    Email,
    Length,
    Range,
    Regexp,
)  # Used to validate in auto_field
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import Customer  # Customers model


class CustomerSchema(SQLAlchemyAutoSchema):
    """Schema for Customer model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Customer
        load_instance = False  # Prevent automatic deserialization, which can trigger
        # Model level validation and skip schema validation
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests
        exclude = ["name_id"]

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

    email = auto_field(  # Validates email on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce Length and return custom error message when violated
            Length(min=3, max=254, error="email must be between 3-254 characters"),
            Email(error="Invalid email address provided, please use valid email"),
        ],
        error_messages={  # Override default error message, when field is empty and required
            "required": "email is required and must be valid"
        },  # Uniqueness not enforced in schema - not atomic
    )

    phone = auto_field(  # Validates phone on schema deserialization
        required=False,  # Phone number not required field
        allow_none=True,  # If field is provided, allows None value
        validate=[  # Enforce length & regex
            Length(min=7, max=20, error="Phone number must be between 7-20 digits"),
            Regexp(r"^[+\d][+\d\s\-\(\)\.]+$", error="Invalid phone number provided"),
        ],
    )

    address_id = auto_field(  # Validates address_id on schema deserialization
        required=False,  # Not required since it's nullable
        allow_none=True,  # If field is provided, allows None value
        validate=[  # Enforce length and valid postcode characters
            Range(min=1, error="address_id must be a positive integer if provided")
        ],  # Validation of existence only for business level logic
    )
    name = fields.Nested("NameSchema", required=True)


customer_schema = CustomerSchema()  # Instance of schema for single customer
customers_schema = CustomerSchema(many=True)  # Instance for multiple customers
