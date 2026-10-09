"""İnovasyon sinyalleri: USPTO patentleri (PatentsView) ve GitHub aktivitesi."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from radar.quality import SourceReport, Status
from radar.sources.base import Context

PATENTSVIEW = "https://search.patentsview.org/api/v1/patent/"


class Patents:
    KEY, TITLE, TIER, ROADS = "uspto", "USPTO patentleri (PatentsView)", 1, [3]

    @staticmethod
    def run(ctx: Context, rep: SourceReport) -> None:
        key = os.environ.get("PATENTSVIEW_API_KEY")
        if not key:
            rep.add("API anahtarı", Status.WARN,
                    "PATENTSVIEW_API_KEY yok. Ücretsiz anahtar: https://patentsview.org/apis/keyrequest — "
                    "alınınca GitHub secret olarak eklenecek")
            return
        query = {"_and": [{"assignees.assignee_organization": "NVIDIA Corporation"},
                          {"_gte": {"patent_date": f"{ctx.today.year - 1}-01-01"}}]}
        data = ctx.client.get(PATENTSVIEW, headers={"X-Api-Key": key},
                              params={"q": json.dumps(query), "f": json.dumps(["patent_id", "patent_date", "patent_title"]),
                                      "o": json.dumps({"size": 100})}).json()
        patents = data.get("patents") or []
        rep.expect_range("NVIDIA: son dönem patent", len(patents), 10, 100)
        dates = [p["patent_date"] for p in patents if p.get("patent_date")]
        if dates:
            rep.expect_fresh("Güncellik", datetime.fromisoformat(max(dates)).replace(tzinfo=timezone.utc), 21)
        rep.sample = patents[:3]


class GitHubActivity:
    KEY, TITLE, TIER, ROADS = "github", "GitHub aktivitesi", 2, [3]

    @staticmethod
    def run(ctx: Context, rep: SourceReport) -> None:
        token = os.environ.get("GITHUB_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        sample = {}
        for org in ["NVIDIA", "microsoft", "apple"]:
            repos = ctx.client.get(f"https://api.github.com/orgs/{org}/repos",
                                   params={"sort": "pushed", "per_page": 30}, headers=headers).json()
            pushed = [datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) for r in repos if r.get("pushed_at")]
            rep.expect_range(f"{org}: depo sayısı (ilk sayfa)", len(repos), 10, 30)
            if pushed:
                rep.expect_fresh(f"{org}: son push", max(pushed), 3)
            sample[org] = [r["full_name"] for r in repos[:3]]
        rep.add("Kapsam notu", Status.INFO, "Yalnızca açık kaynak yapan şirketlerde anlamlı; şirket ↔ organizasyon eşleştirmesi 3. aşamada")
        rep.sample = sample
