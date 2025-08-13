"""Model for creating Address instances with model level validation."""

from extensions import db


class Address(db.Model):
    """Model for storing addresses of customers."""

    __tablename__ = "addresses"
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False)  # Enforces max length of 2
    state_code = db.Column(db.String(3), nullable=False)  # Enforces max length of 3
    city = db.Column(db.String(50))  # Optional as not all addresses have city
    street = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(10), nullable=False)  # Max length of postcodes is 10
