# Tools & CLI Reference

This document outlines the key tools and CLI utilities available in the shopper project for database management, seeding, and testing.

## Seeding the Database

### Quick Start (Standard)

If the database is empty, seeding happens automatically when the Flask app starts. To manually seed:

```bash
# Via module
python -m shopper.seed

# Via installed console script (after `pip install -e .`)
shopper-seed

# Via legacy script (no dependencies required)
python seed_db.py
```

### CLI Flags

The seeding CLI supports the following flags for flexible database management:

#### `--force`
Remove existing trips before seeding (forces reseed even if trips exist).

```bash
python -m shopper.seed --force
```

#### `--full`
Used with `--force`, also removes products (full database reset).

```bash
python -m shopper.seed --force --full
```

#### `--drop`
Drop all tables and recreate them before seeding (most destructive).

```bash
python -m shopper.seed --drop
```

#### `--db-url <URL>`
Override `DATABASE_URL` for this run only (useful for testing).

```bash
python -m shopper.seed --db-url sqlite:////tmp/test.db
```

#### `--yes`
Skip confirmation prompts for destructive actions (useful for automation).

```bash
python -m shopper.seed --drop --yes
```

#### `--count-only`
Show row counts for trips, products, and associations without seeding.

```bash
python -m shopper.seed --count-only
```

### Combined Examples

Force reseed with products (non-interactive):
```bash
python -m shopper.seed --force --full --yes
```

Full reset to a fresh state:
```bash
python -m shopper.seed --drop --force --yes
```

Test with a temporary database:
```bash
python -m shopper.seed --db-url sqlite:////tmp/test.db --drop --yes
```

## Environment Variables

### `RESEED_ON_STARTUP`

Automatically reseed the database when the Flask app starts. Set to `1`, `true`, or `yes`:

```bash
# Reseed and start Flask
RESEED_ON_STARTUP=1 python api.py

# In Docker or container startup scripts
export RESEED_ON_STARTUP=true
python api.py
```

This is useful for:
- Development: Fresh state on every restart
- Container deployments: Reset database on container startup
- Testing: Ensure consistent initial state

## Installation & Package Setup

### Development Installation

Install the package in editable mode to enable the `shopper-seed` console script:

```bash
pip install -e .
```

This makes available:
- `shopper-seed` command (instead of `python -m shopper.seed`)
- All dependencies from `requirements.txt`
- Package imports as `from shopper import ...`

### Console Script Usage

After installation:

```bash
# Equivalent to `python -m shopper.seed`
shopper-seed --force --yes

# Check counts
shopper-seed --count-only
```

## Testing

### Run All Tests

```bash
pytest tests/
```

### Run Seeding Tests Only

```bash
pytest tests/test_seed_util.py -v
```

### Run Specific Test

```bash
pytest tests/test_seed_util.py::TestSeedUtilFunctions::test_seed_db_if_empty_on_empty_db -v
```

Tests verify:
- Empty database seeding works correctly
- Seeding skips when trips already exist
- All expected products are created
- Trip-product associations are valid
- Data commits persist

## Database

### Default Location

The SQLite database is stored at the project root: `/workspaces/shopper/shopper.db`

### Override Default

```bash
# Use a different database for this run
export DATABASE_URL="sqlite:////tmp/custom.db"
python api.py
```

### Manual Inspection

Use the `--count-only` flag:

```bash
python -m shopper.seed --count-only
```

Or query directly with `sqlite3`:

```bash
sqlite3 shopper.db "SELECT count(*) FROM trips;"
```

## Logging

The seeding utilities include INFO-level logging. Set `PYTHONUNBUFFERED=1` to see real-time output:

```bash
PYTHONUNBUFFERED=1 python -m shopper.seed
```

Output example:
```
INFO:shopper.seed_util:Seeding database with 7 trips from INITIAL_HISTORY.
INFO:shopper.seed_util:Seeding complete: 7 trips added, 6 new products added.
```

## Quick Reference

| Task | Command |
|------|---------|
| Seed (if empty) | `python -m shopper.seed` |
| Force reseed | `python -m shopper.seed --force --yes` |
| Full reset | `python -m shopper.seed --drop --yes` |
| Check counts | `python -m shopper.seed --count-only` |
| Run tests | `pytest tests/` |
| Reseed on Flask startup | `RESEED_ON_STARTUP=1 python api.py` |
| Install package | `pip install -e .` |
| Use console script | `shopper-seed [options]` |
