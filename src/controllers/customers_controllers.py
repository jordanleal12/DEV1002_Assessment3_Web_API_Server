"""Controller for defining routes with CRUD functionality for customers table"""

from flask import (
    Blueprint,  # For registering blueprints in main
    request,  # Used for HTTP requests
    jsonify,  # Serializes data to json
)
from werkzeug.exceptions import abort  # Used to raise HTTP exceptions
from extensions import db  # SQLAlchemy instance
from models import Customer, Name  # Customer model
from schemas import customer_schema, customers_schema  # Customer schemas
from utils.error_handling import handle_errors  # Error handling decorator function

# Allows importing routes to main via blueprints
customers = Blueprint("customers", __name__, url_prefix="/customers")


@customers.route("", methods=["POST"])
@handle_errors  # Adds function as decorator to run error handling
def create_customer():
    """Create a new customer and associated name instance from a POST request."""

    data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not data:  # Validate that request contains data
        abort(404, description="Json data is missing or invalid")

    loaded_data = customer_schema.load(data)  # Validate/deserialize with schema

    name_data = loaded_data.pop("name")  # Separate nested name data
    name = Name(**name_data)  # Validate/deserialize with Name model

    db.session.add(name)  # Add name instance to session
    db.session.flush()  # Save pending database changes so we can access name id

    # Validate/deserialize with customer model and assign name id
    customer = Customer(**loaded_data, name_id=name.id)

    db.session.add(customer)  # Adds customer instance to db session
    db.session.commit()  # Commits current session to the database

    # Returns the created customer as JSON with 201 status
    return jsonify(customer_schema.dump(customer)), 201


@customers.route("", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_customers():
    """Fetch all customer instances from db using GET request."""

    stmt = db.select(Customer)  # Create SQL SELECT object for querying customer table
    # Get customers as list of scalar objects
    customers_list = db.session.scalars(stmt).all()
    data = customers_schema.dump(customers_list)  # Deserialize to dict with schema

    return jsonify(data), 200  # Return Json of all customer instances


@customers.route("/<int:customer_id>", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_customer(customer_id):
    """Fetch single customer instance from db using GET request."""

    # Check customer_id is positive integer
    if customer_id < 1:
        abort(400, description="Customer ID must be a positive integer")

    customer = db.session.get(Customer, customer_id)  # Get customer instance

    if not customer:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Customer with ID {customer_id} not found")

    data = customer_schema.dump(customer)
    return jsonify(data), 200  # Return json of single customer instance


@customers.route("/<int:customer_id>", methods=["PUT", "PATCH"])
@handle_errors  # Adds function as decorator to run error handling
def update_customer(customer_id):
    """Fetch and update customer instance using PUT/PATCH request"""

    # Check customer_id is positive integer
    if customer_id < 1:
        abort(400, description="Customer ID must be a positive integer")

    customer = db.session.get(Customer, customer_id)  # Get customer instance

    if not customer:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Customer with ID {customer_id} not found")

    json_data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not json_data:
        abort(400, description="Json data is missing or invalid")

    true_if_patch = request.method == "PATCH"  # True if PATCH else False

    # Deserialize and validate with schema
    updated_customer = customer_schema.load(
        json_data,  # Passes Json data from HTTP request
        partial=true_if_patch,  # Ignores missing fields if PATCH
        session=db.session,  # Allows validation of FK relationships
    )

    if "name" in updated_customer:  # Update name values if included
        for field, value in updated_customer["name"].items():
            setattr(customer.name, field, value)

    # Update instance attributes and validate with model before commit
    for field, value in updated_customer.items():
        if field != "name":  # Skip nested fields
            setattr(customer, field, value)

    db.session.commit()

    return jsonify(customer_schema.dump(customer)), 200


@customers.route("/<int:customer_id>", methods=["DELETE"])
@handle_errors  # Adds function as decorator to run error handling
def delete_customer(customer_id):
    """Delete single customer instance from db using DELETE request."""

    # Check customer_id is positive integer
    if customer_id < 1:
        abort(400, description="Customer ID must be a positive integer")

    customer = db.session.get(Customer, customer_id)  # Get customer instance

    if not customer:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Customer with ID {customer_id} not found")

    db.session.delete(customer)  # Delete customer instance from database
    db.session.commit()

    return (
        jsonify(customer_schema.dump(customer)),
        200,
    )  # Return json of deleted customer instance
