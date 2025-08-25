"""Main application file for creating and configuring Flask application."""

from sqlite3 import Connection as SQLiteConnection  # Lets us check if SQLite connection
from typing import Any  # Used for type hints
from flask import Flask  # Used for creating Flask app instance
from sqlalchemy import (
    PoolProxiedConnection,  # Used for type hints
    event,  # Used for listening for db connection
)
from sqlalchemy.engine import Engine  # Used to listen for Engine connection
from extensions import db  # SQLAlchemy Instance
from cli_commands import registerable_cli_commands
from controllers import controller_blueprints  # Used to register blueprint controllers


def create_app(
    config_class: str | type[Any] = "config.DevConfig",
) -> Flask:  # Sets DevConfig as default configuration unless different config passed
    """Create and configure Flask application instance using configuration passed by config_class"""

    app = Flask(__name__)  # Create Flask app instance
    app.json.sort_keys = False  # Preserve schema field order in json responses
    app.config.from_object(config_class)  # Loads the relevant config from config.py
    # after being passed as a string as an argument in create_app()
    db.init_app(app)  # Connects SQLAlchemy db object to Flask app object, mapping ORM,
    # applying configuration and creating engine connecting database

    @event.listens_for(Engine, "connect")  # Listens for database engine connection
    def set_sqlite_pragma(
        dbapi_connection: SQLiteConnection | Any,  # Database connection object
        connection_record: PoolProxiedConnection | Any,  # SQLAlchemy Wrapper
    ) -> None:
        """Allows SQLite to use FK relationships by executing PRAGMA statement each time
        db connection is made (such as query or transaction) and db instance is SQLite.
        """
        # Executes if db connection object is an sqlite connection object
        if isinstance(dbapi_connection, SQLiteConnection):
            cursor = dbapi_connection.cursor()  # Create cursor object for SQL commands
            cursor.execute("PRAGMA foreign_keys=ON")  # Executes command per connection
            cursor.close()  # Close cursor to free resources

    for command in registerable_cli_commands:  # Iterate CLI commands
        app.cli.add_command(command)  # Register each CLI command

    for controller in controller_blueprints:
        app.register_blueprint(controller)  # Register each blueprint controller

    return app  # Return the configured app instance
