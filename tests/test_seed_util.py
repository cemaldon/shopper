"""Unit tests for seed_util module."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shopper.db import Base
from shopper.models import Product, Trip
from shopper.seed_util import INITIAL_HISTORY, seed_db_if_empty


@pytest.fixture
def test_db_session():
    """Create an in-memory SQLite DB for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestSeedUtilFunctions:
    """Test seeding utility functions."""

    def test_initial_history_not_empty(self):
        """Verify INITIAL_HISTORY has expected trips."""
        assert len(INITIAL_HISTORY) == 7
        assert INITIAL_HISTORY[0] == ["milk", "bread", "eggs", "apples"]

    def test_seed_db_if_empty_on_empty_db(self, test_db_session):
        """Seed should run on an empty database."""
        # Verify DB is empty before seeding
        assert test_db_session.query(Trip).count() == 0
        assert test_db_session.query(Product).count() == 0

        # Seed the database
        seed_db_if_empty(test_db_session)

        # Verify data was added
        assert test_db_session.query(Trip).count() == 7
        assert test_db_session.query(Product).count() == 6

    def test_seed_db_if_empty_skips_on_existing_trips(self, test_db_session):
        """Seed should skip when trips already exist."""
        # Add a single trip to the DB
        trip = Trip()
        test_db_session.add(trip)
        test_db_session.commit()

        # Try to seed (should skip)
        seed_db_if_empty(test_db_session)

        # Verify only the one trip exists (no more were added)
        assert test_db_session.query(Trip).count() == 1

    def test_seeded_products_are_correct(self, test_db_session):
        """Verify all expected products are created during seeding."""
        seed_db_if_empty(test_db_session)

        products = {p.name for p in test_db_session.query(Product).all()}
        expected = {"milk", "bread", "eggs", "apples", "cereal", "butter"}

        assert products == expected

    def test_seeded_trips_have_products(self, test_db_session):
        """Verify each trip has associated products after seeding."""
        seed_db_if_empty(test_db_session)

        trips = test_db_session.query(Trip).all()
        assert len(trips) == 7

        for i, trip in enumerate(trips):
            products = trip.products
            assert len(products) > 0, f"Trip {i} has no products"

            # Verify product names match INITIAL_HISTORY
            product_names = {p.name for p in products}
            expected_names = {name.strip().lower() for name in INITIAL_HISTORY[i]}
            assert product_names == expected_names, f"Trip {i} product mismatch"

    def test_trip_product_associations_are_created(self, test_db_session):
        """Verify trip_products associations are created."""
        seed_db_if_empty(test_db_session)

        # Total associations should be the sum of products in all trips
        expected_associations = sum(len(trip) for trip in INITIAL_HISTORY)
        actual_associations = test_db_session.query(Trip).count()  # Just checking trips were created
        
        # Get actual association count via raw query
        result = test_db_session.execute("SELECT count(*) FROM trip_products").scalar()
        assert result == expected_associations, f"Expected {expected_associations} associations, got {result}"

    def test_seeding_commits_changes(self, test_db_session):
        """Verify seeding commits data to the session."""
        seed_db_if_empty(test_db_session)

        # Refresh session to ensure committed data persists
        test_db_session.expunge_all()

        # Re-query to ensure data persists
        trips_count = test_db_session.query(Trip).count()
        assert trips_count == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
