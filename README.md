BASH

pip install --upgrade pip

pip install -r requirements.txt

Database & Migrations
---------------------

This project now uses SQLAlchemy for persistence with Alembic for schema migrations. By default it uses a local SQLite file `shopper.db`.

Install dependencies and run the migration to create tables:

```bash
pip install -r requirements.txt
export PYTHONPATH=.
alembic upgrade head
```

If Alembic has trouble importing the local app modules, make sure `PYTHONPATH=.` is set before running `alembic upgrade head`.

You can override the DB location with `DATABASE_URL`, e.g. `export DATABASE_URL="sqlite:////tmp/shopper.db"`.

Run the Flask API:

```bash
python api.py
```

On first run the app will seed initial example history into the database if empty.

