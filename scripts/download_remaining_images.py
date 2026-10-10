"""Download Unsplash images for categories that don't have any yet (Beauty, Home, Books)."""

import hashlib
import json
import os
import time
import urllib.request
import urllib.parse

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricewise_data.csv")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "products")
UNSPLASH_ACCESS_KEY = "4EDOGqpGDOlRgsxLQU_cW4kkTmp57G2CD_uMpGONdzI"
UNSPLASH_API_BASE = "https://api.unsplash.com"

CATEGORY_QUERIES = {
    "Beauty": [
        "beauty cosmetics", "skincare product", "makeup",
        "perfume fragrance", "hair care", "beauty salon",
    ],
    "Home": [
        "home decor", "furniture chair", "kitchen appliance",
        "home lighting", "bedroom interior", "home garden",
    ],
    "Books": [
        "books library", "book reading", "notebook stationery",
        "book stack", "bookstore", "reading book",
    ],
}


def _unsplash_search(query: str, per_page: int = 20) -> list:
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": per_page,
        "client_id": UNSPLASH_ACCESS_KEY,
    })
    url = f"{UNSPLASH_API_BASE}/search/photos?{params}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            results = data.get("results", [])
            urls = []
            for r in results:
                img_url = r.get("urls", {}).get("regular") or r.get("urls", {}).get("small")
                if img_url:
                    urls.append(img_url)
            return urls
    except Exception as e:
        print(f"  Search failed for '{query}': {e}")
        return []


def _download_image(url: str, save_path: str, timeout: int = 15) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PriceWise/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            if len(data) < 500:
                return False
            with open(save_path, "wb") as f:
                f.write(data)
            return True
    except Exception:
        return False


def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    # Check which categories already have images
    existing_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]
    existing_cats = set()
    for f in existing_files:
        parts = f.split("_", 1)
        if len(parts) == 2:
            existing_cats.add(parts[0])

    print(f"Existing categories: {existing_cats}")

    # Only download for missing categories
    missing_cats = {k: v for k, v in CATEGORY_QUERIES.items() if k not in existing_cats}
    print(f"Missing categories: {list(missing_cats.keys())}")

    total_downloaded = 0
    api_calls = 0

    for category, queries in missing_cats.items():
        print(f"\nDownloading for {category}...")
        for query in queries:
            if api_calls >= 45:
                print(f"  Reached API limit ({api_calls} calls).")
                break

            print(f"  Searching: '{query}'...")
            api_calls += 1
            urls = _unsplash_search(query, per_page=20)

            for url in urls:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
                filename = f"{category.replace(' ', '_')}_{url_hash}.jpg"
                save_path = os.path.join(IMAGE_DIR, filename)

                if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                    continue

                if _download_image(url, save_path):
                    total_downloaded += 1

            time.sleep(1)

        print(f"  Downloaded {total_downloaded} new images so far")

    print(f"\nTotal new downloads: {total_downloaded}")
    print(f"API calls used: {api_calls}")

    # Now re-assign all images
    print("\nRe-assigning images to CSV...")

    all_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]
    pool_by_category = {}
    for f in all_files:
        parts = f.split("_", 1)
        if len(parts) == 2:
            cat = parts[0]
            full_path = os.path.join("assets", "products", f)
            if cat not in pool_by_category:
                pool_by_category[cat] = []
            pool_by_category[cat].append(full_path)

    for cat, paths in pool_by_category.items():
        print(f"  {cat}: {len(paths)} images")

    df = pd.read_csv(DATA_PATH)
    image_paths = []
    fallback_count = 0

    for idx, row in df.iterrows():
        category = str(row.get("category", ""))
        product_name = str(row.get("product_name", f"product_{idx}"))

        pool = pool_by_category.get(category, [])
        if not pool:
            existing = row.get("image_data", "")
            if isinstance(existing, str) and existing.startswith("data:"):
                image_paths.append(existing)
            else:
                image_paths.append("")
            fallback_count += 1
            continue

        name_hash = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
        selected_path = pool[name_hash % len(pool)]
        image_paths.append(selected_path)

    df["image_data"] = image_paths
    df.to_csv(DATA_PATH, index=False)

    print(f"\nDone! Real images: {len(df) - fallback_count}, SVG fallbacks: {fallback_count}")


if __name__ == "__main__":
    main()
