"""Download real product images for all products in the dataset.

Uses LoremFlickr (free, no API key) to fetch real photos based on product names.
Images are cached locally in assets/products/ and file paths are stored in the CSV.
Falls back to the generated SVG if download fails.
"""

import hashlib
import os
import time
import urllib.request

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricewise_data.csv")
IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "products")


def _sanitize_filename(text: str) -> str:
    """Create a safe filename from product name."""
    safe = "".join(c if c.isalnum() else "_" for c in text)
    return safe[:50]


def _fetch_image_url(product_name: str, category: str) -> str | None:
    """Try to get a real image URL for a product using LoremFlickr.

    LoremFlickr serves real Flickr photos matching keywords. Free, no API key.
    Format: https://loremflickr.com/400/400/{keywords}
    """
    # Build search keywords from product name + category
    keywords = f"{product_name},{category}".replace(" ", ",").replace(",,", ",")
    keywords = ",".join(k for k in keywords.split(",") if k)  # remove empties

    url = f"https://loremflickr.com/400/400/{keywords}"
    return url


def _download_image(url: str, save_path: str, timeout: int = 10) -> bool:
    """Download an image from URL to local path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PriceWise/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                return False
            data = response.read()
            if len(data) < 100:  # too small, probably not a real image
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

    # Check if we already have an image_data column with local paths
    if "image_data" in df.columns:
        # Check if any are already local file paths (not base64)
        sample = df["image_data"].iloc[0] if len(df) > 0 else ""
        if isinstance(sample, str) and not sample.startswith("data:"):
            print("Images already downloaded. Skipping.")
            return

    image_paths = []
    success_count = 0
    fail_count = 0

    for idx, row in df.iterrows():
        product_name = str(row.get("product_name", "product"))
        category = str(row.get("category", ""))

        # Create unique filename
        name_hash = hashlib.md5(f"{product_name}_{category}_{idx}".encode()).hexdigest()[:8]
        filename = f"{_sanitize_filename(product_name)}_{name_hash}.jpg"
        save_path = os.path.join(IMAGE_DIR, filename)

        # Check if already downloaded
        if os.path.exists(save_path) and os.path.getsize(save_path) > 500:
            image_paths.append(save_path)
            success_count += 1
            continue

        # Try to download
        url = _fetch_image_url(product_name, category)
        if url and _download_image(url, save_path):
            image_paths.append(save_path)
            success_count += 1
        else:
            # Keep existing SVG as fallback
            existing = row.get("image_data", "")
            if isinstance(existing, str) and existing.startswith("data:"):
                image_paths.append(existing)
            else:
                image_paths.append("")
            fail_count += 1

        # Progress every 100
        if (idx + 1) % 100 == 0:
            print(f"Progress: {idx + 1}/{len(df)} (success: {success_count}, failed: {fail_count})")

        # Be nice to the server
        time.sleep(0.5)

    df["image_data"] = image_paths
    df.to_csv(DATA_PATH, index=False)

    print(f"\nDone! Downloaded {success_count} images, {fail_count} fallbacks")
    print(f"Images saved to: {IMAGE_DIR}")


if __name__ == "__main__":
    main()
