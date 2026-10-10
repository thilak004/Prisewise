"""Assign already-downloaded Unsplash images to all products in the CSV.

Uses the 204 images already in assets/products/ and assigns them
deterministically by category. No new API calls needed.
"""

import hashlib
import os

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricewise_data.csv")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "products")


def main():
    # Get all downloaded images grouped by category
    all_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]

    # Group by category prefix
    pool_by_category = {}
    generic_pool = []

    for f in all_files:
        # Files are named like "Electronics_abc123.jpg" or "generic_abc123.jpg"
        parts = f.split("_", 1)
        if len(parts) == 2:
            cat = parts[0]
            full_path = os.path.join("assets", "products", f)
            if cat.lower() == "generic":
                generic_pool.append(full_path)
            else:
                if cat not in pool_by_category:
                    pool_by_category[cat] = []
                pool_by_category[cat].append(full_path)

    print(f"Found {len(all_files)} images")
    print(f"Categories: {list(pool_by_category.keys())}")
    for cat, paths in pool_by_category.items():
        print(f"  {cat}: {len(paths)} images")
    print(f"  Generic: {len(generic_pool)} images")

    # Load CSV
    df = pd.read_csv(DATA_PATH)
    print(f"\nLoaded {len(df)} rows")

    # Assign images deterministically
    image_paths = []
    fallback_count = 0

    for idx, row in df.iterrows():
        category = str(row.get("category", ""))
        product_name = str(row.get("product_name", f"product_{idx}"))

        # Find the right pool
        pool = pool_by_category.get(category, [])
        if not pool:
            pool = generic_pool

        if not pool:
            # No images at all, keep existing SVG
            existing = row.get("image_data", "")
            if isinstance(existing, str) and existing.startswith("data:"):
                image_paths.append(existing)
            else:
                image_paths.append("")
            fallback_count += 1
            continue

        # Deterministic assignment based on product name hash
        name_hash = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
        selected_path = pool[name_hash % len(pool)]
        image_paths.append(selected_path)

    df["image_data"] = image_paths
    df.to_csv(DATA_PATH, index=False)

    print(f"\nDone! Assigned images to {len(df)} products")
    print(f"Real image assignments: {len(df) - fallback_count}")
    print(f"SVG fallbacks: {fallback_count}")


if __name__ == "__main__":
    main()
