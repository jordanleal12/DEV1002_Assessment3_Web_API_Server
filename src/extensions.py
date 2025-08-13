"""
Create an instance of SQLAlchemy as an object that will be used for handling database connections.
This 'dormant' configuration has no database connection, ORM mapping, or configuration applied.
"""

from flask_sqlalchemy import SQLAlchemy  # Required for SQLAlchemy instance

db = SQLAlchemy()  # Create SQLAlchemy instance as an object
