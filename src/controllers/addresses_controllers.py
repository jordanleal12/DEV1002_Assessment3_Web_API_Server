"""Controller for defining routes with CRUD functionality for addresses table"""

from flask import (
    Blueprint,  # For registering blueprints in main
    request,  # Used for HTTP requests
    jsonify,  # Serializes data to json
)
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

    data = request.get_json()  # Allows custom arguments, request.json does not
    if not data:  # Validate that request contains data
        raise ValueError("No input data provided")

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
    if not isinstance(address_id, int) or address_id < 1:
        raise ValueError("Address ID must be a positive integer")

    address = db.session.get(Address, address_id)  # Get address instance

    if not address:
        raise ValueError(f"Address with id {address_id} not found")
    data = address_schema.dump(address)
    return jsonify(data), 200  # Return json of single address instance
