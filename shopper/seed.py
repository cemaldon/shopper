"""CLI script to initialize the DB and seed initial data via SQLAlchemy.

Run:

    python -m shopper.seed [options]

Or after installation:

    python seed.py [options]

Available options:
    --force           Delete existing trips before seeding
    --full            With --force, also delete products (full reset)
    --drop            Drop all tables and recreate (destructive)
    --db-url <URL>    Override DATABASE_URL for this run
    --yes             Skip confirmation prompts for destructive actions
    --count-only      Show counts and exit without seeding
"""
import argparse
import logging
import os
import sys

from .seed_util import seed_db_if_empty

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(description="Seed the shopper DB (CLI)")
    p.add_argument("--force", action="store_true", help="Delete existing trips before seeding")
    p.add_argument(
        "--full",
        action="store_true",
        help="When used with --force, also delete products (full reset)",
    )
    p.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables and recreate them before seeding (destructive)",
    )
    p.add_argument("--db-url", type=str, help="Override DATABASE_URL for this run")
    p.add_argument("--yes", action="store_true", help="Skip confirmation prompts for destructive actions")
    p.add_argument("--count-only", action="store_true", help="Show counts and exit without seeding")
    return p.parse_args()


def main(argv=None):
    args = parse_args() if argv is None else parse_args()

    # Allow temporary override of DATABASE_URL before importing db
    db_url = args.db_url
    if db_url:
        os.environ["DATABASE_URL"] = db_url

    try:
        from .db import init_db, SessionLocal, Base, engine
    except Exception:
        logger.exception("Failed to import DB modules. Ensure dependencies are installed.")
        raise

    logger.info("Initializing DB (CLI)...")
    init_db()

    if args.drop:
        if not args.yes:
            confirm = input("Drop all tables and recreate? This is destructive (y/N): ")
            if confirm.lower() != "y":
                logger.info("Aborting per user input.")
                return
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        init_db()

    session = SessionLocal()
    try:
        if args.count_only:
            # report counts and exit
            try:
                trips = session.execute("SELECT count(*) FROM trips").scalar()
                products = session.execute("SELECT count(*) FROM products").scalar()
                assoc = session.execute("SELECT count(*) FROM trip_products").scalar()
                print(f"trips: {trips}")
                print(f"products: {products}")
                print(f"trip_products: {assoc}")
            except Exception as e:
                logger.error("Failed to query counts: %s", e)
            return

        if args.force:
            if not args.yes:
                confirm = input("This will remove existing trips (and products with --full). Continue? (y/N): ")
                if confirm.lower() != "y":
                    logger.info("Aborting per user input.")
                    return
            logger.info("Removing existing trips...")
            session.execute("DELETE FROM trip_products")
            session.execute("DELETE FROM trips")
            if args.full:
                logger.info("Removing products (full reset)...")
                session.execute("DELETE FROM products")
            session.commit()

        # Run the standard seeding routine (it will skip if trips exist and --force not used)
        seed_db_if_empty(session)

    finally:
        session.close()


if __name__ == "__main__":
    main()
