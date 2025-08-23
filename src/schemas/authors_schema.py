"""Schema for Author using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    fields,
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import Author  # Authors model


class AuthorSchema(SQLAlchemyAutoSchema):
    """Schema for Author model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Author
        load_instance = False  # Prevent automatic deserialization, which can trigger
        # Model level validation and skip schema validation
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests
        # Relationships to be defined later when Author model is created
        exclude = ["name_id"]

    name = fields.Nested("NameSchema", required=True)

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


author_schema = AuthorSchema()  # Instance of schema for single author
authors_schema = AuthorSchema(many=True)  # Instance for multiple authors
