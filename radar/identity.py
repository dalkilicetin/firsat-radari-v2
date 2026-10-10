"""Kimlik katmanı: her şirketi (CIK) sembol geçmişi, Nasdaq üyelik dönemi ve fiyat kaynağıyla birleştirir.

Nasdaq üyeliği (hayatta kalan yanılgısı olmadan):
- Bugün Nasdaq'ta olanlar: fiyat verisinin başladığı günden bugüne. Geçmişte başka borsadan geçtiyse
  (o borsanın Form 25-NSE'si ya da şirketin kendi verdiği Form 25, örn. PLTR 2024), üyelik geçiş tarihinde başlar.
- Nasdaq'tan çıkanlar: Form 25-NSE'yi Nasdaq'ın kendisi dosyalar (dosya no öneki NASDAQ_FILER). Bugün Nasdaq'ta
  olmayan ve 2015 sonrası böyle bir bildirimi olan şirketlerin üyeliği son bildirim tarihinde biter.
  Not: 25-NSE adi hisse dışındaki menkul kıymetler için de verilebilir; fiyat verisinin kesilmesiyle birlikte
  değerlendirilir (price_end).
Çıkış anındaki değer (delisting return): çıkıştan önceki 1 yıl / sonraki 90 gün içinde 8-K Madde 1.03 (iflas)
varsa son değer 0 kabul edilir; aksi halde son gözlenen fiyat (satın almalarda anlaşma fiyatına yakındır).
Sembol geçmişi Form 4'lerden (şirketin kendi bildirdiği işlem sembolü) çıkarılır; semboller yeniden
kullanılabildiği için her sembol bir tarih aralığına bağlıdır.
"""

from __future__ import annotations

import pandas as pd

from radar import archive, config

NASDAQ_FILER = "0001354457"
NYSE_FILERS = {"0000876661", "0001143313", "0001143362"}
START = pd.Timestamp("2015-01-01")


def ticker_history(insider: pd.DataFrame) -> pd.DataFrame:
    """(cik, sembol) → ilk/son görülme. Aynı sembolü farklı şirketler farklı dönemlerde kullanabilir."""
    df = insider.dropna(subset=["issuer_cik"])
    df = df[df.ticker.str.fullmatch(r"[A-Z][A-Z0-9.\-]{0,6}", na=False) & ~df.ticker.isin(["NONE", "NA", "N/A"])]
    hist = (df.groupby(["issuer_cik", "ticker"]).filing_date.agg(first_seen="min", last_seen="max", n="size")
            .reset_index().rename(columns={"issuer_cik": "cik"}))
    hist["cik"] = hist.cik.astype("int64")
    return hist[hist.n >= 2]  # tek seferlik yazım hatalarını ele


def exchange_exits(filings: pd.DataFrame) -> pd.DataFrame:
    """Form 25-NSE (borsa dosyalar) ve Form 25 (şirket kendisi dosyalar) kayıtları."""
    d = filings[filings.form.isin(["25-NSE", "25"])][["cik", "form", "filing_date", "accession"]].copy()
    prefix = d.accession.str[:10]
    d["exchange"] = prefix.map(lambda p: "NASDAQ" if p == NASDAQ_FILER else "NYSE" if p in NYSE_FILERS else "OTHER")
    d.loc[d.form == "25", "exchange"] = "ISSUER"  # şirketin kendi başvurusu: hangi borsadan olduğu belirsiz
    return d


def build() -> dict[str, pd.DataFrame]:
    universe = pd.read_csv(config.STATE_DIR / "universe.csv", dtype={"cik": "Int64"})
    filings = archive.load("filings", columns=["cik", "form", "filing_date", "accession", "name", "tickers", "items"])
    insider = archive.load("insider", columns=["issuer_cik", "ticker", "filing_date"])
    prices = archive.load("prices", columns=["symbol", "date", "close", "volume"])
    ftd = archive.load("ftd", columns=["settle_date", "symbol", "price"])

    hist = ticker_history(insider)
    exits = exchange_exits(filings)
    names = filings.drop_duplicates("cik", keep="last").set_index("cik").name

    # A) Bugün Nasdaq'ta olanlar
    first_price = prices.groupby("symbol").date.min()
    cur = universe.dropna(subset=["cik"]).copy()
    cur["cik"] = cur.cik.astype("int64")
    cur["start"] = cur.symbol.map(first_price).fillna(pd.Timestamp.today().normalize())
    transfer = exits[exits.exchange != "NASDAQ"].groupby("cik").filing_date.max()
    moved = cur.cik.map(transfer)
    cur["transferred_from_other"] = moved.notna() & (moved > cur.start + pd.Timedelta(days=30))
    cur["start"] = cur.start.where(~cur.transferred_from_other, moved)
    # Birden çok hisse sınıfı aynı CIK'ı paylaşır (GOOG/GOOGL): son 1 yılın işlem hacmi en yüksek sınıf ana sınıftır.
    recent = prices[prices.date >= prices.date.max() - pd.Timedelta(days=365)]
    dollar_vol = (recent.close * recent.volume).groupby(recent.symbol).median()
    cur["dollar_volume"] = cur.symbol.map(dollar_vol).fillna(0)
    cur = cur.sort_values("dollar_volume", ascending=False).drop_duplicates("cik")
    # Kapalı uçlu fonlar şirket değildir.
    cur = cur[~cur.name.str.contains("Closed End Fund", case=False, na=False)]
    cur = cur.assign(end=pd.NaT, price_source="yahoo", status="aktif", bankrupt=False)[
        ["cik", "symbol", "name", "start", "end", "price_source", "status", "transferred_from_other", "bankrupt"]]

    # B) 2015 sonrası Nasdaq'tan çıkanlar
    nasdaq_exit = exits[(exits.exchange == "NASDAQ") & (exits.filing_date >= START)].groupby("cik").filing_date.max()
    gone = nasdaq_exit[~nasdaq_exit.index.isin(cur.cik)].rename("end").reset_index()
    # Çıkış anında kullanılan sembol: çıkıştan önce/30 gün sonrasına kadar en son görülen sembol.
    h = hist.merge(gone, on="cik")
    h = h[h.first_seen <= h.end + pd.Timedelta(days=30)].sort_values("last_seen")
    sym_at_exit = h.groupby("cik").agg(symbol=("ticker", "last"), sym_first=("first_seen", "min"))
    gone = gone.merge(sym_at_exit, on="cik", how="left")
    gone["name"] = gone.cik.map(names)

    # Fiyat kaynağı: FTD (seyrek); sembol aralığı içinde, çıkıştan en fazla 10 gün sonrasına kadar.
    ftd = ftd[ftd.price > 0]
    by_sym = ftd.groupby("symbol").settle_date
    gone["ftd_first"] = gone.symbol.map(by_sym.min())
    gone["ftd_last"] = gone.symbol.map(by_sym.max())
    gone["start"] = gone[["sym_first", "ftd_first"]].max(axis=1).clip(lower=START)
    # İflas: çıkıştan önceki 1 yıl ya da sonraki 90 gün içinde 8-K Madde 1.03.
    bk = filings[(filings.form == "8-K") & filings["items"].fillna("").str.contains(r"\b1\.03\b")][["cik", "filing_date"]]
    bk = bk.merge(gone[["cik", "end"]], on="cik")
    bk = bk[(bk.filing_date >= bk.end - pd.Timedelta(days=365)) & (bk.filing_date <= bk.end + pd.Timedelta(days=90))]
    gone["bankrupt"] = gone.cik.isin(bk.cik)
    gone["price_source"] = "ftd"
    gone["status"] = "çıktı"
    gone["transferred_from_other"] = False
    # Sembolü bilinmeyenler çoğunlukla hisse dışı menkul kıymetlerdir (tahvil, ETN); Form 4 vermeyen yabancı
    # şirketler de bu gruba düşer (bilinen sınırlama).
    gone = gone[gone.symbol.notna()]
    gone = gone[["cik", "symbol", "name", "start", "end", "price_source", "status", "transferred_from_other", "bankrupt"]]

    securities = pd.concat([cur, gone], ignore_index=True)
    return {"securities": securities, "tickers": hist, "exits": exits}


def summarize(tables: dict[str, pd.DataFrame]) -> list[str]:
    s = tables["securities"]
    gone = s[s.status == "çıktı"]
    lines = [
        f"Bugün Nasdaq'ta (CIK'li): {int((s.status == 'aktif').sum()):,}",
        f"  başka borsadan Nasdaq'a geçmiş: {int(s.transferred_from_other.sum()):,}",
        f"2015 sonrası Nasdaq'tan çıkan (sembolü bilinen hisseler): {len(gone):,}",
        f"  iflasla çıkan (8-K 1.03): {int(gone.bankrupt.sum()):,}",
        f"Çıkış yılları: {gone.end.dt.year.value_counts().sort_index().to_dict()}",
    ]
    return lines


if __name__ == "__main__":
    t = build()
    out = config.DATA_DIR / "derived"
    out.mkdir(parents=True, exist_ok=True)
    for name, df in t.items():
        df.to_parquet(out / f"identity_{name}.parquet", index=False)
    print("\n".join(summarize(t)))
