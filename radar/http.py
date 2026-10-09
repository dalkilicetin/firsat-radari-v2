"""Hız sınırlı, tekrar deneyen HTTP istemcisi.

Her yanıt, çekildiği anın UTC zaman damgasıyla döner. Bu damga, geriye dönük testte
"o tarihte bu veri elimizde var mıydı?" sorusunun cevabının temelidir.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from radar import config

RETRY_STATUSES = {429, 500, 502, 503, 504}


class FetchError(Exception):
    def __init__(self, url: str, status: int | None, message: str):
        super().__init__(f"{url} -> {status}: {message}")
        self.url = url
        self.status = status


@dataclass
class Fetched:
    url: str
    status: int
    content: bytes
    fetched_at: datetime

    @property
    def text(self) -> str:
        return self.content.decode("utf-8", errors="replace")

    def json(self):
        return json.loads(self.content)


class HttpClient:
    def __init__(self, user_agent: str = config.USER_AGENT, retries: int = 4, timeout: float = 60):
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self.session.headers["Accept-Encoding"] = "gzip, deflate"
        self.retries = retries
        self.timeout = timeout
        self._last_request: dict[str, float] = {}
        self.request_count = 0

    def _throttle(self, host: str) -> None:
        rate = config.RATE_LIMITS.get(host, config.DEFAULT_RATE)
        wait = self._last_request.get(host, 0) + 1.0 / rate - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_request[host] = time.monotonic()

    def request(self, method: str, url: str, *, ok_statuses=(200,), retries: int | None = None, **kwargs) -> Fetched:
        host = urlparse(url).netloc
        kwargs.setdefault("timeout", self.timeout)
        last_error = ""
        status = None
        retries = self.retries if retries is None else retries
        for attempt in range(retries + 1):
            self._throttle(host)
            self.request_count += 1
            try:
                resp = self.session.request(method, url, **kwargs)
            except requests.RequestException as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                status = None
            else:
                status = resp.status_code
                if status in ok_statuses:
                    return Fetched(resp.url, status, resp.content, datetime.now(timezone.utc))
                last_error = resp.text[:200]
                if status not in RETRY_STATUSES:
                    break
                retry_after = resp.headers.get("Retry-After", "")
                if retry_after.isdigit() and attempt < retries:
                    time.sleep(min(int(retry_after), 60))
                    continue
            if attempt < retries:
                time.sleep(2 ** (attempt + 1))
        raise FetchError(url, status, last_error)

    def get(self, url: str, **kwargs) -> Fetched:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> Fetched:
        return self.request("POST", url, **kwargs)
