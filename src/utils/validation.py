"""Validation functions to keep code DRY while validating data"""

from datetime import datetime  # For validating current year
from marshmallow import ValidationError  # Schema level validation error


def checks_input(
    value: str | None,
    column_name: str,
    required: bool = True,
    data_type: type[any] = str,
    min_len: int | None = None,
    max_len: int | None = None,
    min_val: int | None = None,
    max_val: int | None = None,
) -> any:
    """
    Takes a column input to be passed to an @validates decorator, checking if value exists if
    required, if instance matches correct data type, and if length meets length requirements,
    returning a ValueError on invalid input.
    """

    # Return None if no value and not required, or ValueError if required
    if value is None:
        if required:
            raise ValueError(f"{column_name} is required")
        return None

    if not isinstance(value, data_type):  # Checks if value matches data_type (e.g. str)
        raise ValueError(f"{column_name} must be type {data_type}")

    if data_type is str:  # Applies the following to string columns only
        value = value.strip()  # Strips whitespace

        if required and len(value) == 0:  # Checks value is not empty string
            raise ValueError(f"{column_name} is required and cannot be empty")

        if min_len is not None and max_len is not None:  # If both min and max length
            # If min and max length equal and value doesn't match
            if min_len == max_len and len(value) != max_len:
                raise ValueError(f"{column_name} must be exactly {max_len} characters")
            # If value isn't between min and max length range
            if not min_len <= len(value) <= max_len:
                raise ValueError(
                    f"{column_name} must be between {min_len} and {max_len} characters."
                )
        # min length only, checks value is greater
        if min_len is not None and len(value) < min_len:
            raise ValueError(f"{column_name} must be at least {min_len} characters")
        # max length only, checks value is lesser
        if max_len is not None and len(value) > max_len:
            raise ValueError(f"{column_name} cannot exceed {max_len} characters")

    if data_type is int or float:  # Applies the following to integer columns only

        if min_val is not None and max_val is not None:  # If both min and max value
            # If min and max value equal and value doesn't match
            if min_val == max_val and value != max_val:
                raise ValueError(f"{column_name} must be exactly {max_val}")
            # If value isn't between min and max value range
            if not min_val <= value <= max_val:
                raise ValueError(
                    f"{column_name} must be between {min_val} and {max_val}."
                )
        # min value only, checks value is greater
        if min_val is not None and value < min_val:
            raise ValueError(f"{column_name} must be at least {min_val}.")
        # max value only, checks value is lesser
        if max_val is not None and value > max_val:
            raise ValueError(f"{column_name} cannot exceed {max_val}.")

    return value


def validate_publication_year(value) -> None:
    """
    Custom function to validate publication year within 1000 and current year to be passed
    to schema, as datetime would only be called once per app startup in schema, so we need
    to pass a custom function that calls datetime each validation, giving current datetime
    """
    if not isinstance(value, int):
        raise ValidationError("publication_year must be a whole number integer")
    if not 1000 <= value <= datetime.now().year:
        raise ValidationError(
            f"publication_year must be between 1000 and {datetime.now().year}"
        )


def validate_bool(value) -> None:
    """Used to validate boolean instance in schema"""

    if not isinstance(value, bool):
        raise ValidationError("Discontinued must be boolean value")
