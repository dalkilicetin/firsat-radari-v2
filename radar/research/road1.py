"""1. yol (sayısal kısım): şirketin yönü — büyüme, marj, yatırım ve kazanç kalitesi (XBRL).

Büyüme oranları her raporun kendi içindeki geçen yıl karşılaştırmasından hesaplanır (aynı rapor = aynı
muhasebe tanımı) ve rapor SEC'e kabul edildikten sonraki ilk Cuma'dan itibaren kullanılır.
10-K metinlerine dayalı kısım (iş tanımı, Lazy Prices) metin veri seti yüklendikten sonra eklenecek.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive
from radar.research import fundamentals
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit

REVENUE = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
           "RevenueFromContractWithCustomerIncludingAssessedTax", "Revenue"]


def load_fin() -> pd.DataFrame:
    fin = fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "uom"])
    return fin[fin.uom.isin(["USD", "shares", "USD/shares"])]


def by_filing(fin: pd.DataFrame, tags: list[str], qtrs: list[int]) -> pd.DataFrame:
    """Her rapor için ilk bulunan etiketin cari dönem ve geçen yıl aynı dönem değeri."""
    d = fin[fin.tag.isin(tags) & fin.qtrs.isin(qtrs)].copy()
    d["prio"] = d.tag.map({t: i for i, t in enumerate(tags)})
    d = d.sort_values(["adsh", "prio"])
    first_tag = d.groupby("adsh").tag.transform("first")
    d = d[d.tag == first_tag]
    cur_date = d.groupby(["adsh", "qtrs"]).ddate.transform("max")
    cur = d[d.ddate == cur_date]
    gap = (cur_date - d.ddate).dt.days
    prev = d[gap.between(350, 380)]
    keys = ["adsh", "cik", "accepted", "qtrs"]
    cur = cur.groupby(keys).value.first().rename("cur")
    prev = prev.groupby(keys).value.first().rename("prev")
    out = pd.concat([cur, prev], axis=1).reset_index()
    # Çeyreklik değer varsa onu, yoksa yıllığı kullan (10-K'larda çoğunlukla yalnızca yıllık vardır).
    out = out.sort_values("qtrs").drop_duplicates("adsh", keep="first")
    return out


def balance(fin: pd.DataFrame, tags: list[str]) -> pd.DataFrame:
    d = fin[fin.tag.isin(tags) & (fin.qtrs == 0)]
    d = d[d.ddate == d.groupby("adsh").ddate.transform("max")]
    return d.groupby(["adsh", "cik", "accepted"]).value.first().reset_index()


def annual(fin: pd.DataFrame, tags: list[str]) -> pd.DataFrame:
    d = fin[fin.tag.isin(tags) & (fin.qtrs == 4)]
    d = d[d.ddate == d.groupby("adsh").ddate.transform("max")]
    return d.groupby(["adsh", "cik", "accepted"]).value.first().reset_index()


def signals(p: dict) -> dict[str, pd.DataFrame]:
    price, raw = p["price"], p["raw"]
    dates, cols = price.index, price.columns
    all_fin = load_fin()
    fin = fundamentals.plain(all_fin)
    P = lambda df, v: pit(df.rename(columns={"accepted": "date"}).assign(value=v)[["cik", "date", "value"]],
                          dates, cols, FUNDAMENTAL_MAX_AGE)

    rev = by_filing(fin, REVENUE, [1, 4])
    growth = P(rev, (rev.cur / rev.prev - 1).where(rev.prev > 0))
    gp = by_filing(fin, ["GrossProfit"], [1, 4]).merge(rev, on=["adsh", "cik", "accepted"], suffixes=("_gp", ""))
    gm_chg = P(gp, (gp.cur_gp / gp.cur - gp.prev_gp / gp.prev).where((gp.cur > 0) & (gp.prev > 0)))
    op = by_filing(fin, ["OperatingIncomeLoss"], [1, 4]).merge(rev, on=["adsh", "cik", "accepted"], suffixes=("_op", ""))
    om_chg = P(op, (op.cur_op / op.cur - op.prev_op / op.prev).where((op.cur > 0) & (op.prev > 0)))

    rev_a = annual(fin, REVENUE)
    rd = annual(fin, ["ResearchAndDevelopmentExpense"]).merge(rev_a, on=["adsh", "cik", "accepted"], suffixes=("_rd", ""))
    rd_int = P(rd, (rd.value_rd / rd.value).where(rd.value > 0))
    ocf = annual(fin, ["NetCashProvidedByUsedInOperatingActivities"])
    capex = annual(fin, ["PaymentsToAcquirePropertyPlantAndEquipment"])
    ni = annual(fin, ["NetIncomeLoss", "ProfitLoss"])
    assets = balance(fin, ["Assets"])
    shares = fundamentals.shares_outstanding(all_fin)

    fcf = ocf.merge(capex, on=["adsh", "cik", "accepted"], how="left", suffixes=("", "_cx"))
    fcf_v = P(fcf, fcf.value - fcf.value_cx.fillna(0))
    mcap = P(shares, shares.value) * raw
    acc = ni.merge(ocf, on=["adsh", "cik", "accepted"], suffixes=("_ni", "_ocf")).merge(assets, on=["adsh", "cik", "accepted"])
    accruals = P(acc, (acc.value_ni - acc.value_ocf) / acc.value)
    assets_w = P(assets, assets.value)

    return {
        "gelir_buyumesi": growth.clip(-1, 5),
        "buyume_ivmesi": (growth - growth.shift(52)).clip(-3, 3),
        "brut_marj_degisimi": gm_chg.clip(-1, 1),
        "faaliyet_marji_degisimi": om_chg.clip(-2, 2),
        "arge_yogunlugu": rd_int.clip(0, 5),
        "serbest_nakit_getirisi": (fcf_v / mcap).where(mcap > 0).clip(-2, 2),
        "kazanc_getirisi": (P(ni, ni.value) / mcap).where(mcap > 0).clip(-2, 2),
        "tahakkuklar_dusuk": -accruals.clip(-2, 2),          # düşük tahakkuk = kaliteli kazanç
        "varlik_buyumesi_dusuk": -(assets_w / assets_w.shift(52) - 1).clip(-1, 5),  # yatırım etkisi
    }


# --- 10-K metinlerine dayalı sinyaller -----------------------------------------------------------

import re
from collections import Counter
from math import sqrt

TOKEN = re.compile(r"[a-z]{3,}")
SECTIONS = ["item1", "item1a", "item7"]


def term_counts(text: str) -> Counter:
    return Counter(TOKEN.findall(str(text).lower()))


def cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return float("nan")
    small, big = (a, b) if len(a) < len(b) else (b, a)
    dot = sum(v * big.get(k, 0) for k, v in small.items())
    return dot / (sqrt(sum(v * v for v in a.values())) * sqrt(sum(v * v for v in b.values())))


def text_changes(frames) -> pd.DataFrame:
    """Her 10-K için, aynı şirketin bir önceki 10-K'sıyla bölüm bazında benzerlik (Lazy Prices).

    frames: tarih sırasıyla gelen tablolar (yıl yıl) ya da tek tablo. Bellek için her şirketin yalnızca
    son raporunun kelime sayımları tutulur.
    """
    if isinstance(frames, pd.DataFrame):
        frames = [frames]
    prev: dict = {}
    rows = []
    for tenk in frames:
        for r in tenk.sort_values("accepted").itertuples():
            cur = {s: term_counts(getattr(r, s)) for s in SECTIONS}
            rec = {"cik": r.cik, "accepted": r.accepted, "going_concern": r.going_concern,
                   "len_item1a": len(str(r.item1a))}
            p = prev.get(r.cik)
            if p is not None and (r.accepted - p["accepted"]).days < 550:
                for s in SECTIONS:
                    rec[f"sim_{s}"] = cosine(cur[s], p["counts"][s])
                rec["risk_len_growth"] = (rec["len_item1a"] / p["len_item1a"] - 1) if p["len_item1a"] > 2000 else np.nan
            rows.append(rec)
            prev[r.cik] = {"accepted": r.accepted, "counts": cur, "len_item1a": rec["len_item1a"]}
    return pd.DataFrame(rows)


def text_signals(p: dict) -> dict[str, pd.DataFrame]:
    price = p["price"]
    dates, cols = price.index, price.columns
    cols_ = ["cik", "accepted", "going_concern"] + SECTIONS
    years = sorted(archive.entries("tenk"))
    ch = text_changes(archive.load("tenk", names=[y], columns=cols_) for y in years)
    P = lambda v: pit(ch.rename(columns={"accepted": "date"}).assign(value=v)[["cik", "date", "value"]],
                      dates, cols, FUNDAMENTAL_MAX_AGE)
    sims = [P(ch[f"sim_{s}"]) for s in SECTIONS]
    return {
        "metin_benzerligi_is_tanimi": sims[0],
        "metin_benzerligi_riskler": sims[1],
        "metin_benzerligi_yonetim": sims[2],
        "metin_benzerligi_ortalama": sum(sims) / 3,
        "risk_bolumu_buyumesi_dusuk": -P(ch.risk_len_growth).clip(-1, 5),
        "devamlilik_suphesi": P(ch.going_concern.astype(float)) > 0,
    }
