"""Shared seeding utilities for the shopper app.

Expose `INITIAL_HISTORY` and `seed_db_if_empty(session)` so the API and CLI
can reuse the same seeding logic without duplicating code or importing the
Flask app at module import time.
"""
import logging
from models import Product, Trip

logger = logging.getLogger(__name__)

INITIAL_HISTORY = [
    ["milk", "bread", "eggs", "apples"],
    ["milk", "bread", "cereal"],
    ["eggs", "bread", "butter"],
    ["milk", "bread", "eggs", "butter"],
    ["milk", "cereal", "apples"],
    ["eggs", "butter"],
    ["milk", "bread", "eggs"],
]


def seed_db_if_empty(session):
    """Seed the DB from INITIAL_HISTORY if there are no trips.

    Uses the provided SQLAlchemy `session` and commits when finished.
    """
    if session.query(Trip).first() is not None:
        logger.info("Database already has trips; skipping seeding.")
        return

    logger.info("Seeding database with %d trips from INITIAL_HISTORY.", len(INITIAL_HISTORY))
    product_count_before = session.query(Product).count()
    trips_added = 0

    for trip_items in INITIAL_HISTORY:
        trip = Trip()
        for name in trip_items:
            name = name.strip().lower()
            prod = session.query(Product).filter_by(name=name).first()
            if prod is None:
                prod = Product(name=name)
                session.add(prod)
                session.flush()
            trip.products.append(prod)
        session.add(trip)
        trips_added += 1

    session.commit()
    product_count_after = session.query(Product).count()
    logger.info(
        "Seeding complete: %d trips added, %d new products added.",
        trips_added,
        product_count_after - product_count_before,
    )
