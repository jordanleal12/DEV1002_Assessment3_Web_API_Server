"""Utility functions for matching existing instances in the database to avoid duplicates"""

from extensions import db  # SQLAlchemy instance
from models.names_model import Name
from models.authors_model import Author  # Table models


def fetch_or_create_author(author_dict: dict) -> Author:
    """Fetch existing author instance from matching name, else create new author"""

    name_data = author_dict.pop("name")  # Separate nested name data
    name_author_query = (  # Select joined table of Name and Author where name matches
        db.select(Name, Author)
        .join(Author, Author.name_id == Name.id)  # Joins Name and Author tables
        .where(  # Filters by matching first name and matching last name if last name exists
            (Name.first_name == name_data.get("first_name"))
            # .get returns None if no last name as some authors have first name only
            & (Name.last_name == name_data.get("last_name"))
        )
    )
    # Returns first match as tuple containing name instance (0) and author instance (1) or None.
    # Should be no duplicate authors due to above check
    existing_author = db.session.execute(name_author_query).first()

    if existing_author:  # Assign author instance from tuple if match found
        author = existing_author[1]  # The author instance

    else:  # Create new name and author if no matching author found
        name = Name(**name_data)  # Validate/deserialize with Name model
        db.session.add(name)
        db.session.flush()

        author = Author(**author_dict, name_id=name.id)
        db.session.add(author)
        db.session.flush()

    return author  # Return existing or new author instance
