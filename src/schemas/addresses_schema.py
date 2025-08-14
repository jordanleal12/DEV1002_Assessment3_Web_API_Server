"""Schema for Address using Marshmallow"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import Address
from extensions import db


class AddressSchema(SQLAlchemyAutoSchema):
    """Schema for Address model using Auto Schema"""

    class Meta:
        """Sets metadata and controls behavior of the schema"""

        model = Address
        load_instance = True  # Automatically converts json data to python object
        sqla_session = db.session  # Links SQLAlchemy session to the schema, allowing it
        # to validate and load objects from foreign key/relationships when deserializing

        # Relationships to be defined later when Customer model is created


address_schema = AddressSchema()  # Instance of schema for single address
addresses_schema = AddressSchema(many=True)  # Instance of schema for multiple addresses
