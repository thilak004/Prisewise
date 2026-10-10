"""Generate unique SVG-based product images for every product in the dataset.

Each image is a deterministic SVG based on product name, category, and platform,
encoded as a base64 data URI and stored in a new `image_data` column.
This avoids external API dependencies and works offline.
"""

import base64
import hashlib
import os

import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pricewise_data.csv")

CATEGORY_COLORS = {
    "Electronics": "#4A90D9",
    "Fashion": "#E91E63",
    "Beauty": "#FF6B6B",
    "Home": "#4CAF50",
    "Books": "#FF9800",
}

PLATFORM_COLORS = {
    "Amazon": "#FF9900",
    "Flipkart": "#2874F0",
    "Croma": "#00BFA5",
    "Reliance Digital": "#D32F2F",
    "Tata CLiQ": "#1976D2",
    "Myntra": "#FF3F6C",
    "Nykaa": "#FC2779",
    "Purplle": "#7B1FA2",
    "Pepperfry": "#8D6E63",
}


def _hash_string(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def _escape_xml(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_image(product_name: str, category: str, platform: str) -> str:
    """Generate a unique SVG image as a base64 data URI."""
    name = str(product_name) if pd.notna(product_name) else "Product"
    cat = str(category) if pd.notna(category) else "General"
    plat = str(platform) if pd.notna(platform) else "Store"

    # Deterministic colors
    cat_color = CATEGORY_COLORS.get(cat, "#607D8B")
    plat_color = PLATFORM_COLORS.get(plat, "#9E9E9E")

    # Hash for variation
    h = _hash_string(f"{name}{cat}{plat}")
    hue_shift = h % 60 - 30  # -30 to +30

    # Initials for the product (first 2 chars of first two words)
    words = name.split()[:2]
    initials = "".join(w[0] for w in words if w).upper()[:2] or "P"

    # Generate SVG
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{cat_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{plat_color};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="200" height="200" fill="url(#bg)" rx="16"/>
  <circle cx="100" cy="80" r="35" fill="rgba(255,255,255,0.2)"/>
  <text x="100" y="92" font-family="Arial,sans-serif" font-size="32" font-weight="bold"
        fill="white" text-anchor="middle">{_escape_xml(initials)}</text>
  <text x="100" y="140" font-family="Arial,sans-serif" font-size="14" font-weight="600"
        fill="white" text-anchor="middle">{_escape_xml(cat)}</text>
  <text x="100" y="160" font-family="Arial,sans-serif" font-size="11"
        fill="rgba(255,255,255,0.8)" text-anchor="middle">{_escape_xml(plat)}</text>
  <rect x="20" y="175" width="160" height="4" rx="2" fill="rgba(255,255,255,0.3)"/>
</svg>"""

    # Encode as base64 data URI
    svg_bytes = svg.encode("utf-8")
    b64 = base64.b64encode(svg_bytes).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"


def main():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows, {df['product_name'].nunique()} unique products")

    # Generate image for each row
    images = []
    for _, row in df.iterrows():
        img = generate_image(
            row.get("product_name", ""),
            row.get("category", ""),
            row.get("platform", ""),
        )
        images.append(img)

    df["image_data"] = images

    # Save
    df.to_csv(DATA_PATH, index=False)
    print(f"Added 'image_data' column with {len(images)} images")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    main()
