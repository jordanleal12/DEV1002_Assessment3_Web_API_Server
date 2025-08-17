"""Controller for defining routes with CRUD functionality for addresses table"""

from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError  # DB level errors
from marshmallow.exceptions import ValidationError  # Schema level errors
from psycopg2 import errorcodes  # For specific DB level error messages
from extensions import db  # SQLAlchemy instance
from models import Address  # Address model
from schemas import address_schema, addresses_schema  # Address schemas

# Allows importing routes to main via blueprints
addresses = Blueprint("addresses", __name__, url_prefix="/addresses")


@addresses.route("", methods=["POST"])
def create_address():
    """Create a new address from a POST request."""

    try:
        data = request.get_json()  # Allows custom arguments, request.json does not
        if not data:  # Validate that request contains data
            # Abort invokes error handler whereas returning 400 with dict would not
            abort(400, description="No input data provided.")

        deserialized = address_schema.load(data)  # Validate/deserialize with schema
        address = Address(**deserialized)  # Validate/deserialize with model

        db.session.add(address)  # Adds address instance to db session
        db.session.commit()  # Commits current session to the database

        # Returns the created address as JSON with 201 status
        return jsonify(address_schema.dump(address)), 201

    except ValidationError as e:  # Schema level validation errors
        return {"error": "Invalid format", "messages": str(e.messages)}, 400

    except ValueError as e:  # Catch custom @validates errors defined in the model
        return {"error": "Invalid Content", "message": str(e)}, 400

    except IntegrityError as e:  # Database constraint errors like NOT NULL or UNIQUE
        db.session.rollback()  # Rollback required as IntegrityError occurs after adding to session
        if (
            e.orig.pgcode == errorcodes.NOT_NULL_VIOLATION
        ):  # Custom message for NOT NULL violations
            return {
                "error": "Required field missing",
                "field": str(e.orig.diag.column_name),
            }, 400
        return {
            "error": "Database Integrity Error",
            "message": str(e.orig),
        }, 400  # General error message for miscellaneous integrity issues


@addresses.route("", methods=["GET"])
def get_addresses():
    """Fetch all address instances from db using GET request."""

    stmt = db.select(Address)  # Create SQL SELECT object for querying address table
    # Get addresses as list of scalar objects
    addresses_list = db.session.scalars(stmt).all()
    data = addresses_schema.dump(addresses_list)  # Deserialize to dict with schema

    if data:
        return jsonify(data)  # Return Json of all address instances
    else:
        return {"message": "No address records found."}, 404  # Error msg for no records


@addresses.route("/<int:address_id>", methods=["GET"])
def get_address(address_id):
    """Fetch single address instance from db using GET request."""

    address = db.session.get(Address, address_id)
    data = address_schema.dump(address)

    if data:
        return jsonify(data)
    else:
        return {"message": "No address record found."}, 404
