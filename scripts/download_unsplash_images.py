"""Download real product images from Unsplash API for all 1,500 products.

Strategy (to stay within 50 req/hour free tier):
1. Search Unsplash by category + product keywords (~20 searches)
2. Build a pool of real product image URLs
3. Download images and cache locally in assets/products/
4. Assign images to products deterministically (hash-based)
5. Update CSV with local file paths
"""

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

# Search queries per category to build image pools
CATEGORY_QUERIES = {
    "Electronics": [
        "electronics gadget", "smartphone", "laptop computer",
        "headphones audio", "camera tech", "tablet device",
    ],
    "Fashion": [
        "fashion clothing", "t-shirt apparel", "jeans denim",
        "shoes sneakers", "watch accessory", "jacket coat",
    ],
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

# Generic fallback queries
GENERIC_QUERIES = [
    "product", "shopping", "ecommerce", "retail store",
    "online shopping", "product photo", "commercial product",
]


def _unsplash_search(query: str, per_page: int = 30) -> list:
    """Search Unsplash and return list of image URLs."""
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
    """Download an image from URL to local path."""
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

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, {df['product_name'].nunique()} unique products")
    print(f"Categories: {df['category'].unique().tolist()}")

    # Step 1: Build image pool by searching Unsplash
    image_pool = {}  # category -> list of local file paths
    total_downloaded = 0
    api_calls = 0

    all_categories = df["category"].dropna().unique().tolist()

    for category in all_categories:
        cat_lower = category.lower()
        queries = CATEGORY_QUERIES.get(category, CATEGORY_QUERIES.get(cat_lower, GENERIC_QUERIES))

        image_pool[category] = []

        for query in queries:
            if api_calls >= 45:  # Stay within 50/hour limit
                print(f"  Reached API limit ({api_calls} calls). Stopping searches.")
                break

            print(f"  Searching: '{query}' for {category}...")
            api_calls += 1
            urls = _unsplash_search(query, per_page=20)

            for url in urls:
                # Create filename from URL hash
                url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
                filename = f"{category.replace(' ', '_')}_{url_hash}.jpg"
                save_path = os.path.join(IMAGE_DIR, filename)

                if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                    image_pool[category].append(save_path)
                    continue

                if _download_image(url, save_path):
                    image_pool[category].append(save_path)
                    total_downloaded += 1

            time.sleep(1)  # Rate limit

        print(f"  {category}: {len(image_pool[category])} images in pool")

    # Also add generic queries as fallback
    print("\nBuilding generic fallback pool...")
    generic_pool = []
    for query in GENERIC_QUERIES[:3]:
        if api_calls >= 48:
            break
        api_calls += 1
        urls = _unsplash_search(query, per_page=15)
        for url in urls:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filename = f"generic_{url_hash}.jpg"
            save_path = os.path.join(IMAGE_DIR, filename)
            if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
                generic_pool.append(save_path)
            elif _download_image(url, save_path):
                generic_pool.append(save_path)
                total_downloaded += 1
        time.sleep(1)

    print(f"\nGeneric pool: {len(generic_pool)} images")
    print(f"Total downloaded: {total_downloaded}")
    print(f"API calls used: {api_calls}")

    # Step 2: Assign images to each product deterministically
    image_paths = []
    fallback_count = 0

    for idx, row in df.iterrows():
        category = row.get("category", "")
        product_name = str(row.get("product_name", f"product_{idx}"))

        pool = image_pool.get(category, [])
        if not pool:
            pool = generic_pool

        if not pool:
            # No images available, keep existing SVG
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
    print(f"Fallbacks (no image): {fallback_count}")
    print(f"Images saved to: {IMAGE_DIR}")


if __name__ == "__main__":
    main()
