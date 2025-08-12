"""
Configuration file that manages environment specific settings by making configuration profiles
that allow us to run different environments as required (i.e. DevConfig for development,
TestConfig for testing). Safely loads environment variables from .env without exposing them.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class. Settings from this class are used across all configurations."""

    # Cryptographic key used to secure cookies, session data, CSRF tokens, etc.
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Legacy feature best set to false.


class DevConfig(Config):  # Inherits from Config
    """Development configuration. Settings from this class are used in development environment."""

    # Pull database URI from .env, which provides database connection string with name + password
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
    DEBUG = True  # Enables debug mode, automatically updates flask server and gives error pages


class TestConfig(Config):  # Inherits from Config
    """Testing configuration. Settings from this class are used in pytest environment."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Create in memory sqlite database
    TESTING = True  # Stops Flask catching HTTP errors, enables test features for some extensions
    WTF_CSRF_ENABLED = False  # Disables protection for Cross-Site Request Forgery
