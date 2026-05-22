import argparse
import json
from typing import Dict, List, Set

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def encode_history(grocery_history: List[List[str]]) -> pd.DataFrame:
    """Convert shopping history into a one-hot encoded DataFrame."""
    all_items = sorted({item for week in grocery_history for item in week})
    encoded_rows = [
        {item: item in week for item in all_items}
        for week in grocery_history
    ]
    return pd.DataFrame(encoded_rows, dtype=bool)


def build_association_rules(
    grocery_history: List[List[str]],
    min_support: float = 0.3,
    metric: str = "lift",
    min_threshold: float = 1.0,
) -> pd.DataFrame:
    """Build association rules from past grocery trips."""
    df = encode_history(grocery_history)
    frequent_itemsets = apriori(df, min_support=min_support, use_colnames=True)
    if frequent_itemsets.empty:
        return pd.DataFrame()
    rules = association_rules(frequent_itemsets, metric=metric, min_threshold=min_threshold)
    return rules.sort_values(["lift", "confidence"], ascending=False)


def suggest_items(current_list: Set[str], rules: pd.DataFrame, top_n: int = 5) -> List[Dict[str, object]]:
    """Return top suggestions based on association rules for the current list."""
    suggestions: Dict[str, Dict[str, object]] = {}

    for _, row in rules.iterrows():
        antecedents = set(row["antecedents"])
        consequents = set(row["consequents"])
        if antecedents.issubset(current_list):
            for item in consequents - current_list:
                score = row["confidence"] * row["lift"]
                existing = suggestions.get(item)
                if existing is None or score > existing["score"]:
                    suggestions[item] = {
                        "item": item,
                        "confidence": float(row["confidence"]),
                        "lift": float(row["lift"]),
                        "support": float(row["support"]),
                        "matched_antecedent": sorted(antecedents),
                        "score": score,
                    }

    sorted_suggestions = sorted(
        suggestions.values(),
        key=lambda row: (row["score"], row["confidence"], row["lift"]),
        reverse=True,
    )
    return sorted_suggestions[:top_n]


def print_suggestions(current_list: Set[str], suggestions: List[Dict[str, object]]) -> None:
    if not suggestions:
        print("No suggestions found for the current list.")
        return

    print("--- AI Suggestions ---")
    for suggestion in suggestions:
        item = suggestion["item"]
        confidence_pct = suggestion["confidence"] * 100
        lift = suggestion["lift"]
        matched = suggestion["matched_antecedent"]
        print(
            f"Based on buying {matched}, you might have forgotten: {item} "
            f"({confidence_pct:.1f}% confidence, lift={lift:.2f})"
        )


def main() -> None:
    grocery_history = [
        ["milk", "bread", "eggs", "apples"],
        ["milk", "bread", "cereal"],
        ["eggs", "bread", "butter"],
        ["milk", "bread", "eggs", "butter"],
        ["milk", "cereal", "apples"],
        ["eggs", "butter"],
        ["milk", "bread", "eggs"],
    ]

    parser = argparse.ArgumentParser(
        description="Suggest grocery items using association rules from past shopping history."
    )
    parser.add_argument(
        "--current",
        type=str,
        default="milk,eggs",
        help="Comma-separated current list items, e.g. milk,eggs",
    )
    parser.add_argument(
        "--min-support",
        type=float,
        default=0.3,
        help="Minimum support threshold for frequent itemsets.",
    )
    parser.add_argument(
        "--min-lift",
        type=float,
        default=1.0,
        help="Minimum lift threshold for association rules.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of suggested items to display.",
    )
    args = parser.parse_args()

    current_list = {item.strip().lower() for item in args.current.split(",") if item.strip()}
    rules = build_association_rules(
        grocery_history,
        min_support=args.min_support,
        metric="lift",
        min_threshold=args.min_lift,
    )

    print(f"Current List: {sorted(current_list)}\n")
    if rules.empty:
        print("No association rules were generated from the available history.")
        return

    suggestions = suggest_items(current_list, rules, top_n=args.top_n)
    print_suggestions(current_list, suggestions)

    print("\nHistory used for training:")
    print(json.dumps(grocery_history, indent=2))


if __name__ == "__main__":
    main()
