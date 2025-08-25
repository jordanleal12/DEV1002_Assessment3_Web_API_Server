"""Controller for API home page with some basic information."""

from flask import Blueprint, jsonify
from utils.error_handling import handle_errors

# Allows importing routes to main via blueprints
home = Blueprint("home", __name__, url_prefix="")


@home.route("/")
@handle_errors
def get_home():
    """API home page with basic info and navigation."""

    return (
        jsonify(
            {
                "name": "Jordan's Online Bookstore Emporium",
                "description": "API for managing an online bookstore and customers",
                "endpoints": {
                    "books": "/books",
                    "book": "/books/<book_id>",
                    "customers": "/customers",
                    "customer": "/customers/<customer_id>",
                    "orders": "/orders",
                    "order": "/orders/<order_id>",
                    "addresses": "/addresses",
                    "address": "/addresses/<address_id>",
                },
                "docs": "https://github.com/jordanleal12/DEV1002_Assessment3_Web_API_Server",
            }
        ),
        200,
    )
