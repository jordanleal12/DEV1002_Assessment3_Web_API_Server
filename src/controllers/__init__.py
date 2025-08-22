"""Import all controller blueprints as a list to be registered in main.py"""

from .addresses_controllers import addresses
from .customers_controllers import customers

controller_blueprints = [addresses, customers]
