"""Import all controller blueprints as a list to be registered in main.py"""

from .addresses_controllers import addresses
from .customers_controllers import customers
from .books_controllers import books
from .orders_controllers import orders

controller_blueprints = [addresses, customers, books, orders]
