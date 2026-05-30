"""Flask API wrapper for the grocery suggestion engine with DB persistence."""

from flask import Flask, request, jsonify
from app import build_association_rules, suggest_items
from db import SessionLocal, init_db
from models import Product, Trip

INITIAL_HISTORY = [
    ["milk", "bread", "eggs", "apples"],
    ["milk", "bread", "cereal"],
    ["eggs", "bread", "butter"],
    ["milk", "bread", "eggs", "butter"],
    ["milk", "cereal", "apples"],
    ["eggs", "butter"],
    ["milk", "bread", "eggs"],
]


app = Flask(__name__)


def get_grocery_history_from_db(session):
    trips = session.query(Trip).order_by(Trip.id).all()
    history = [[p.name for p in trip.products] for trip in trips]
    return history


def seed_db_if_empty(session):
    # If there are no trips, seed from INITIAL_HISTORY
    if session.query(Trip).first() is not None:
        return

    for trip_items in INITIAL_HISTORY:
        trip = Trip()
        for name in trip_items:
            name = name.strip().lower()
            prod = session.query(Product).filter_by(name=name).first()
            if prod is None:
                prod = Product(name=name)
            trip.products.append(prod)
        session.add(trip)
    session.commit()


def setup_db():
    init_db()
    db = SessionLocal()
    try:
        seed_db_if_empty(db)
    finally:
        db.close()


# Initialize the DB and seed example history when the app loads.
# This avoids Flask 3 compatibility issues with the removed before_first_request decorator.
setup_db()


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


@app.route("/suggest", methods=["POST"])
def get_suggestions():
    try:
        data = request.get_json()
        if not data or "current_items" not in data:
            return jsonify({"error": "Missing 'current_items' in request"}), 400

        current_items = set(item.strip().lower() for item in data["current_items"] if item.strip())
        if not current_items:
            return jsonify({"error": "'current_items' cannot be empty"}), 400

        min_support = data.get("min_support", 0.3)
        min_lift = data.get("min_lift", 1.0)
        top_n = data.get("top_n", 5)

        # Validate parameters
        if not (0 < min_support <= 1):
            return jsonify({"error": "min_support must be between 0 and 1"}), 400
        if min_lift < 0:
            return jsonify({"error": "min_lift must be non-negative"}), 400
        if top_n < 1:
            return jsonify({"error": "top_n must be at least 1"}), 400

        db = SessionLocal()
        try:
            grocery_history = get_grocery_history_from_db(db)
        finally:
            db.close()

        rules = build_association_rules(
            grocery_history,
            min_support=min_support,
            metric="lift",
            min_threshold=min_lift,
        )

        if rules.empty:
            return jsonify({
                "current_items": sorted(current_items),
                "suggestions": [],
                "message": "No association rules found with the given parameters"
            }), 200

        suggestions = suggest_items(current_items, rules, top_n=top_n)

        return jsonify({
            "current_items": sorted(current_items),
            "suggestions": suggestions,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def get_history():
    db = SessionLocal()
    try:
        history = get_grocery_history_from_db(db)
    finally:
        db.close()
    return jsonify({"history": history}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
