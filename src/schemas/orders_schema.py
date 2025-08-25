"""Schema for Order using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    fields,
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import Range  # Used to validate price
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import Order  # Order model


class OrderSchema(SQLAlchemyAutoSchema):
    """Schema for Order model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Order
        load_instance = False  # Prevent automatic deserialization
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests
        ordered = True  # Serializes fields in order they are defined in schema

    @pre_load  # Process data before validation
    def strip_data(self, data: Any, **kwargs) -> Any:
        """Iterate over key-value pairs, strip whitespace from value and return"""

        if not isinstance(data, dict):  # Skip non-dict data
            return data
        for key, value in data.items():
            value = value.strip() if isinstance(value, str) else value
            data[key] = None if value == "" else value
        return data

    id = auto_field(dump_only=True)
    customer_id = auto_field(
        required=True,  # Required
        validate=[  # Enforce length and valid postcode characters
            Range(min=1, error="address_id must be a positive integer if provided")
        ],  # Validation of existence only for business level logic
    )

    order_date = auto_field(dump_only=True)  # Server sets this value
    price_total = fields.Float(  # Validates price on schema deserialization
        required=True,  # Requires field with value
        validate=[
            Range(min=0, max=9999.99, error="price must be between 0 and 999.99")
        ],
        error_messages={"required": "price is required, and must be a float"},
    )

    # Include nested order items with book details
    order_items = fields.Nested("OrderItemSchema", many=True)


order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
