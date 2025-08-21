"""Schema for Name using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import Length  # Used to validate in auto_field
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import Name  # Names model


class NameSchema(SQLAlchemyAutoSchema):
    """Schema for Name model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Name
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

    first_name = auto_field(  # Validates first_name on schema deserialization
        required=True,  # Requires field with value
        validate=[  # Enforce Length and return custom error message when violated
            Length(min=3, max=50, error="First name must be 3-50 characters"),
        ],  # Regex shouldn't be used for names
        error_messages={  # Override default error message, when field is empty and required
            "required": "first_name is required"
        },
    )

    last_name = auto_field(  # Validates last_name on schema deserialization
        required=False,  # Some names are one name only
        validate=[  # Enforce length & alpha characters
            Length(max=50, error="if given, last name must be 50 characters or less"),
        ],
    )


name_schema = NameSchema()  # Instance of schema for single name
names_schema = NameSchema(many=True)  # Instance of schema for multiple names
