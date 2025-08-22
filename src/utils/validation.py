"""Validation functions to keep code DRY while validating data"""


def checks_input(
    value: str | None,
    column_name: str,
    required: bool = True,
    data_type: type[any] = str,
    min_len: int | None = None,
    max_len: int | None = None,
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

        if min_len and max_len:  # If both min and max length
            # If min and max length equal and value doesn't match
            if min_len == max_len and len(value) != max_len:
                raise ValueError(f"{column_name} must be exactly {max_len} characters")
            # If value isn't between min and max length range
            if not min_len <= len(value) <= max_len:
                raise ValueError(
                    f"{column_name} must be between {min_len} and {max_len} characters."
                )

        if min_len and len(value) < min_len:  # min length only, checks value is greater
            raise ValueError(f"{column_name} must be at least {min_len} characters")

        if max_len and len(value) > max_len:  # max length only, checks value is lesser
            raise ValueError(f"{column_name} cannot exceed {max_len} characters")

    return value
