from functools import wraps  # Used to preserve metadata of wrapped functions
from flask import jsonify  # For formatting responses as json
from sqlalchemy.exc import SQLAlchemyError, IntegrityError  # SQLAlchemy level errors
from marshmallow import ValidationError  # Schema level errors
from psycopg2 import (
    OperationalError,  # Database operation errors
    errorcodes,  # For diagnosing error codes
)
from werkzeug.exceptions import HTTPException  # Flask level exceptions (e.g. abort)
from extensions import db  # SQLAlchemy instance


def handle_errors(func):
    """Decorator function to process error handling in routes"""

    @wraps(func)  # Preserves metadata of function being decorated
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)  # Attempts route with error handling

        except HTTPException as e:  # Flask level exceptions (e.g. abort)
            return (
                jsonify(
                    {
                        "error": e.name,  # Error name, e.g. "Not Found"
                        "message": e.description or "An error occurred",
                    }
                ),
                e.code,  # Attaches error code (e.g. 404)
            )

        except ValidationError as e:  # Schema level validation errors
            return (
                jsonify({"error": "Schema Validation Failed", "messages": e.messages}),
                400,
            )

        except ValueError as e:  # Model level validation errors
            return jsonify({"error": "Model Validation Failed", "message": str(e)}), 400

        except IntegrityError as e:  # Database constraint errors like NOT NULL
            db.session.rollback()  # Rollback required as IntegrityError occurs after adding commit
            if e.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:  # NOT NULL violations
                return (
                    jsonify(
                        {
                            "error": "Required field missing",
                            "message": f"{e.orig.diag.column_name} cannot be null",
                        }  # References column name (e.g. country_code)
                    ),
                    400,
                )

            if e.orig.pgcode == errorcodes.UNIQUE_VIOLATION:  # UNIQUE violations
                return (
                    jsonify(
                        {
                            "error": "Duplicate value",
                            "message": f"{e.orig.diag.constraint_name.replace('_key', '')} must be unique",
                        }  # References constraint name (e.g. customers_email_key), removing '_key'
                    ),
                    400,
                )

            if e.orig.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:  # FK violations
                return (
                    jsonify(
                        {
                            "error": "Invalid Relationship",
                            "message": f"Instance referenced by {e.orig.diag.column_name} doesn't exist",
                        }  # References column name (e.g. address_id)
                    ),
                    400,
                )

            return (  # Catch any missed IntegrityErrors
                jsonify(
                    {
                        "error": "Database Integrity Error",
                        "message": str(e.orig),
                    }
                ),
                400,
            )

        except OperationalError as e:  # Database operation errors
            db.session.rollback()
            return (
                jsonify(
                    {
                        "error": "Unexpected Database Error",
                        "message": "Could not connect to database",
                    }
                ),
                503,
            )

        except SQLAlchemyError as e:  # All other SQLAlchemy errors
            db.session.rollback()
            return jsonify({"error": "Database Error", "message": str(e)}), 500

    return decorated_function  # Returns function after executing error handling
