"""Controller for defining routes with CRUD functionality for addresses table"""

from flask import (
    Blueprint,  # For registering blueprints in main
    request,  # Used for HTTP requests
    jsonify,  # Serializes data to json
)
from werkzeug.exceptions import abort  # Used to raise HTTP exceptions
from extensions import db  # SQLAlchemy instance
from models import Address  # Address model
from schemas import address_schema, addresses_schema  # Address schemas
from utils.error_handling import handle_errors  # Error handling decorator function

# Allows importing routes to main via blueprints
addresses = Blueprint("addresses", __name__, url_prefix="/addresses")


@addresses.route("", methods=["POST"])
@handle_errors  # Adds function as decorator to run error handling
def create_address():
    """Create a new address from a POST request."""

    data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not data:  # Validate that request contains data
        abort(404, description="Json data is missing or invalid")

    loaded_data = address_schema.load(data)  # Validate/deserialize with schema
    address = Address(**loaded_data)  # Validate/deserialize with model

    db.session.add(address)  # Adds address instance to db session
    db.session.commit()  # Commits current session to the database

    # Returns the created address as JSON with 201 status
    return jsonify(address_schema.dump(address)), 201


@addresses.route("", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_addresses():
    """Fetch all address instances from db using GET request."""

    stmt = db.select(Address)  # Create SQL SELECT object for querying address table
    # Get addresses as list of scalar objects
    addresses_list = db.session.scalars(stmt).all()
    data = addresses_schema.dump(addresses_list)  # Deserialize to dict with schema

    return jsonify(data), 200  # Return Json of all address instances


@addresses.route("/<int:address_id>", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_address(address_id):
    """Fetch single address instance from db using GET request."""

    # Check address_id is positive integer
    if address_id < 1:
        abort(400, description="Address ID must be a positive integer")

    address = db.session.get(Address, address_id)  # Get address instance

    if not address:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Address with ID {address_id} not found")

    data = address_schema.dump(address)
    return jsonify(data), 200  # Return json of single address instance


@addresses.route("/<int:address_id>", methods=["PUT", "PATCH"])
@handle_errors  # Adds function as decorator to run error handling
def update_address(address_id):
    """Fetch and update address instance using PUT/PATCH request"""

    # Check address_id is positive integer
    if address_id < 1:
        abort(400, description="Address ID must be a positive integer")

    address = db.session.get(Address, address_id)  # Get address instance

    if not address:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Address with ID {address_id} not found")

    json_data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not json_data:
        abort(404, description="Json data is missing or invalid")

    true_if_patch = request.method == "PATCH"  # True if PATCH else False

    # Deserialize and validate with schema
    updated_address = address_schema.load(
        json_data,  # Passes Json data from HTTP request
        partial=true_if_patch,  # Ignores missing fields if PATCH
        session=db.session,  # Allows validation of FK relationships
    )

    # Update instance attributes and validate with model before commit
    for field, value in updated_address.items():
        setattr(address, field, value)

    db.session.commit()

    return jsonify(address_schema.dump(address)), 200


@addresses.route("/<int:address_id>", methods=["DELETE"])
@handle_errors  # Adds function as decorator to run error handling
def delete_address(address_id):
    """Delete single address instance from db using DELETE request."""

    # Check address_id is positive integer
    if address_id < 1:
        abort(400, description="Address ID must be a positive integer")

    address = db.session.get(Address, address_id)  # Get address instance

    if not address:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Address with ID {address_id} not found")

    db.session.delete(address)  # Delete address instance from database
    db.session.commit()

    return (
        jsonify(address_schema.dump(address)),
        200,
    )  # Return json of deleted address instance
