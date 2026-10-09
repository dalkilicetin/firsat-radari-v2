"""Ücretsiz gündem kaynakları: Hacker News, Google News RSS, Reddit.

Reddit, kimlik bilgisi olmadan bulut sunuculardan sıklıkla engellenir; REDDIT_CLIENT_ID ve
REDDIT_CLIENT_SECRET tanımlıysa resmî (ücretsiz) OAuth erişimi kullanılır.
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context

HN = "https://hn.algolia.com/api/v1/search_by_date"
GNEWS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def parse_rss(text: str) -> list[dict]:
    root = ET.fromstring(text)
    items = []
    for it in root.iter("item"):
        try:
            published = parsedate_to_datetime(it.findtext("pubDate") or "")
        except (TypeError, ValueError):
            published = None
        items.append({"title": (it.findtext("title") or "").strip(), "published": published,
                      "source": (it.findtext("source") or "").strip(), "link": it.findtext("link") or ""})
    return items


class HackerNews:
    KEY, TITLE, TIER, ROADS = "hackernews", "Hacker News", 2, [2, 4]

    @staticmethod
    def run(ctx: Context, rep: SourceReport) -> None:
        since = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
        hits = ctx.client.get(HN, params={"query": "nvidia", "tags": "story", "hitsPerPage": 100,
                                          "numericFilters": f"created_at_i>{since}"}).json().get("hits", [])
        rep.expect_range("Son 7 gün 'nvidia' haberi", len(hits), 5, 100)
        if hits:
            rep.expect_fresh("Güncellik", datetime.fromtimestamp(max(h["created_at_i"] for h in hits), tz=timezone.utc), 2)
        start, end = int(datetime(2016, 1, 1, tzinfo=timezone.utc).timestamp()), int(datetime(2016, 2, 1, tzinfo=timezone.utc).timestamp())
        old = ctx.client.get(HN, params={"query": "nvidia", "tags": "story", "hitsPerPage": 50,
                                         "numericFilters": f"created_at_i>{start},created_at_i<{end}"}).json()
        rep.expect_range("Geçmiş veri: Ocak 2016 sonuç", old.get("nbHits", 0), 1, 10_000)
        rep.sample = [{"title": h.get("title"), "points": h.get("points")} for h in hits[:3]]


class GoogleNews:
    KEY, TITLE, TIER, ROADS = "gnews", "Google News RSS", 2, [2, 4]

    @staticmethod
    def run(ctx: Context, rep: SourceReport) -> None:
        sample = {}
        for q in ["Nvidia stock", "Apple earnings", "Nasdaq IPO"]:
            items = parse_rss(ctx.client.get(GNEWS.format(q=q.replace(" ", "+"))).text)
            rep.expect_range(f"'{q}': haber sayısı", len(items), 20, 200)
            dated = [i["published"] for i in items if i["published"]]
            rep.expect_min_ratio(f"'{q}': tarihi okunabilen", len(dated), len(items), 0.98, 0.9)
            if dated:
                rep.expect_fresh(f"'{q}': güncellik", max(dated), 2)
            titles = [i["title"] for i in items]
            rep.expect_min_ratio(f"'{q}': tekil başlık", len(set(titles)), len(titles), 0.9, 0.75)
            sample[q] = [{"title": i["title"], "source": i["source"]} for i in items[:2]]
        rep.sample = sample


class Reddit:
    KEY, TITLE, TIER, ROADS = "reddit", "Reddit", 2, [2, 4]

    @staticmethod
    def run(ctx: Context, rep: SourceReport) -> None:
        cid, secret = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
        if cid and secret:
            token = ctx.client.post("https://www.reddit.com/api/v1/access_token", auth=(cid, secret),
                                    data={"grant_type": "client_credentials"}).json()["access_token"]
            base, headers = "https://oauth.reddit.com", {"Authorization": f"bearer {token}"}
            rep.add("Erişim yöntemi", Status.INFO, "OAuth (resmî, ücretsiz)")
        else:
            base, headers = "https://www.reddit.com", {}
            rep.add("Erişim yöntemi", Status.INFO, "kimliksiz; REDDIT_CLIENT_ID/SECRET tanımlanırsa OAuth kullanılır")
        blocked_status = Status.FAIL if cid else Status.WARN
        sample = {}
        for sub in ["stocks", "investing", "wallstreetbets"]:
            try:
                data = ctx.client.get(f"{base}/r/{sub}/new.json", params={"limit": 100}, headers=headers).json()
            except FetchError as exc:
                rep.add(f"r/{sub}", blocked_status, f"erişilemedi (HTTP {exc.status})"
                        + ("" if cid else " — ücretsiz Reddit OAuth uygulaması gerekiyor"))
                continue
            posts = [c["data"] for c in data.get("data", {}).get("children", [])]
            rep.expect_range(f"r/{sub}: gönderi", len(posts), 50, 100)
            if posts:
                rep.expect_fresh(f"r/{sub}: güncellik",
                                 datetime.fromtimestamp(max(p["created_utc"] for p in posts), tz=timezone.utc), 1)
            sample[sub] = [p.get("title") for p in posts[:2]]
        rep.sample = sample
