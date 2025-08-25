import click
from flask.cli import with_appcontext
from extensions import db


@click.command("create")
@with_appcontext
def create_table() -> None:
    """Create database tables."""
    db.create_all()
    click.echo("Database tables created.")
