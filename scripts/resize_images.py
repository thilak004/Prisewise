"""Resize all product images to small thumbnails for faster deployment.

Converts all images in assets/products/ to 100x100px JPEGs at quality 60.
Reduces total size from ~133 MB to ~5-10 MB, suitable for git push.
"""

import os

from PIL import Image

IMAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "products")


def main():
    files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]
    print(f"Resizing {len(files)} images...")

    total_before = 0
    total_after = 0

    for i, filename in enumerate(files):
        filepath = os.path.join(IMAGE_DIR, filename)

        try:
            # Get size before
            size_before = os.path.getsize(filepath)
            total_before += size_before

            # Open, resize, and save
            with Image.open(filepath) as img:
                img = img.resize((100, 100), Image.LANCZOS)
                img.save(filepath, "JPEG", quality=60, optimize=True)

            # Get size after
            size_after = os.path.getsize(filepath)
            total_after += size_after

            if (i + 1) % 100 == 0:
                print(f"  Resized {i + 1}/{len(files)} images")

        except Exception as e:
            print(f"  Failed to resize {filename}: {e}")

    print(f"\nDone!")
    print(f"Size before: {total_before / 1024 / 1024:.1f} MB")
    print(f"Size after: {total_after / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
