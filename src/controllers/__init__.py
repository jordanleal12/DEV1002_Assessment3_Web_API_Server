"""Import all controller blueprints as a list to be registered in main.py"""

from .addresses_controllers import addresses

controller_blueprints = [
    addresses,
]
