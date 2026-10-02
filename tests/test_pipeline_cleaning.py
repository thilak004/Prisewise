import unittest

import pandas as pd

from data_pipeline import clean_data


class TestPipelineCleaning(unittest.TestCase):
    def test_price_parsing_invalid_becomes_na(self):
        raw = pd.DataFrame(
            [
                {
                    "product_name": "Test A",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": "abc",
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
                {
                    "product_name": "Test B",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": -50,
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
                {
                    "product_name": "Test C",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 1999,
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
            ]
        )

        cleaned = clean_data(raw)
        # Essential drop removes rows missing price
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(cleaned.iloc[0]["product_name"], "Test C")

    def test_discount_parsing_invalid_becomes_na(self):
        raw = pd.DataFrame(
            [
                {
                    "product_name": "Test A",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 1999,
                    "original_price": 2000,
                    "discount": "not-a-number",
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                }
            ]
        )

        cleaned = clean_data(raw)
        self.assertTrue(pd.isna(cleaned.iloc[0]["discount"]))

    def test_rating_parsing_out_of_range_becomes_na(self):
        raw = pd.DataFrame(
            [
                {
                    "product_name": "Test A",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 1999,
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 20,  # invalid
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                }
            ]
        )

        cleaned = clean_data(raw)
        self.assertTrue(pd.isna(cleaned.iloc[0]["rating"]))

    def test_duplicate_removal_keeps_lowest_price_same_name_platform(self):
        raw = pd.DataFrame(
            [
                {
                    "product_name": "Phone X",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 3000,
                    "original_price": 3500,
                    "discount": 10,
                    "rating": 4.1,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
                {
                    "product_name": "Phone X",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 2500,
                    "original_price": 3500,
                    "discount": 10,
                    "rating": 4.1,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-02",
                },
            ]
        )

        cleaned = clean_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(float(cleaned.iloc[0]["price"]), 2500)

    def test_missing_essential_fields_removed(self):
        raw = pd.DataFrame(
            [
                {
                    "product_name": "",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": 1999,
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
                {
                    "product_name": "Phone Y",
                    "platform": "Amazon",
                    "category": "Phones",
                    "price": None,
                    "original_price": 2000,
                    "discount": 10,
                    "rating": 4.0,
                    "availability": "In Stock",
                    "product_url": "",
                    "scraped_date": "2024-01-01",
                },
            ]
        )

        cleaned = clean_data(raw)
        self.assertEqual(len(cleaned), 0)


if __name__ == "__main__":
    unittest.main()
