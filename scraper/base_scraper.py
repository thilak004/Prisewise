"""scraper/base_scraper.py

Base scraping utilities for PriceWise.

This file is designed for:
- Safe/relatively low-rate sequential fetching
- Clear handling of HTTP status codes
- Limited retries for temporary network / 5xx errors
- Simple URL caching to reduce unnecessary downloads
- robots.txt checking (best-effort)

IMPORTANT:
- This project DOES NOT attempt to bypass bot protection, CAPTCHAs, or anti-bot systems.
- If a source gets blocked (403/429) or triggers bot detection, we stop that source.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urljoin, urlparse

import requests
import urllib.robotparser

from scraper.scraper_config import (
    CACHE_ENABLED,
    CACHE_DIR,
    MAX_RETRIES,
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    USER_AGENT,
)


logger = logging.getLogger("pricewise_scraper")


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(str(CACHE_DIR), f"{_hash_url(url)}.txt")


def _safe_write_cache(url: str, text: str) -> None:
    if not CACHE_ENABLED:
        return
    try:
        os.makedirs(str(CACHE_DIR), exist_ok=True)
        with open(_cache_path(url), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        # Cache failures should not break scraping.
        logger.debug("Cache write failed", exc_info=True)


def _read_cache(url: str) -> str | None:
    if not CACHE_ENABLED:
        return None
    try:
        p = _cache_path(url)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        logger.debug("Cache read failed", exc_info=True)
    return None


def _robots_allowed(base_url: str, target_url: str, user_agent: str) -> bool:
    """Best-effort robots.txt check.

    If robots cannot be fetched/parsed, we return True (do not block scraping by default).
    """
    try:
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            return True

        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        cached = _read_cache(robots_url)
        if cached is None:
            resp = requests.get(
                robots_url,
                headers={"User-Agent": user_agent},
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code == 200:
                cached = resp.text
                _safe_write_cache(robots_url, cached)

        rp = urllib.robotparser.RobotFileParser()
        if cached is None:
            return True
        rp.parse(cached.splitlines())

        # robotparser wants a path
        t = urlparse(target_url)
        path = t.path or "/"
        return rp.can_fetch(user_agent, path)
    except Exception:
        logger.debug("robots.txt check failed", exc_info=True)
        return True


@dataclass
class FetchResult:
    url: str
    status_code: int | None
    text: str | None
    error: str | None


class BaseScraper:
    def __init__(
        self,
        base_url: str,
        request_delay_seconds: int = REQUEST_DELAY_SECONDS,
        request_timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        user_agent: str = USER_AGENT,
        mode: str = "demo",
    ):
        self.base_url = base_url
        self.request_delay_seconds = request_delay_seconds
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.mode = mode

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def _should_stop_for_status(self, status_code: int) -> bool:
        # Stop the source on access forbidden or rate limiting.
        return status_code in (403, 429)

    def _retryable_status(self, status_code: int) -> bool:
        # Retry only temporary failures.
        return status_code >= 500

    def _fetch_url(self, url: str) -> FetchResult:
        # Cache first.
        cached = _read_cache(url)
        if cached is not None:
            logger.info("[CACHE] Using cached response")
            return FetchResult(url=url, status_code=200, text=cached, error=None)

        headers = {"User-Agent": self.user_agent}

        for attempt in range(1, self.max_retries + 2):
            try:
                if attempt > 1:
                    # Exponential backoff for temporary errors.
                    backoff = min(60, (2 ** (attempt - 1)) * 2)
                    logger.info(f"[RETRY] Attempt {attempt} after backoff {backoff}s")
                    time.sleep(backoff)

                logger.info(f"[INFO] Requesting: {url}")
                resp = self.session.get(url, headers=headers, timeout=self.request_timeout, allow_redirects=False)

                if resp.status_code in (301, 302, 303, 307, 308):
                    # Follow redirects only if expected/safe: we will resolve Location if present.
                    loc = resp.headers.get("Location")
                    if not loc:
                        return FetchResult(url=url, status_code=resp.status_code, text=None, error="Redirect without Location")
                    next_url = urljoin(url, loc)
                    parsed = urlparse(next_url)
                    # Keep same netloc for safety.
                    if parsed.netloc != urlparse(self.base_url).netloc:
                        return FetchResult(url=url, status_code=resp.status_code, text=None, error="Redirected to different host; stopping")
                    url = next_url
                    logger.info(f"[REDIRECT] Following redirect to {url}")
                    continue

                if resp.status_code == 200:
                    text = resp.text
                    _safe_write_cache(url, text)
                    return FetchResult(url=url, status_code=resp.status_code, text=text, error=None)

                # Explicit access/rate-limit handling.
                if resp.status_code == 403:
                    return FetchResult(url=url, status_code=resp.status_code, text=None, error="Access forbidden")
                if resp.status_code == 429:
                    return FetchResult(url=url, status_code=resp.status_code, text=None, error="Rate limited")

                # CAPTCHA/bot detection often show as 403/429 or special pages.
                # We do not attempt to bypass; treat as access forbidden.
                if resp.status_code in (400, 401):
                    return FetchResult(url=url, status_code=resp.status_code, text=None, error=f"HTTP {resp.status_code}")

                # Retry 5xx.
                if self._retryable_status(resp.status_code):
                    if attempt <= self.max_retries + 1:
                        continue
                    return FetchResult(url=url, status_code=resp.status_code, text=None, error="Server error")

                # Other errors: return without retry.
                return FetchResult(
                    url=url,
                    status_code=resp.status_code,
                    text=None,
                    error=f"HTTP {resp.status_code}",
                )

            except requests.exceptions.Timeout:
                if attempt <= self.max_retries + 1:
                    logger.warning("[WARNING] Timeout — retrying")
                    continue
                return FetchResult(url=url, status_code=None, text=None, error="Timeout")

            except requests.exceptions.ConnectionError:
                if attempt <= self.max_retries + 1:
                    logger.warning("[WARNING] Connection error — retrying")
                    continue
                return FetchResult(url=url, status_code=None, text=None, error="Connection error")

            except Exception as e:
                logger.exception("Unexpected error during fetch")
                return FetchResult(url=url, status_code=None, text=None, error=str(e))

        return FetchResult(url=url, status_code=None, text=None, error="Failed after retries")

    def fetch(self, path: str) -> FetchResult:
        """Fetch a relative path on the base_url with robots + delay + safe status handling."""
        target_url = urljoin(self.base_url, path)

        # Demo mode should not hit live endpoints (including robots.txt checks).
        if self.mode == "demo":
            logger.info(f"[DEMO] Not requesting live URL: {target_url}")
            return FetchResult(url=target_url, status_code=None, text=None, error="Demo mode")

        # Robots check.
        if not _robots_allowed(self.base_url, target_url, self.user_agent):
            logger.warning(f"[SKIP] robots.txt disallows: {target_url}")
            return FetchResult(url=target_url, status_code=None, text=None, error="Robots disallow")

        # Rate limiting delay
        logger.info(f"[INFO] Waiting {self.request_delay_seconds} seconds before next request")
        time.sleep(self.request_delay_seconds)

        return self._fetch_url(target_url)
