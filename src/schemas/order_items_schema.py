"""Schema for OrderItem using Marshmallow"""

from typing import Any  # Used for type hints
from marshmallow import (
    fields,
    pre_load,  # Schema uses pre_load hook to strip data before validating
    EXCLUDE,  # unknown = EXCLUDE ignores extra or invalid fields
)
from marshmallow.validate import Range  # Used to validate quantity
from marshmallow_sqlalchemy import (
    SQLAlchemyAutoSchema,  # Auto Schema automatically generates fields based on model
    auto_field,  # Automatically infers data type from model and allows marshmallow validation
)
from models import OrderItem  # OrderItem model


class OrderItemSchema(SQLAlchemyAutoSchema):
    """Schema for OrderItem model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = OrderItem
        load_instance = False  # Prevent automatic deserialization
        unknown = EXCLUDE  # Ignores extra or unknown fields in requests
        # Decide whether to include book details when serializing order items
        include_relationships = False  # We want only book for nested relationships
        ordered = True  # Serializes fields in order they are defined in schema
        exclude = ("order_id",)  # Order_items will be nested within order

    @pre_load  # Process data before validation
    def strip_data(self, data: Any, **kwargs) -> Any:
        """Iterate over key-value pairs, strip whitespace from value and return"""

        if not isinstance(data, dict):  # Skip non-dict data
            return data
        for key, value in data.items():
            value = value.strip() if isinstance(value, str) else value
            data[key] = None if value == "" else value
        return data

    book_id = auto_field(required=True)  # Can change from routes for orders
    order_id = auto_field(dump_only=True)  # Only needed for loading
    quantity = auto_field(  # Validates quantity on schema deserialization
        required=True,  # Requires field with value
        validate=[Range(min=1, error="quantity must be at least 1")],
        strict=True,  # Reject floats
        error_messages={"required": "quantity is required and must be an integer"},
    )
    # When nested in orders, include book details
    book = fields.Nested("BookSchema", only=("id", "title", "price"), dump_only=True)


order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
