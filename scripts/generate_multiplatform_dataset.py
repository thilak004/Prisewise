import os
import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)

# Platform configurations tailored to categories for realism:
# Electronics: Amazon, Flipkart, Croma, Reliance Digital, Tata CLiQ
# Fashion: Amazon, Flipkart, Myntra, Ajio, Tata CLiQ
# Beauty: Amazon, Flipkart, Nykaa, Purplle, Myntra
# Home: Amazon, Flipkart, Croma, Reliance Digital, Pepperfry
# Books: Amazon, Flipkart, Bookswagon, Crossword, SapnaOnline

category_platforms = {
    "Electronics": ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Tata CLiQ"],
    "Fashion": ["Amazon", "Flipkart", "Myntra", "Ajio", "Tata CLiQ"],
    "Beauty": ["Amazon", "Flipkart", "Nykaa", "Purplle", "Myntra"],
    "Home": ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Pepperfry"],
    "Books": ["Amazon", "Flipkart", "Bookswagon", "Crossword", "SapnaOnline"],
}

# 60 products per category = 300 unique products total
# 300 products * 5 platforms = 1,500 total offers (500 extra over 1,000)
catalog = {
    "Electronics": [
        ("Apple iPhone 16 (128 GB)", 79900),
        ("Apple iPhone 16 Plus (128 GB)", 89900),
        ("Apple iPhone 16 Pro (256 GB)", 129900),
        ("Apple iPhone 15 (128 GB)", 69900),
        ("Apple iPhone 15 Plus (128 GB)", 79900),
        ("Samsung Galaxy S24 Ultra 5G (256 GB)", 129999),
        ("Samsung Galaxy S24+ 5G (256 GB)", 99999),
        ("Samsung Galaxy S24 5G (256 GB)", 79999),
        ("Samsung Galaxy S23 FE 5G (128 GB)", 49999),
        ("Samsung Galaxy A55 5G (128 GB)", 39999),
        ("OnePlus 12 (256 GB)", 64999),
        ("OnePlus 12R (128 GB)", 39999),
        ("OnePlus Nord 4 5G (256 GB)", 32999),
        ("OnePlus Nord CE4 (128 GB)", 24999),
        ("Google Pixel 9 Pro (128 GB)", 109999),
        ("Google Pixel 9 (128 GB)", 79999),
        ("Google Pixel 8a (128 GB)", 52999),
        ("Xiaomi 14 (512 GB)", 69999),
        ("Redmi Note 13 Pro+ 5G (256 GB)", 31999),
        ("Redmi 13C 5G (128 GB)", 11999),
        ("Realme GT 6 (256 GB)", 40999),
        ("Realme 12 Pro+ 5G (256 GB)", 29999),
        ("Motorola Edge 50 Pro (256 GB)", 35999),
        ("Motorola Edge 50 Fusion (128 GB)", 22999),
        ("Apple MacBook Air M3 (13-inch, 256 GB)", 114900),
        ("Apple MacBook Air M2 (13-inch, 256 GB)", 99900),
        ("Apple MacBook Pro 14-inch M3 (512 GB)", 169900),
        ("Dell XPS 13 Intel Core Ultra 7", 139990),
        ("Dell Inspiron 15 Intel Core i5", 54990),
        ("HP Pavilion 15 AMD Ryzen 7", 67990),
        ("HP Victus Gaming Laptop AMD Ryzen 5", 62990),
        ("Lenovo ThinkPad E14 Gen 5", 62990),
        ("Lenovo IdeaPad Slim 3 Intel Core i5", 48990),
        ("ASUS ROG Zephyrus G14 Gaming Laptop", 149990),
        ("ASUS TUF Gaming F15 Intel Core i5", 58990),
        ("Acer Swift Go 14 OLED", 59990),
        ("Apple iPad Air 11-inch M2 (128 GB)", 59900),
        ("Apple iPad 10th Gen (64 GB)", 34900),
        ("Apple iPad Pro 11-inch M4 (256 GB)", 99900),
        ("Samsung Galaxy Tab S9 FE (128 GB)", 36999),
        ("Samsung Galaxy Tab A9+ (64 GB)", 18999),
        ("Sony WH-1000XM5 Wireless Noise Cancelling Headphones", 29990),
        ("Sony WH-1000XM4 Wireless Noise Cancelling Headphones", 22990),
        ("Sony WH-CH720N Noise Canceling Wireless Headphones", 9990),
        ("Bose QuietComfort 45 Bluetooth Headphones", 26900),
        ("Bose Noise Cancelling Headphones 700", 29900),
        ("Apple AirPods Pro (2nd Gen)", 24900),
        ("Apple AirPods (3rd Gen)", 18900),
        ("Samsung Galaxy Buds2 Pro", 14999),
        ("OnePlus Buds Pro 2", 9999),
        ("Boat Airdopes 141 TWS Earbuds", 1499),
        ("JBL Flip 6 Portable Bluetooth Speaker", 9999),
        ("JBL Charge 5 Portable Bluetooth Speaker", 14999),
        ("Marshall Emberton II Bluetooth Speaker", 14999),
        ("Apple Watch Series 9 GPS 45mm", 44900),
        ("Apple Watch SE (2nd Gen) GPS 44mm", 29900),
        ("Samsung Galaxy Watch 6 Bluetooth 44mm", 29999),
        ("Amazfit GTR 4 Smartwatch", 16999),
        ("Sony Bravia 55 inch 4K Ultra HD Smart Google TV", 64990),
        ("LG 55 inch 4K Ultra HD Smart OLED TV", 119990),
    ],
    "Fashion": [
        ("Levi's 511 Men's Slim Fit Jeans", 2999),
        ("Levi's 501 Original Fit Men's Jeans", 3599),
        ("Levi's Women's 711 Skinny Fit Jeans", 2799),
        ("Wrangler Regular Fit Men's Jeans", 2499),
        ("Wrangler Men's Texas Stretch Regular Jeans", 2899),
        ("Pepe Jeans London Men's Skinny Jeans", 2799),
        ("Nike Air Force 1 '07 Men's Sneakers", 8195),
        ("Nike Air Max SC Running Shoes", 5995),
        ("Nike Revolution 7 Men's Road Running Shoes", 3695),
        ("Adidas Originals Stan Smith Sneakers", 7999),
        ("Adidas Originals Superstar Sneakers", 8999),
        ("Adidas Ultraboost Light Running Shoes", 12999),
        ("Puma Smash v2 Leather Sneakers", 3999),
        ("Puma Softride Rift Tech Running Shoes", 3499),
        ("New Balance 574 Core Sneakers", 8999),
        ("Skechers Men's Go Walk Max Walking Shoes", 4499),
        ("Tommy Hilfiger Solid Casual Men's Shirt", 4599),
        ("Tommy Hilfiger Embroidered Logo Polo T-Shirt", 3299),
        ("US Polo Assn Regular Fit Casual Shirt", 2399),
        ("US Polo Assn Solid Pique Polo T-Shirt", 1799),
        ("Zara Oversized Linen Blend Casual Shirt", 2990),
        ("H&M Regular Fit Denim Trucker Jacket", 2999),
        ("H&M Slim Fit Cotton Chino Trousers", 1999),
        ("Allen Solly Men's Slim Fit Casual Chinos", 2199),
        ("Peter England Men's Slim Fit Formal Trouser", 1599),
        ("Van Heusen Men's Formal Cotton Shirt", 1899),
        ("Arrow Men's Classic Formal White Shirt", 2299),
        ("Louis Philippe Men's Classic Formal Blazer", 7999),
        ("Raymond Men's Poly Wool Formal Suit", 9999),
        ("Biba Floral Print Cotton Anarkali Kurta", 2999),
        ("Biba Embroidered Straight Kurta with Palazzo", 4599),
        ("W for Woman Printed Straight Fit Kurta", 2499),
        ("Aurelia Geometric Print Cotton Kurta", 1699),
        ("Manyavar Men's Embroidered Silk Kurta Set", 6999),
        ("Manyavar Men's Jacquard Silk Indo-Western Set", 8999),
        ("FabIndia Cotton Hand Block Print Short Kurta", 1990),
        ("Fastrack Casual Analog Watch for Men", 1895),
        ("Casio Vintage Digital Unisex Watch A168WA", 2695),
        ("Casio G-Shock GA-2100 Black Dial Watch", 8495),
        ("Fossil Grant Chronograph Leather Watch", 9995),
        ("Fossil Jacqueline Women's Analog Watch", 8495),
        ("Titan Neo Analog Dial Men's Watch", 4495),
        ("Titan Raga Aurora Women's Analog Watch", 6995),
        ("Ray-Ban Classic Aviator Sunglasses RB3025", 8590),
        ("Ray-Ban Wayfarer Classic Sunglasses RB2140", 7990),
        ("Oakley Holbrook Polarized Sunglasses", 9490),
        ("Wildcraft 45L Cargo Rucksack Backpack", 3499),
        ("American Tourister 68cm Trolley Bag Suitcase", 4899),
        ("American Tourister 32L Laptop Backpack", 2299),
        ("Skybags Brat Casual Backpack 30L", 1899),
        ("Safari Thorium 65cm Polycarbonate Hard Luggage", 3999),
        ("Woodland Men's Leather Casual Boots", 4295),
        ("Clarks Men's Tilden Walk Oxford Leather Shoes", 5999),
        ("Red Tape Men's Classic Walking Slip-On Shoes", 1699),
        ("Lavie Women's Faux Leather Satchel Handbag", 2690),
        ("Baggit Structured Women's Tote Bag", 2190),
        ("Caprese Faux Leather Women's Shoulder Bag", 2499),
        ("Allen Solly Women's Solid Regular Fit Blazer", 3499),
        ("Calvin Klein Men's Classic Monogram Leather Belt", 3199),
        ("Wildhorn Men's Genuine Leather Bifold Wallet", 899),
    ],
    "Beauty": [
        ("Cetaphil Gentle Skin Cleanser 250ml", 645),
        ("Cetaphil Moisturizing Lotion 250ml", 599),
        ("Cetaphil Bright Healthy Radiance Day Cream SPF 15", 999),
        ("Minimalist 10% Niacinamide Face Serum 30ml", 599),
        ("Minimalist 2% Salicylic Acid Face Serum 30ml", 549),
        ("Minimalist 16% Vitamin C Face Serum 30ml", 699),
        ("The Ordinary Hyaluronic Acid 2% + B5 30ml", 750),
        ("The Ordinary Niacinamide 10% + Zinc 1% 30ml", 600),
        ("The Ordinary AHA 30% + BHA 2% Peeling Solution", 950),
        ("The Ordinary Caffeine Solution 5% + EGCG", 700),
        ("Neutrogena Hydro Boost Water Gel 50g", 1050),
        ("Neutrogena Ultra Sheer Dry-Touch Sunscreen SPF 50+", 675),
        ("Neutrogena Deep Clean Gentle Foaming Cleanser 100g", 399),
        ("Plum Green Tea Pore Cleansing Face Wash 100ml", 345),
        ("Plum 15% Vitamin C Face Serum 30ml", 790),
        ("Dot & Key Watermelon Cooling Sunscreen SPF 50", 495),
        ("Dot & Key Cica Calming Blemish Clearing Gel", 595),
        ("Dot & Key Barrier Repair Face Moisturizer 100ml", 595),
        ("L'Oreal Paris Extraordinary Oil Hair Serum 100ml", 649),
        ("L'Oreal Paris Hyaluron Moisture Shampoo 650ml", 749),
        ("L'Oreal Paris Revitalift 1.5% Hyaluronic Acid Serum", 899),
        ("Mamaearth Onion Hair Fall Control Shampoo 400ml", 499),
        ("Mamaearth Ubtan Face Wash with Turmeric & Saffron", 375),
        ("Tresemme Keratin Smooth Conditioner 340ml", 420),
        ("Tresemme Keratin Smooth Shampoo 580ml", 620),
        ("Maybelline New York Colossal Waterproof Mascara", 449),
        ("Maybelline Fit Me Matte + Poreless Foundation", 599),
        ("Maybelline Superstay Matte Ink Liquid Lipstick", 699),
        ("MAC Retro Matte Lipstick - Ruby Woo", 2150),
        ("MAC Studio Fix Powder Plus Foundation", 3300),
        ("MAC Prep + Prime Fix+ Facial Mist 100ml", 2400),
        ("Lakme Absolute Matte Melt Liquid Lip Color", 525),
        ("Lakme Lumi Skin Cream Highlighter 60g", 349),
        ("Lakme Eyeconic Kajal Deep Black Twin Pack", 399),
        ("Forest Essentials Ayurvedic Night Treatment Jasmine", 3150),
        ("Forest Essentials Soundarya Radiance Cream", 5600),
        ("Forest Essentials Delicate Facial Cleanser Kashmiri Saffron", 1475),
        ("Biotique Bio Dandelion Ageless Lightening Serum 40ml", 230),
        ("Biotique Bio Morning Nectar Nourish & Hydrate Lotion", 280),
        ("Versace Eros Eau De Toilette 100ml", 7800),
        ("Versace Bright Crystal EDT for Women 90ml", 7500),
        ("Davidoff Cool Water Men EDT 125ml", 5200),
        ("Calvin Klein One Unisex EDT 100ml", 4900),
        ("Jaguar Classic Black EDT for Men 100ml", 2200),
        ("Nautica Voyage Eau De Toilette for Men 100ml", 2450),
        ("Nivea Soft Light Moisturizing Cream 200ml", 340),
        ("Nivea Men Deep Impact Shower Gel 250ml", 225),
        ("Vaseline Intensive Care Cocoa Glow Body Lotion 400ml", 385),
        ("Vaseline Healthy Bright Daily Sun Refreshing Body Lotion", 425),
        ("Bioré UV Aqua Rich Watery Essence SPF 50+", 1270),
        ("Philips Kerashine Titanium Hair Straightener", 2495),
        ("Philips Hair Dryer 1200W Compact", 1195),
        ("Dyson Supersonic Hair Dryer HD08", 34900),
        ("Dyson Airwrap Multi-Styler Complete Long", 45900),
        ("Urban Company Cordless Hair Trimmer", 1299),
        ("Philips Series 3000 Beard Trimmer BT3211", 1695),
        ("Clinique Moisture Surge 100H Auto-Replenishing Hydrator", 2950),
        ("Clinique Take The Day Off Cleansing Balm", 3200),
        ("Kama Ayurveda Pure Rose Water 200ml", 1450),
        ("Kama Ayurveda Bringadi Intensive Hair Treatment Oil", 1695),
    ],
    "Home": [
        ("Philips Digital Air Fryer HD9200 (4.1 L)", 7995),
        ("Instant Pot Duo 7-in-1 Electric Pressure Cooker 6 Qt", 9999),
        ("Prestige Iris 750W Mixer Grinder with 4 Jars", 3895),
        ("Bajaj Rex 500W Mixer Grinder with 3 Jars", 2499),
        ("Wonderchef Nutri-Blend 400W Mixer Grinder", 3200),
        ("Sujata Dynamix 900W Mixer Grinder with 3 Jars", 6200),
        ("Dyson V12 Detect Slim Total Clean Cordless Vacuum", 55900),
        ("Eureka Forbes Quick Clean DX 1200W Vacuum Cleaner", 3999),
        ("Kent Grand Plus RO + UV + UF Water Purifier 9L", 16999),
        ("Aquaguard Aura RO + UV + Active Copper Water Purifier", 14499),
        ("Mi Smart Air Purifier 4 with True HEPA Filter", 12999),
        ("Philips Series 2000i Smart Air Purifier", 18995),
        ("Havells Stealth Air 1200mm Ceiling Fan", 4990),
        ("Atomberg Renesa 1200mm BLDC Motor Ceiling Fan", 3899),
        ("Crompton SilentPro Enso 1200mm BLDC Ceiling Fan", 4999),
        ("Bajaj New Shakti Neo 15L Storage Water Heater", 6499),
        ("AO Smith HSE-SHS-015 Storage 15L Water Heater", 7899),
        ("Solimo 100% Cotton 300 TC Queen Flat Bedsheet", 1299),
        ("Wakefit Hollow Fiber Sleeping Pillows (Set of 2)", 799),
        ("SleepyCat Original 6-inch Orthopedic Memory Foam Mattress", 12499),
        ("Wakefit Orthopedic Memory Foam 6-inch King Mattress", 13999),
        ("The Sleep Company SmartGRID Orthopedic Pro Mattress", 19999),
        ("Portronics Pure Sound 1 Pro 20W Bluetooth Soundbar", 1999),
        ("Stanley Classic Vacuum Insulated Flask 1L", 3499),
        ("Milton Stainless Steel Thermosteel Bottle 1000ml", 995),
        ("Pigeon by Stovekraft Cruise 1800W Induction Cooktop", 1995),
        ("Prestige PIC 20 1600W Induction Cooktop", 2495),
        ("Bosch 7kg 1200 RPM Fully Automatic Front Load Washing Machine", 34990),
        ("IFB 6.5kg 5 Star Fully Automatic Top Load Washing Machine", 17990),
        ("LG 7kg 5 Star Inverter Touch Control Front Load Washing Machine", 32990),
        ("Samsung 7kg Fully Automatic Top Load Washing Machine", 16490),
        ("Faber 60cm Curved Glass Autoclean Kitchen Chimney", 12990),
        ("Hindware 60cm 1200 m3/hr Pyramid Kitchen Chimney", 8990),
        ("Godrej 236L 2 Star Frost Free Double Door Refrigerator", 21990),
        ("Samsung 236L 3 Star Digital Inverter Double Door Refrigerator", 25990),
        ("Whirlpool 184L 4 Star Direct Cool Single Door Refrigerator", 15490),
        ("LG 190L 4 Star Smart Inverter Single Door Refrigerator", 16990),
        ("Morphy Richards 24L Convection Microwave Oven", 11495),
        ("IFB 30L Convection Microwave Oven 30BRC2", 15290),
        ("Panasonic 20L Solo Microwave Oven", 6490),
        ("Prestige Deluxe Alpha Stainless Steel 3L Pressure Cooker", 2150),
        ("Hawkins Contura 3L Hard Anodized Pressure Cooker", 1950),
        ("Borosil Glass Mixing Bowls Set of 3", 1195),
        ("Solimo Stainless Steel Knife Set 3-Piece", 699),
        ("Cello Opalware Dazzle Tropical Lagoon Dinner Set 18-Piece", 1899),
        ("Pigeon 4-Piece Non-Stick Cookware Set", 1799),
        ("Prestige Omega Deluxe Granite 3-Piece Cookware Set", 2399),
        ("Philips Daily Collection 300W Hand Mixer", 1895),
        ("Kent 16044 Hand Blender 300W with Stainless Steel Blade", 1499),
        ("Pigeon by Stovekraft 1.5L Stainless Steel Electric Kettle", 649),
        ("Havells Aqua Plus 1.2L 1500W Stainless Steel Kettle", 1399),
        ("Morphy Richards Europa 800W Espresso & Cappuccino Maker", 4995),
        ("Wonderchef Regalia Capsule Coffee Machine", 8999),
        ("Godrej Security Solutions Forte Pro Digital Electronic Safe", 5999),
        ("D-Link 2MP Full HD Pan & Tilt Smart Home Security Camera", 2199),
        ("TP-Link Tapo C200 360-degree 2MP Wi-Fi Security Camera", 2399),
        ("Wipro Smart LED Bulb 9W B22 WiFi Enabled", 599),
        ("Philips Smart Wi-Fi HexaStyle Downlight LED 10W", 999),
        ("Spaces 100% Cotton 400 TC Super King Bedsheet Set", 3499),
        ("Story@Home Blackout Window Curtains 7 Feet (Set of 2)", 1299),
    ],
    "Books": [
        ("Atomic Habits by James Clear", 599),
        ("The Psychology of Money by Morgan Housel", 450),
        ("Sapiens: A Brief History of Humankind by Yuval Noah Harari", 699),
        ("Homo Deus: A Brief History of Tomorrow by Yuval Noah Harari", 699),
        ("Rich Dad Poor Dad by Robert T. Kiyosaki", 499),
        ("Ikigai: The Japanese Secret to a Long and Happy Life", 499),
        ("Deep Work by Cal Newport", 499),
        ("So Good They Can't Ignore You by Cal Newport", 550),
        ("Thinking, Fast and Slow by Daniel Kahneman", 599),
        ("The Alchemist by Paulo Coelho", 350),
        ("To Kill a Mockingbird by Harper Lee", 399),
        ("1984 by George Orwell", 299),
        ("Animal Farm by George Orwell", 199),
        ("The Midnight Library by Matt Haig", 499),
        ("Project Hail Mary by Andy Weir", 599),
        ("The Martian by Andy Weir", 499),
        ("Can't Hurt Me: Master Your Mind by David Goggins", 699),
        ("Never Finished by David Goggins", 699),
        ("Good to Great by Jim Collins", 650),
        ("Start With Why by Simon Sinek", 550),
        ("Leaders Eat Last by Simon Sinek", 599),
        ("The Subtle Art of Not Giving a F*ck by Mark Manson", 499),
        ("Everything Is F*cked by Mark Manson", 499),
        ("A Man Called Ove by Fredrik Backman", 450),
        ("Anxious People by Fredrik Backman", 499),
        ("Shoe Dog: A Memoir by the Creator of Nike by Phil Knight", 599),
        ("Rework by Jason Fried and David Heinemeier Hansson", 550),
        ("Zero to One by Peter Thiel", 499),
        ("The Power of Your Subconscious Mind by Joseph Murphy", 250),
        ("Man's Search for Meaning by Viktor E. Frankl", 350),
        ("The 7 Habits of Highly Effective People by Stephen R. Covey", 599),
        ("Think and Grow Rich by Napoleon Hill", 250),
        ("The Courage to Be Disliked by Ichiro Kishimi", 499),
        ("Factfulness by Hans Rosling", 499),
        ("Quiet: The Power of Introverts by Susan Cain", 550),
        ("Outliers: The Story of Success by Malcolm Gladwell", 499),
        ("Talking to Strangers by Malcolm Gladwell", 550),
        ("Grit: The Power of Passion and Perseverance by Angela Duckworth", 550),
        ("Never Split the Difference by Chris Voss", 599),
        ("Essentialism: The Disciplined Pursuit of Less by Greg McKeown", 499),
        ("Ego Is the Enemy by Ryan Holiday", 450),
        ("The Obstacle Is the Way by Ryan Holiday", 450),
        ("Meditations by Marcus Aurelius", 299),
        ("The Daily Stoic by Ryan Holiday", 599),
        ("Steve Jobs by Walter Isaacson", 799),
        ("Elon Musk by Walter Isaacson", 999),
        ("Leonardo da Vinci by Walter Isaacson", 899),
        ("Dune by Frank Herbert", 599),
        ("The Hobbit by J.R.R. Tolkien", 499),
        ("The Lord of the Rings 3-Book Box Set by J.R.R. Tolkien", 1499),
        ("The Da Vinci Code by Dan Brown", 450),
        ("Angels and Demons by Dan Brown", 450),
        ("Norwegian Wood by Haruki Murakami", 499),
        ("Kafka on the Shore by Haruki Murakami", 550),
        ("The 48 Laws of Power by Robert Greene", 650),
        ("The Art of War by Sun Tzu", 199),
        ("Clear Thinking by Shane Parrish", 599),
        ("Four Thousand Weeks: Time Management for Mortals by Oliver Burkeman", 499),
        ("The Song of Achilles by Madeline Miller", 499),
        ("Before the Coffee Gets Cold by Toshikazu Kawaguchi", 399),
    ],
}

# Domain mapping for clean URLs
domain_map = {
    "Amazon": "amazon.in",
    "Flipkart": "flipkart.com",
    "Croma": "croma.com",
    "Reliance Digital": "reliancedigital.in",
    "Tata CLiQ": "tatacliq.com",
    "Myntra": "myntra.com",
    "Ajio": "ajio.com",
    "Nykaa": "nykaa.com",
    "Purplle": "purplle.com",
    "Pepperfry": "pepperfry.com",
    "Bookswagon": "bookswagon.com",
    "Crossword": "crossword.in",
    "SapnaOnline": "sapnaonline.com",
}

platform_offsets = {
    "Amazon": -0.04,
    "Flipkart": -0.05,
    "Croma": -0.02,
    "Reliance Digital": -0.01,
    "Tata CLiQ": -0.03,
    "Myntra": -0.03,
    "Ajio": -0.06,
    "Nykaa": -0.02,
    "Purplle": -0.04,
    "Pepperfry": -0.02,
    "Bookswagon": -0.08,
    "Crossword": -0.02,
    "SapnaOnline": -0.05,
}

rows = []
base_date = datetime(2026, 9, 25)

for category, products in catalog.items():
    platforms = category_platforms[category]
    for prod_name, base_mrp in products:
        for platform in platforms:
            offset = platform_offsets.get(platform, -0.03)

            # Price variation between platforms: ±2.5%
            var_pct = offset + random.uniform(-0.025, 0.025)
            # General discount off MRP between 8% and 28%
            disc_pct = random.uniform(0.08, 0.28) + var_pct
            disc_pct = max(0.04, min(0.48, disc_pct))

            selling_price = round(base_mrp * (1.0 - disc_pct), 2)
            actual_discount = round(((base_mrp - selling_price) / base_mrp) * 100, 1)

            rating = round(random.uniform(3.8, 4.9), 1)

            avail_rand = random.random()
            if avail_rand < 0.88:
                avail = "In Stock"
            elif avail_rand < 0.95:
                avail = "Limited Stock"
            else:
                avail = "Out of Stock"

            days_ago = random.randint(0, 14)
            scraped_date = (base_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            domain = domain_map.get(platform, "ecom.in")
            clean_q = prod_name.replace(" ", "+")
            url = f"https://www.{domain}/search?q={clean_q}"

            rows.append({
                "product_name": prod_name,
                "category": category,
                "platform": platform,
                "price": selling_price,
                "original_price": float(base_mrp),
                "discount": actual_discount,
                "rating": rating,
                "availability": avail,
                "product_url": url,
                "scraped_date": scraped_date,
            })

df = pd.DataFrame(rows)

print(f"Generated {len(df)} total rows across {df['product_name'].nunique()} unique products.")
print("\nCategory breakdown (rows):")
print(df["category"].value_counts())
print("\nPlatform breakdown (rows):")
print(df["platform"].value_counts())
print(f"\nUnique platforms: {df['platform'].nunique()} platforms: {sorted(df['platform'].unique())}")
multi_plat_count = (df.groupby("product_name")["platform"].nunique() == 5).sum()
print(f"Products available on all 5 platforms: {multi_plat_count} / {df['product_name'].nunique()}")

# Save to all target locations
out_paths = [
    os.path.abspath("data/pricewise_data.csv"),
    os.path.abspath("data/sample_data.csv"),
    os.path.abspath("data/processed/pricewise_data.csv"),
    os.path.abspath("data/raw/pricewise_raw.csv"),
]

for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    df.to_csv(p, index=False)
    print(f"Saved: {p} ({len(df)} rows)")
