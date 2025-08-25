import click
from flask.cli import with_appcontext
from datetime import datetime, timezone  # Make order_date utc timezone aware
from extensions import db
from models import Name, Author, Book, BookAuthor, Address, Customer, Order, OrderItem


@click.command("seed")
@with_appcontext
def seed_data():
    """Seed the database with sample data."""
    # Check if data already exists to prevent duplicates
    if db.session.query(Book).count() > 0:
        click.echo(
            "Database already contains data. Use 'flask drop' first to clear it."
        )
        return

    click.echo("Seeding database with sample data...")

    # Create author names
    author_names = [
        Name(first_name="Brandon", last_name="Sanderson"),  # 1
        Name(first_name="Robert", last_name="Jordan"),  # 2
        Name(first_name="Mark", last_name="Lawrence"),  # 3
        Name(first_name="Patrick", last_name="Rothfuss"),  # 4
        Name(first_name="Terry", last_name="Pratchett"),  # 5
        Name(first_name="Neil", last_name="Gaiman"),  # 6
    ]
    db.session.add_all(author_names)
    db.session.flush()

    # Create authors using the names
    authors = [
        Author(name=author_names[0]),  # Brandon Sanderson
        Author(name=author_names[1]),  # Robert Jordan
        Author(name=author_names[2]),  # Mark Lawrence
        Author(name=author_names[3]),  # Patrick Rothfuss
        Author(name=author_names[4]),  # Terry Pratchett
        Author(name=author_names[5]),  # Neil Gaiman
    ]
    db.session.add_all(authors)
    db.session.flush()

    # Create books
    books = [
        Book(
            isbn="9780765326355",
            series="The Stormlight Archive",
            title="The Way of Kings",
            publication_year=2010,
            price=29.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780765326362",
            series="The Stormlight Archive",
            title="Words of Radiance",
            publication_year=2014,
            price=29.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780765326379",
            series="The Stormlight Archive",
            title="Oathbringer",
            publication_year=2017,
            price=29.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312850098",
            series="The Wheel of Time",
            title="The Eye of the World",
            publication_year=1990,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312851408",
            series="The Wheel of Time",
            title="The Great Hunt",
            publication_year=1990,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312852481",
            series="The Wheel of Time",
            title="The Dragon Reborn",
            publication_year=1991,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312854317",
            series="The Wheel of Time",
            title="The Shadow Rising",
            publication_year=1992,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312854270",
            series="The Wheel of Time",
            title="The Fires of Heaven",
            publication_year=1993,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312854287",
            series="The Wheel of Time",
            title="Lord of Chaos",
            publication_year=1994,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312857677",
            series="The Wheel of Time",
            title="A Crown of Swords",
            publication_year=1996,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312857691",
            series="The Wheel of Time",
            title="The Path of Daggers",
            publication_year=1998,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312864255",
            series="The Wheel of Time",
            title="Winter's Heart",
            publication_year=2000,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312864590",
            series="The Wheel of Time",
            title="Crossroads of Twilight",
            publication_year=2003,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780312873073",
            series="The Wheel of Time",
            title="Knife of Dreams",
            publication_year=2005,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780765302304",
            series="The Wheel of Time",
            title="The Gathering Storm",
            publication_year=2009,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780765325945",
            series="The Wheel of Time",
            title="Towers of Midnight",
            publication_year=2010,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780765325952",
            series="The Wheel of Time",
            title="A Memory of Light",
            publication_year=2013,
            price=19.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780756405892",
            series="The Kingkiller Chronicle",
            title="The Name of the Wind",
            publication_year=2007,
            price=14.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780756407124",
            series="The Kingkiller Chronicle",
            title="The Wise Man's Fear",
            publication_year=2011,
            price=14.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780060853976",
            series=None,
            title="Good Omens: The Nice and Accurate Prophecies of Agnes Nutter, Witch",
            publication_year=1990,
            price=12.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780007423293",
            series="Broken Empire",
            title="Prince of Thorns",
            publication_year=2011,
            price=14.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9781937007478",
            series="Broken Empire",
            title="King of Thorns",
            publication_year=2012,
            price=14.99,
            quantity=10,
            discontinued=False,
        ),
        Book(
            isbn="9780425256855",
            series="Broken Empire",
            title="Emperor of Thorns",
            publication_year=2013,
            price=14.99,
            quantity=10,
            discontinued=False,
        ),
    ]
    db.session.add_all(books)
    db.session.flush()

    # Create book_author relationships
    book_authors = [
        # Brandon Sanderson books
        BookAuthor(book=books[0], author=authors[0]),  # The Way of Kings
        BookAuthor(book=books[1], author=authors[0]),  # Words of Radiance
        BookAuthor(book=books[2], author=authors[0]),  # Oathbringer
        # Robert Jordan books
        BookAuthor(book=books[3], author=authors[1]),  # The Eye of the World
        BookAuthor(book=books[4], author=authors[1]),  # The Great Hunt
        BookAuthor(book=books[5], author=authors[1]),  # The Dragon Reborn
        BookAuthor(book=books[6], author=authors[1]),  # The Shadow Rising
        BookAuthor(book=books[7], author=authors[1]),  # The Fires of Heaven
        BookAuthor(book=books[8], author=authors[1]),  # Lord of Chaos
        BookAuthor(book=books[9], author=authors[1]),  # A Crown of Swords
        BookAuthor(book=books[10], author=authors[1]),  # The Path of Daggers
        BookAuthor(book=books[11], author=authors[1]),  # Winter's Heart
        BookAuthor(book=books[12], author=authors[1]),  # Crossroads of Twilight
        BookAuthor(book=books[13], author=authors[1]),  # Knife of Dreams
        # Brandon Sanderson & Robert Jordan collaborations
        BookAuthor(book=books[14], author=authors[1]),  # The Gathering Storm - Jordan
        BookAuthor(
            book=books[14], author=authors[0]
        ),  # The Gathering Storm - Sanderson
        BookAuthor(book=books[15], author=authors[1]),  # Towers of Midnight - Jordan
        BookAuthor(book=books[15], author=authors[0]),  # Towers of Midnight - Sanderson
        BookAuthor(book=books[16], author=authors[1]),  # A Memory of Light - Jordan
        BookAuthor(book=books[16], author=authors[0]),  # A Memory of Light - Sanderson
        # Patrick Rothfuss books
        BookAuthor(book=books[17], author=authors[3]),  # The Name of the Wind
        BookAuthor(book=books[18], author=authors[3]),  # The Wise Man's Fear
        # Neil Gaiman & Terry Pratchett collaboration
        BookAuthor(book=books[19], author=authors[4]),  # Good Omens - Pratchett
        BookAuthor(book=books[19], author=authors[5]),  # Good Omens - Gaiman
        # Mark Lawrence books
        BookAuthor(book=books[20], author=authors[2]),  # Prince of Thorns
        BookAuthor(book=books[21], author=authors[2]),  # King of Thorns
        BookAuthor(book=books[22], author=authors[2]),  # Emperor of Thorns
    ]
    db.session.add_all(book_authors)
    db.session.flush()

    # Create addresses
    addresses = [
        Address(
            country_code="US",
            state_code="CA",
            city="San Francisco",
            street="123 Market St",
            postcode="94103",
        ),
        Address(
            country_code="US",
            state_code="NY",
            city="New York",
            street="456 Broadway",
            postcode="10001",
        ),
        Address(
            country_code="GB",
            state_code="ENG",
            city="London",
            street="789 Oxford St",
            postcode="W1D2LT",
        ),
        Address(
            country_code="CA",
            state_code="ON",
            city="Toronto",
            street="101 Queen St W",
            postcode="M5H2N2",
        ),
        Address(
            country_code="AU",
            state_code="NSW",
            city="Sydney",
            street="202 George St",
            postcode="2000",
        ),
        Address(
            country_code="DE",
            state_code="BE",
            city="Berlin",
            street="303 Unter den Linden",
            postcode="10117",
        ),
    ]
    db.session.add_all(addresses)
    db.session.flush()

    # Create customer names
    customer_names = [
        Name(first_name="Alice", last_name="Smith"),
        Name(first_name="Bob", last_name="Johnson"),
        Name(first_name="Charlie", last_name="Brown"),
        Name(first_name="David", last_name="Williams"),
        Name(first_name="Eve", last_name="Davis"),
        Name(first_name="Frank", last_name="Miller"),
        Name(first_name="Grace", last_name="Wilson"),
    ]
    db.session.add_all(customer_names)
    db.session.flush()

    # Create customers with VALID E.164 phone numbers and emails
    customers = [
        Customer(
            name=customer_names[0],
            email="alice.smith@example.com",
            phone="+61412345678",  # Australian test number
            address=addresses[0],
        ),
        Customer(
            name=customer_names[1],
            email="bob.johnson@example.com",
            phone=None,
            address=addresses[1],
        ),
        Customer(
            name=customer_names[2],
            email="charlie.brown@example.com",
            phone="+61412345679",
            address=addresses[2],
        ),
        Customer(
            name=customer_names[3],
            email="david.williams@example.com",
            phone="+61412345671",
            address=addresses[3],
        ),
        Customer(
            name=customer_names[4],
            email="eve.davis@example.com",
            phone="+61412345672",
            address=addresses[4],
        ),
        Customer(
            name=customer_names[5],
            email="frank.miller@example.com",
            phone=None,
            address=addresses[5],
        ),
        Customer(
            name=customer_names[6],
            email="grace.wilson@example.com",
            phone="+61412345673",
            address=addresses[4],
        ),
    ]
    db.session.add_all(customers)
    db.session.flush()

    # Create orders with empty price_total initially
    orders = [
        Order(
            customer=customers[0],
            order_date=datetime(2025, 2, 1, 10, 15, 30, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[0],
            order_date=datetime(2025, 2, 1, 11, 10, 20, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[1],
            order_date=datetime(2025, 2, 2, 11, 20, 45, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[2],
            order_date=datetime(2025, 4, 3, 12, 25, 50, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[3],
            order_date=datetime(2025, 5, 4, 13, 30, 55, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[4],
            order_date=datetime(2025, 6, 5, 14, 35, 0, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[5],
            order_date=datetime(2025, 6, 6, 15, 40, 5, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[5],
            order_date=datetime(2025, 6, 7, 16, 45, 10, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[3],
            order_date=datetime(2025, 7, 3, 17, 50, 15, tzinfo=timezone.utc),
            price_total=0.0,
        ),
        Order(
            customer=customers[2],
            order_date=datetime(2025, 7, 4, 18, 55, 20, tzinfo=timezone.utc),
            price_total=0.0,
        ),
    ]
    db.session.add_all(orders)
    db.session.flush()

    # Define order items and calculate price totals
    order_item_data = [
        # Order 1: Alice
        (0, 0, 1),  # The Way of Kings
        (0, 1, 1),  # Words of Radiance
        # Order 2: Alice
        (1, 3, 1),  # The Eye of the World
        (1, 17, 1),  # The Name of the Wind
        (1, 19, 1),  # Good Omens
        # Order 3: Bob
        (2, 3, 2),  # 2x The Eye of the World
        (2, 4, 1),  # The Great Hunt
        (2, 5, 1),  # The Dragon Reborn
        # Order 4: Charlie
        (3, 17, 1),  # The Name of the Wind
        # Order 5: David
        (4, 0, 1),  # The Way of Kings
        (4, 19, 2),  # 2x Good Omens
        # Order 6: Eve
        (5, 21, 1),  # King of Thorns
        # Order 7: Frank
        (6, 0, 1),  # The Way of Kings
        (6, 1, 1),  # Words of Radiance
        (6, 2, 1),  # Oathbringer
        # Order 8: Frank
        (7, 14, 1),  # The Gathering Storm
        (7, 15, 1),  # Towers of Midnight
        (7, 16, 1),  # A Memory of Light
        # Order 9: David
        (8, 18, 3),  # 3x The Wise Man's Fear
        # Order 10: Charlie
        (9, 20, 1),  # Prince of Thorns
        (9, 21, 1),  # King of Thorns
        (9, 22, 1),  # Emperor of Thorns
    ]

    # Create OrderItems and calculate price totals
    for order_idx, book_idx, quantity in order_item_data:
        order = orders[order_idx]
        book = books[book_idx]

        order_item = OrderItem(order=order, book=book, quantity=quantity)
        db.session.add(order_item)

        # Update the order's price_total
        order.price_total += float(book.price * quantity)

    # Commit all changes to the database
    db.session.commit()

    # Print summary of seeded data
    click.echo(f"Seeded {len(books)} books")
    click.echo(f"Seeded {len(authors)} authors")
    click.echo(f"Seeded {len(customers)} customers")
    click.echo(f"Seeded {len(orders)} orders")
    click.echo(f"Seeded {len(order_item_data)} order items")
    click.echo("Database seeding complete!")
