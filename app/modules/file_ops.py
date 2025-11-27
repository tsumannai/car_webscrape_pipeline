import json
import os

def append_product_list(path: str, new_products: list):
    # If file exists, load data — else create new list
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
            if not isinstance(existing, list):
                raise ValueError("JSON file must contain a list.")
    else:
        existing = []

    # Append new products
    existing.extend(new_products)

    # Write back updated list
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
