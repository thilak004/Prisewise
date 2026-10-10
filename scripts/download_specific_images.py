"""Download specific product images by extracting product type from product names.

Instead of assigning random category images, this script:
1. Extracts the product type from each product name (e.g., "mobile", "laptop")
2. Searches Unsplash for that specific product type
3. Downloads and caches the image for each unique product
4. Assigns images to all 1,500 rows in the CSV
"""

import hashlib
import json
import os
import re
import time
import urllib.request
import urllib.parse

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricewise_data.csv")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "products")
UNSPLASH_ACCESS_KEY = "4EDOGqpGDOlRgsxLQU_cW4kkTmp57G2CD_uMpGONdzI"
UNSPLASH_API_BASE = "https://api.unsplash.com"

# Map product keywords to Unsplash search queries
PRODUCT_TYPE_QUERIES = {
    # Smartphones
    "iphone": "iphone smartphone",
    "galaxy": "samsung galaxy smartphone",
    "pixel": "google pixel smartphone",
    "oneplus": "oneplus smartphone",
    "redmi": "xiaomi redmi smartphone",
    "realme": "realme smartphone",
    "oppo": "oppo smartphone",
    "vivo": "vivo smartphone",
    "nothing": "nothing phone",
    # Laptops
    "laptop": "laptop computer",
    "macbook": "apple macbook laptop",
    "inspiron": "dell laptop",
    "thinkpad": "lenovo thinkpad laptop",
    "vivobook": "asus vivobook laptop",
    "ideapad": "lenovo ideapad laptop",
    "pavilion": "hp pavilion laptop",
    "omen": "hp omen gaming laptop",
    "nitro": "acer nitro gaming laptop",
    "tuf": "asus tuf gaming laptop",
    "legion": "lenovo legion gaming laptop",
    "victus": "hp victus laptop",
    "aspire": "acer aspire laptop",
    "swift": "acer swift laptop",
    # Audio / Headphones
    "headphone": "headphones",
    "earphone": "earphones",
    "airpods": "apple airpods",
    "earbuds": "wireless earbuds",
    "airdopes": "boat airdopes earbuds",
    "wh-1000": "sony wh-1000xm headphones",
    "bose": "bose headphones",
    "sennheiser": "sennheiser headphones",
    "jbl": "jbl headphones",
    "boat": "boat earphones",
    "noise": "noise earbuds",
    "zebronics": "zebronics earphones",
    "ptron": "ptron earphones",
    # TVs
    "tv": "television tv",
    "smart tv": "smart tv television",
    "oled tv": "oled tv television",
    "qled tv": "qled tv television",
    # Cameras
    "camera": "camera",
    "dslr": "dslr camera",
    "mirrorless": "mirrorless camera",
    # Smart Watches
    "watch": "smartwatch",
    "smartwatch": "smartwatch",
    "fitbit": "fitbit smartwatch",
    # Tablets
    "tablet": "tablet device",
    "ipad": "apple ipad tablet",
    "galaxy tab": "samsung galaxy tab tablet",
    # Home appliances
    "refrigerator": "refrigerator",
    "fridge": "refrigerator",
    "ac ": "air conditioner",
    "air conditioner": "air conditioner",
    "washing machine": "washing machine",
    "microwave": "microwave oven",
    # Fashion
    "t-shirt": "t-shirt apparel",
    "shirt": "shirt clothing",
    "jeans": "jeans denim",
    "shoes": "shoes sneakers",
    "sneakers": "sneakers shoes",
    "kurta": "kurta ethnic wear",
    "saree": "saree ethnic wear",
    "dress": "dress clothing",
    "jacket": "jacket coat",
    "hoodie": "hoodie sweatshirt",
    "backpack": "backpack bag",
    # Beauty
    "lipstick": "lipstick makeup",
    "foundation": "foundation makeup",
    "serum": "skincare serum",
    "moisturizer": "moisturizer skincare",
    "shampoo": "shampoo hair care",
    "conditioner": "conditioner hair care",
    "perfume": "perfume fragrance",
    "cologne": "cologne fragrance",
    # Books
    "novel": "novel book fiction",
    "textbook": "textbook education",
    "notebook": "notebook stationery",
    "diary": "diary journal",
}


def _unsplash_search(query: str, per_page: int = 10) -> list:
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


def _extract_product_type(product_name: str) -> str:
    """Extract the product type from the product name."""
    name_lower = product_name.lower()
    for keyword, query in PRODUCT_TYPE_QUERIES.items():
        if keyword in name_lower:
            return query
    return None


def main():
    os.makedirs(IMAGE_DIR, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, {df['product_name'].nunique()} unique products")

    # Get unique product names
    unique_products = df["product_name"].dropna().unique().tolist()
    print(f"Unique products to process: {len(unique_products)}")

    # Check which products already have specific images
    existing_specific = [f for f in os.listdir(IMAGE_DIR) if f.startswith("specific_")]
    print(f"Already have {len(existing_specific)} specific images")

    # Download specific images for each unique product
    product_image_map = {}  # product_name -> local_path
    api_calls = 0
    downloads = 0

    for i, product_name in enumerate(unique_products):
        product_type = _extract_product_type(product_name)

        if product_type is None:
            # Use category-based fallback
            category = df[df["product_name"] == product_name]["category"].iloc[0]
            product_type = f"{category} product"

        # Create filename
        name_hash = hashlib.md5(product_name.encode()).hexdigest()[:12]
        filename = f"specific_{name_hash}.jpg"
        save_path = os.path.join(IMAGE_DIR, filename)

        # Check if already downloaded
        if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            product_image_map[product_name] = os.path.join("assets", "products", filename)
            continue

        # Search and download
        print(f"  [{i+1}/{len(unique_products)}] {product_type}: {product_name[:50]}...")
        api_calls += 1
        urls = _unsplash_search(product_type, per_page=5)

        if urls:
            # Download first result
            if _download_image(urls[0], save_path):
                product_image_map[product_name] = os.path.join("assets", "products", filename)
                downloads += 1
                print(f"    -> Downloaded!")
            else:
                print(f"    -> Download failed")
        else:
            print(f"    -> No results")

        # Rate limit
        time.sleep(1)

        # Stop if we're hitting API limits
        if api_calls >= 45:
            print(f"\nReached API limit ({api_calls} calls). Stopping.")
            break

    print(f"\nDownloaded {downloads} specific images using {api_calls} API calls")

    # Assign images to all rows
    print("\nAssigning images to CSV...")

    # Also load category-based images as fallback
    all_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg") and not f.startswith("specific_")]
    pool_by_category = {}
    for f in all_files:
        parts = f.split("_", 1)
        if len(parts) == 2:
            cat = parts[0]
            full_path = os.path.join("assets", "products", f)
            if cat not in pool_by_category:
                pool_by_category[cat] = []
            pool_by_category[cat].append(full_path)

    image_paths = []
    specific_count = 0
    fallback_count = 0

    for idx, row in df.iterrows():
        product_name = str(row.get("product_name", ""))
        category = str(row.get("category", ""))

        # Try specific image first
        if product_name in product_image_map:
            image_paths.append(product_image_map[product_name])
            specific_count += 1
        else:
            # Fall back to category-based image
            pool = pool_by_category.get(category, [])
            if pool:
                name_hash = int(hashlib.md5(product_name.encode()).hexdigest(), 16)
                selected_path = pool[name_hash % len(pool)]
                image_paths.append(selected_path)
                fallback_count += 1
            else:
                image_paths.append("")
                fallback_count += 1

    df["image_data"] = image_paths
    df.to_csv(DATA_PATH, index=False)

    print(f"\nDone!")
    print(f"Specific images: {specific_count}")
    print(f"Category fallbacks: {fallback_count}")


if __name__ == "__main__":
    main()
