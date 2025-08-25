"""Controller for defining routes with CRUD functionality for orders table"""

from flask import (
    Blueprint,  # For registering blueprints in main
    request,  # Used for HTTP requests
    jsonify,  # Serializes data to json
)
from sqlalchemy import desc
from werkzeug.exceptions import abort  # Used to raise HTTP exceptions
from extensions import db  # SQLAlchemy instance
from models import Order, Name, Author, OrderItem, Customer, Book  # Table models
from schemas import order_schema, orders_schema  # Order schemas
from utils.error_handling import handle_errors  # Error handling decorator function

# Allows importing routes to main via blueprints
orders = Blueprint("orders", __name__, url_prefix="/orders")


@orders.route("", methods=["POST"])
@handle_errors  # Adds function as decorator to run error handling
def create_order():
    """Create a new order and associated order_items and authors instance from a POST request."""

    data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not data:  # Validate that request contains data
        abort(400, description="Json data is missing or invalid")

    order_data = order_schema.load(data)  # Validate/deserialize with schema

    customer_id = order_data["customer_id"]  # Get customer_id from order_data
    customer = db.session.get(Customer, customer_id)
    if not customer:  # Raise 404 for no customer associated with customer_id
        abort(404, description=f"Customer with ID {customer_id} not found")

    # Get order_items data, returns empty list if no order_items
    order_items_data = order_data.pop("order_items", [])
    if not order_items_data:  # Return 400 for missing order_items
        abort(400, description="At least one order item is required per order")

    order = Order(**order_data)  # Create order instance
    db.session.add(order)
    db.session.flush()  # Flush to get order.id

    total_price = 0  # Set total price to be added to from order items

    for item in order_items_data:
        book = db.session.get(Book, item["book_id"])  # Validate book exists
        if not book:  # Return 404 for missing book
            abort(404, description=f"Book with ID {item['book_id']} not found")
        quantity = item.get("quantity", 1)  # Default 1 if quantity not provided
        total_price += book.price * quantity  # Add to total price
        # Create order_item instance with order id, book id and quantity
        order_item = OrderItem(order_id=order.id, book_id=book.id, quantity=quantity)
        db.session.add(order_item)  # Add order_item to session

    order.price_total = total_price  # Update order price total from order items

    db.session.commit()

    # Returns the created order as JSON with 201 status
    return jsonify(order_schema.dump(order)), 201


@orders.route("", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_orders():
    """Fetch all order instances from db using GET request."""

    stmt = db.select(Order)  # Create SQL SELECT object for querying order table
    # Get orders as list of scalar objects
    orders_list = db.session.scalars(stmt).all()
    data = orders_schema.dump(orders_list)  # Deserialize to dict with schema

    return jsonify(data), 200  # Return Json of all order instances


@orders.route("/<int:order_id>", methods=["GET"])
@handle_errors  # Adds function as decorator to run error handling
def get_order(order_id):
    """Fetch single order instance from db using GET request."""

    # Check order_id is positive integer
    if order_id < 1:
        abort(400, description="Order ID must be a positive integer")

    order = db.session.get(Order, order_id)  # Get order instance

    if not order:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Order with ID {order_id} not found")

    data = order_schema.dump(order)
    return jsonify(data), 200  # Return json of single order instance


@orders.route("/<int:order_id>", methods=["PUT", "PATCH"])
@handle_errors  # Adds function as decorator to run error handling
def update_order(order_id):
    """Fetch and update order instance using PUT/PATCH request"""

    # Check order_id is positive integer
    if order_id < 1:
        abort(400, description="Order ID must be a positive integer")

    order = db.session.get(Order, order_id)  # Get order instance

    if not order:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Order with ID {order_id} not found")

    json_data = request.get_json(silent=True)  # Prevents error raising on invalid json
    if not json_data:
        abort(400, description="Json data is missing or invalid")

    true_if_patch = request.method == "PATCH"  # True if PATCH else False

    # Deserialize and validate with schema
    updated_order = order_schema.load(
        json_data,  # Passes Json data from HTTP request
        partial=true_if_patch,  # Ignores missing fields if PATCH
        session=db.session,  # Allows validation of FK relationships
    )

    total_price = 0.0  # Price to be added from new order_items
    checked_books = set()  # Keep track of unique book IDs

    if "customer_id" in updated_order:  # Prevent changing of customer_id
        if updated_order["customer_id"] != order.customer_id:
            abort(400, description="Cannot change customer_id on current order")

    if not "order_items" in updated_order:  # Raise error for no order_items
        abort(400, description="order_items list is required")

    updated_items = updated_order.pop("order_items")  # Get list of order_items
    if len(updated_items) == 0:  # Return 400 for empty order_items list
        abort(400, description="order_items list cannot be empty")

    for order_item in updated_items:  # Iterate over order_items
        book_id = order_item.get("book_id", None)
        if not book_id:  # Order item requires book id
            abort(400, description="book_id is required for order_items")
        # Match existing order id if order_item order id is incorrect or missing
        order_item["order_id"] = order_id  # Match order_id to route parameter
        order_item["quantity"] = order_item.get("quantity", 1)  # Default quantity to 1

        existing_item = next(  # Check new order_items against existing items
            (item for item in order.order_items if item.book_id == book_id), None
        )  # Next returns first matching item or None

        if not existing_item:  # Check for existing order_item instance
            book = db.session.get(Book, book_id)
            if not book:  # Check valid book id if new order_item
                abort(404, description=f"Book with ID {book_id} not found")

            if book_id in checked_books:  # Order items must be unique books
                abort(400, description=f"Book with ID {book_id} is duplicated")

            db.session.add(OrderItem(**order_item))  # Create new order_item
            # Update total_price, defaulting quantity to 1 if not provided
            total_price += float(book.price * order_item["quantity"])

        else:  # Update existing order_item quantity and new price total
            existing_item.quantity = order_item["quantity"]
            total_price += float(existing_item.book.price * order_item["quantity"])

        checked_books.add(book_id)  # Add processed book_id to set

    for order_item in order.order_items:  # Delete old order_items not in request
        if order_item.book_id not in checked_books:
            db.session.delete(order_item)

    order.price_total = total_price  # Update order price total from new order items

    db.session.commit()

    return jsonify(order_schema.dump(order)), 200


@orders.route("/<int:order_id>", methods=["DELETE"])
@handle_errors  # Adds function as decorator to run error handling
def delete_order(order_id):
    """Delete single order instance and associated order_items from db using DELETE request."""

    # Check order_id is positive integer
    if order_id < 1:
        abort(400, description="Order ID must be a positive integer")

    order = db.session.get(Order, order_id)  # Get order instance

    if not order:  # Raise HTTP exception if no instance with id
        abort(404, description=f"Order with ID {order_id} not found")
    order_data = order_schema.dump(order)

    for order_item in order.order_items.copy():  # Copy to not change iterator
        db.session.delete(order_item)  # Delete associated order_item instances
    db.session.commit()  # Update FK relationships after delete

    # Listens_for event in order_items model should delete orphaned order instances,
    # check if order deleted and delete if not
    order = db.session.get(Order, order_id)  # Check order instance
    if order:
        db.session.delete(order)  # Delete order instance from database
        db.session.commit()

    return (jsonify(order_data), 200)  # Return json of deleted order
