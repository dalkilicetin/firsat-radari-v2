"""Reddit geçmişi (açık arşiv, anahtarsız): finans alt-forumlarında hisse × ay toplu sayıları.

Kaynak: Watchful1'in alt-forum bazında ayrılmış Pushshift arşivi (en büyük 40 bin alt-forum, başlangıç → 2023 sonu),
academictorrents 56aa49f9653ba545f48df2e33679f014d2829c10. Torrent içinden yalnızca istenen dosya indirilir (aria2c).
Gizlilik ve Reddit kuralları: HAM METİN VE KULLANICI ADI SAKLANMAZ. Arşive yalnızca toplu sayılar yazılır:
- month_cik: ay × şirket → gönderi sayısı, anılma, puan toplamı, yorum toplamı, olumlu / olumsuz / öfkeli gönderi sayısı
- month_total: ay → alt-forumdaki toplam gönderi (normalleştirme için)
Sembol tanıma: $NVDA biçimi her zaman; büyük harfli çıplak sembol yalnızca 3+ harfliyse ve yaygın kelime değilse;
sembol o tarihte o şirkete aitse (kimlik katmanındaki üyelik aralığı).
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from radar.backfill.base import Dataset, Loaded
from radar.http import HttpClient
from radar.quality import SourceReport, Status

TORRENT = "https://academictorrents.com/download/56aa49f9653ba545f48df2e33679f014d2829c10.torrent"
SUBREDDITS = ["wallstreetbets", "stocks", "investing", "StockMarket", "pennystocks", "options"]

STOP = set("""THE AND FOR YOLO CEO CFO CTO IPO ETF USA GDP FED SEC IMO LOL ATH EPS ITM OTM WSB EOD ALL ARE CAN NOW NEW ONE OUT
BIG GOOD LOVE FUN REAL EDIT TLDR PSA USD EUR API FOMO HODL MOON BUY SELL HOLD PUT PUTS CALL CALLS LONG SHORT GAIN LOSS
YES NOT YOU HIS HER HAS WAS WHO WHY HOW WHAT WHEN THIS THAT WITH FROM JUST LIKE ANY GET GOT TOP LOW HIGH RED GREEN
CASH DEBT FREE EVER NEXT LAST BEST WELL VERY MUCH MOST SOME SAME DAY WEEK YEAR TIME OPEN NYSE NASDAQ IRS CPI PPI FOMC
IMHO DOW OTC LLC INC CORP ROI ROE EBIT RSI MACD SMA EMA VWAP IRA LMAO WTF FYI DIY TBH OMG ELI LFG RIP GUH OPEX""".split())
POS = set("moon mooning rocket calls bullish buy buying long tendies undervalued squeeze breakout beat upgrade gains rally rip printing"
          .split()) | {"🚀"}
NEG = set("puts bearish sell selling short dump dumping scam fraud bagholder bagholding crash overvalued bankrupt dilution downgrade "
          "miss rugpull tanking dead".split())
ANGRY = set("fuck fucking fucked shit shitty crap damn wtf trash garbage idiot hate rigged scam clown".split())
WORD = re.compile(r"[a-z]+|🚀")
CASHTAG = re.compile(r"\$([A-Za-z]{1,5})\b")
BARE = re.compile(r"\b([A-Z]{3,5})\b")


def tickers_in(text: str, known: set[str]) -> set[str]:
    out = {m.upper() for m in CASHTAG.findall(text) if m.upper() in known}
    out |= {m for m in BARE.findall(text) if m in known and m not in STOP}
    return out


def tone(text: str) -> tuple[bool, bool, bool]:
    words = set(WORD.findall(text.lower()))
    return bool(words & POS), bool(words & NEG), bool(words & ANGRY)


class RedditArchive(Dataset):
    name = "reddit_arsiv"
    title = "Reddit finans alt-forumları — hisse × ay toplu sayıları (açık arşiv, 2005→2023)"
    max_parallel = 2

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"{s}_submissions" for s in SUBREDDITS]

    def _download(self, partition: str, work: Path) -> Path:
        tor = work / "a.torrent"
        subprocess.run(["curl", "-sSL", "-o", str(tor), TORRENT], check=True, timeout=300)
        listing = subprocess.run(["aria2c", "--show-files", str(tor)], capture_output=True, text=True, check=True).stdout
        idx = None
        for line in listing.splitlines():
            m = re.match(r"\s*(\d+)\|(.+)$", line)
            if m and m.group(2).strip().endswith(f"/{partition}.zst"):
                idx = m.group(1)
        if idx is None:
            raise RuntimeError(f"torrent içinde {partition}.zst bulunamadı")
        subprocess.run(["aria2c", f"--select-file={idx}", "--seed-time=0", "--file-allocation=none", "--bt-stop-timeout=900",
                        "--max-connection-per-server=8", "-d", str(work), str(tor)], check=True, timeout=4 * 3600)
        return next(work.rglob(f"{partition}.zst"))

    def load(self, client: HttpClient, partition: str) -> Loaded:
        import zstandard
        from radar.identity import build
        sec = build()["securities"][["cik", "symbol", "start", "end"]].dropna(subset=["symbol"])
        windows = defaultdict(list)
        for r in sec.itertuples():
            windows[str(r.symbol).upper()].append((int(r.cik), r.start, r.end))
        known = set(windows)
        agg = defaultdict(lambda: [0, 0, 0, 0, 0, 0, 0])  # gönderi, anılma, puan, yorum, olumlu, olumsuz, öfkeli
        totals = defaultdict(int)
        lines = bad = 0
        with tempfile.TemporaryDirectory(dir=".") as tmp:
            path = self._download(partition, Path(tmp))
            with path.open("rb") as fh:
                reader = io.TextIOWrapper(zstandard.ZstdDecompressor(max_window_size=2 ** 31).stream_reader(fh),
                                          encoding="utf-8", errors="ignore")
                for line in reader:
                    lines += 1
                    try:
                        o = json.loads(line)
                        ts = datetime.fromtimestamp(int(float(o["created_utc"])), tz=timezone.utc)
                    except (ValueError, KeyError, TypeError):
                        bad += 1
                        continue
                    if ts.year < 2009:
                        continue
                    month = pd.Timestamp(ts.year, ts.month, 1)
                    totals[month] += 1
                    text = f"{o.get('title') or ''} {o.get('selftext') or ''}"
                    found = tickers_in(text, known)
                    if not found:
                        continue
                    p, n, a = tone(text)
                    day = pd.Timestamp(ts.date())
                    for sym in found:
                        cik = next((c for c, s, e in windows[sym]
                                    if (pd.isna(s) or s <= day) and (pd.isna(e) or day <= e)), None)
                        if cik is None:
                            continue
                        v = agg[(month, cik)]
                        v[0] += 1
                        v[1] += len(CASHTAG.findall(text)) + text.count(sym)
                        v[2] += int(o.get("score") or 0)
                        v[3] += int(o.get("num_comments") or 0)
                        v[4] += p; v[5] += n; v[6] += a
        sub = partition.rsplit("_", 1)[0]
        rows = [("month_cik", sub, m, c, *v) for (m, c), v in agg.items()]
        rows += [("month_total", sub, m, None, t, 0, 0, 0, 0, 0, 0) for m, t in totals.items()]
        df = pd.DataFrame(rows, columns=["kind", "subreddit", "date", "cik", "posts", "mentions", "score", "comments",
                                         "pos", "neg", "angry"])
        df["cik"] = df.cik.astype("Int64")
        return Loaded(df, [TORRENT + f" ({partition}.zst; yalnızca toplu sayılar saklanır)"],
                      {"lines": lines, "bad": bad, "months": len(totals)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        rep.expect_min_ratio("Okunabilen satır", notes["lines"] - notes["bad"], max(notes["lines"], 1), 0.99, 0.95)
        rep.add("Ay sayısı", Status.INFO, str(notes["months"]))
        mc = df[df.kind == "month_cik"]
        top = mc.groupby("cik").posts.sum().nlargest(8)
        rep.add("En çok anılan şirketler (CIK)", Status.INFO, ", ".join(f"{c}:{n}" for c, n in top.items()))
        rep.add("Şirket-ay satırı", Status.OK if len(mc) > 100 else Status.WARN, f"{len(mc):,}")
