import unittest
from unittest.mock import MagicMock, patch

from scraper.base_scraper import BaseScraper


class _FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text
        self.headers = {}


class TestBaseScraper(unittest.TestCase):
    def test_429_stops_without_retry(self):
        scraper = BaseScraper(
            base_url="https://example.com",
            request_delay_seconds=0,
            request_timeout=1,
            max_retries=2,
            user_agent="PriceWise/1.0",
            mode="live",
        )

        # Avoid caching & sleeping.
        with patch("scraper.base_scraper.CACHE_ENABLED", False), patch("scraper.base_scraper.time.sleep") as sleep_mock:
            scraper.session.get = MagicMock(return_value=_FakeResponse(429))
            res = scraper._fetch_url("https://example.com/test")

        self.assertEqual(res.error, "Rate limited")
        self.assertEqual(scraper.session.get.call_count, 1)
        sleep_mock.assert_not_called()

    def test_5xx_retries_then_success(self):
        scraper = BaseScraper(
            base_url="https://example.com",
            request_delay_seconds=0,
            request_timeout=1,
            max_retries=2,
            user_agent="PriceWise/1.0",
            mode="live",
        )

        responses = [
            _FakeResponse(500),
            _FakeResponse(500),
            _FakeResponse(200, text="<html></html>"),
        ]

        with patch("scraper.base_scraper.CACHE_ENABLED", False), patch("scraper.base_scraper.time.sleep"):
            scraper.session.get = MagicMock(side_effect=responses)
            res = scraper._fetch_url("https://example.com/test")

        self.assertIsNone(res.error)
        self.assertEqual(scraper.session.get.call_count, 3)


if __name__ == "__main__":
    unittest.main()
