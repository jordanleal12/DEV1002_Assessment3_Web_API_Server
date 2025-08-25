from .create import create_table
from .seed import seed_data
from .drop import drop_table

registerable_cli_commands = [create_table, seed_data, drop_table]
