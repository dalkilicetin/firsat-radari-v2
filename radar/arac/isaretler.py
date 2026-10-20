"""Analiz aracının işaretleri: 6 olumlu işaret, kesin ret ve dikkat işaretleri (analiz_araci_plani.md, bölüm 3–4).

Her değer Cuma t kararı içindir ve yalnızca perşembe 16:00 (New York) itibarıyla bilinen veriyle hesaplanır
(duzenek.kullanilabilir). Eşikler önceden yazılmıştır; ağırlıklar 2013–2022'de ölçülür (otopsi/benzer analizi).

Olumlu işaretler (bool):
1. yukselis       — 12-1 ay getirisi evrenin en iyi %20'sinde VE 52 haftalık zirveye en fazla %25 uzak
2. is_iyilesiyor  — son raporda satışlar geçen yılın aynı dönemine göre ≥ %20 arttı VE büyüme bir önceki rapora göre hızlandı
3. dipten_kalkti  — fiyat 52 haftalık dibin en az 2 katı
4. sektor         — hissenin sektör ETF'i son 1 yılda (12-1 ay) S&P 500'den iyi gitti
5. iceriden       — son 90 günde en az 2 farklı yönetici/ortak borsadan hisse aldı, ya da yeni 13D (aktivist) / yeni 13G (≥ %5 ortak)
6. yakin_haber    — son periyodik rapordan bu yana 56–100 gün geçti (sonraki bilanço ~6 hafta içinde bekleniyor)

Kesin ret (bool): devamlilik (son 10-K'da devamlılık şüphesi), gec_rapor (son 180 günde NT 10-K/10-Q),
cikarilma (son 180 günde 8-K madde 3.01: borsa kotasyon uyarısı).
Dikkat (bool): hisse_basma (son 90 günde hisse satışı izahnamesi/kayıt beyanı ya da 12 ayda hisse sayısı ≥ %20 arttı),
ters_bolunme (son 365 günde), nakit_sikintisi (faaliyetler nakit yakıyor ve nakit < 4 çeyreklik yakım),
dusen_bicak (zirveden ≥ %70 aşağıda ve 26 haftalık ortalamanın altında), ucuzluk_tuzagi (satışlar ≥ %20 düşüyor ve zarar büyüyor).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from radar import archive, config
from radar.arac.duzenek import Duzenek, duvar_saati, kullanilabilir
from radar.research import fundamentals, panel
from radar.research.pit import pit
from radar.research.road1 import REVENUE, by_filing, balance

CACHE = config.DATA_DIR / "derived" / "arac"
OLUMLU = ["yukselis", "is_iyilesiyor", "dipten_kalkti", "sektor", "iceriden", "yakin_haber"]
KESIN_RET = ["devamlilik", "gec_rapor", "cikarilma"]
DIKKAT = ["hisse_basma", "ters_bolunme", "nakit_sikintisi", "dusen_bicak", "ucuzluk_tuzagi"]
FIN_MAX_AGE = 200  # gün: iki çeyrekten eski rapor yok sayılır

CASH = ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "CashAndCashEquivalents"]
SHORT_INV = ["ShortTermInvestments", "MarketableSecuritiesCurrent"]
NET_INCOME = ["NetIncomeLoss", "ProfitLossAttributableToOwnersOfParent"]
OCF = ["NetCashProvidedByUsedInOperatingActivities"]
NT_FORMS = {"NT 10-K", "NT 10-Q", "NT 20-F", "NT 10-K/A", "NT 10-Q/A", "NT 11-K"}
D13 = {"SC 13D", "SCHEDULE 13D"}
G13 = {"SC 13G", "SCHEDULE 13G"}
ISSUE = {"424B1", "424B3", "424B4", "424B5", "424B7", "S-1", "S-3", "F-1", "F-3"}  # 424B2: çoğunlukla borç senedi
PERIODIC = {"10-K", "10-Q", "20-F", "40-F", "10-K/A", "10-Q/A"}


@dataclass
class Kaynaklar:
    """İşaretlerin ham girdileri. `kes(T)` yalnızca Cuma T'de kullanılabilir olanları bırakır (sızıntı testi)."""
    finans: pd.DataFrame     # temel.finans()
    filings: pd.DataFrame    # cik, form, items, gun (kullanılabilir Cuma)
    ihrac: pd.DataFrame
    insider: pd.DataFrame
    tenk: pd.DataFrame
    splits: pd.DataFrame

    @classmethod
    def yukle(cls, d: Duzenek) -> "Kaynaklar":
        f = archive.load("filings", columns=["cik", "form", "items", "accepted"])
        f = f.assign(cik=f.cik.astype(str), gun=kullanilabilir(f.accepted).to_numpy())
        ih = archive.load("ihrac_belgeleri", columns=["cik", "form", "accepted"])
        ih = ih.assign(cik=ih.cik.astype(str), gun=kullanilabilir(ih.accepted).to_numpy())
        cols = ["accession", "issuer_cik", "owner_cik", "owner_name", "relationship", "code", "acq_disp", "shares", "price",
                "available_date"]
        ins = archive.load("insider", columns=cols)
        try:  # toplu dosyası henüz çıkmamış günler (haftalık tarama)
            rec = archive.load("insider_guncel", columns=cols)
            ins = pd.concat([ins, rec[~rec.accession.isin(set(ins.accession))]], ignore_index=True)
        except Exception:
            pass
        ins = ins[(ins.code == "P") & (ins.acq_disp == "A")]
        ins = ins.assign(owner_cik=ins.owner_cik.astype("Int64").astype(str).where(ins.owner_cik.notna(), ins.owner_name))
        ins = ins.assign(cik=ins.issuer_cik.astype("Int64").astype(str), deger=ins.shares * ins.price,
                         gun=kullanilabilir(ins.available_date, saatli=False).to_numpy())
        tk = archive.load("tenk", columns=["cik", "accepted", "going_concern"])
        tk = tk.assign(cik=tk.cik.astype(str), gun=kullanilabilir(tk.accepted).to_numpy())
        sp = panel.split_events()
        # Bölünme yürürlük günü (tarih) biliniyor; günün sonunda kullanılabilir sayılır.
        sp = sp.assign(cik=sp.cik.astype(str), gun=kullanilabilir(sp.date, saatli=False).to_numpy())
        fin = d.finans.assign(gun=kullanilabilir(d.finans.accepted).to_numpy())
        return cls(fin, f, ih, ins, tk, sp)

    def kes(self, T: pd.Timestamp) -> "Kaynaklar":
        return Kaynaklar(*(x[x.gun <= T] for x in (self.finans, self.filings, self.ihrac, self.insider, self.tenk, self.splits)))


def _son_gunlerde(ev: pd.DataFrame, dates, cols, gun_sayisi: int) -> pd.DataFrame:
    """Olay (cik, gun) → Cuma t'de son `gun_sayisi` gün içinde kullanılabilir olmuş olay var mı."""
    ev = ev[ev.cik.isin(set(cols))]
    w = ev.groupby(["gun", "cik"]).size().unstack("cik").reindex(index=dates, columns=cols).fillna(0)
    return w.rolling(int(np.ceil(gun_sayisi / 7)), min_periods=1).sum() > 0


def _deger(long: pd.DataFrame, dates, cols, max_age=FIN_MAX_AGE) -> pd.DataFrame:
    """(cik, gun, value) → Cuma t itibarıyla son değer (gun: kullanılabilir Cuma)."""
    x = long.assign(cik=long.cik.astype(str), date=long.gun - pd.Timedelta(days=1))
    return pit(x[["cik", "date", "value"]], dates, cols, max_age)


def fiyat_olculeri(d: Duzenek, etf: pd.DataFrame) -> dict[str, pd.DataFrame]:
    P = d.persembe["price"]
    hi, lo = P.rolling(52, min_periods=40).max(), P.rolling(52, min_periods=40).min()
    mom = P.shift(4) / P.shift(52) - 1
    e12 = etf.shift(4) / etf.shift(52) - 1
    sek = pd.DataFrame({c: e12[s] if s in e12 else np.nan for c, s in d.sektor_etf.items()}, index=P.index)
    return {"momentum_12_1": mom, "zirve_uzaklik": P / hi - 1, "dip_kat": P / lo,
            "ort26_uzaklik": P / P.rolling(26, min_periods=20).mean() - 1, "getiri_26h": P / P.shift(26) - 1,
            "sektor_12_1": sek, "spy_12_1": pd.DataFrame(np.broadcast_to(e12["SPY"].to_numpy()[:, None], P.shape), index=P.index,
                                                         columns=P.columns)}


def temel_olculer(k: Kaynaklar, dates, cols, hisse: pd.DataFrame) -> dict[str, pd.DataFrame]:
    fin = fundamentals.plain(k.finans)
    fin = fin[fin.uom.isin(["USD", "shares"])]
    rev = by_filing(fin, REVENUE, [1, 4])
    rev = rev.assign(cik=rev.cik.astype(str), g=(rev.cur / rev.prev - 1).where(rev.prev > 0).clip(-1, 10))
    rev = rev.merge(fin.drop_duplicates("adsh")[["adsh", "gun"]], on="adsh").sort_values(["cik", "gun"])
    prev_g = rev.groupby("cik").g.shift(1)
    prev_gun = rev.groupby("cik").gun.shift(1)
    rev["ivme"] = (rev.g - prev_g).where((rev.gun - prev_gun).dt.days <= 200)
    ni = by_filing(fin, NET_INCOME, [1, 4])
    ni = ni.merge(fin.drop_duplicates("adsh")[["adsh", "gun"]], on="adsh")
    cash = balance(fin, CASH).rename(columns={"value": "nakit"})
    sti = balance(fin, SHORT_INV).rename(columns={"value": "yatirim"})
    o = fin[fin.tag.isin(OCF) & fin.qtrs.between(1, 4)]
    o = o[o.ddate == o.groupby("adsh").ddate.transform("max")]
    o = o.sort_values("qtrs").groupby(["adsh", "cik"]).agg(v=("value", "last"), q=("qtrs", "last")).reset_index()
    o["value"] = o.v / o.q  # çeyreklik ortalama faaliyet nakit akışı
    gun = fin.drop_duplicates("adsh").set_index("adsh").gun
    for x in (cash, sti, o):
        x["gun"] = x.adsh.map(gun)
    out = {
        "gelir_buyume": _deger(rev.rename(columns={"g": "value"}), dates, cols),
        "gelir_ivme": _deger(rev.rename(columns={"ivme": "value"}), dates, cols),
        "net_kar": _deger(ni.rename(columns={"cur": "value"}), dates, cols),
        "net_kar_once": _deger(ni.rename(columns={"prev": "value"}), dates, cols),
        "nakit": _deger(cash.rename(columns={"nakit": "value"}), dates, cols).fillna(0)
                 + _deger(sti.rename(columns={"yatirim": "value"}), dates, cols).fillna(0),
        "faaliyet_nakit_ceyrek": _deger(o, dates, cols),
        "hisse_artisi_12a": hisse / hisse.shift(52) - 1,
    }
    out["nakit"] = out["nakit"].where(out["faaliyet_nakit_ceyrek"].notna())
    return out


def olay_olculeri(k: Kaynaklar, dates, cols) -> dict[str, pd.DataFrame]:
    f = k.filings
    items = f["items"].fillna("")
    ins = k.insider
    buy = ins[ins.relationship.fillna("").str.contains("Director|Officer|TenPercentOwner")]
    pairs = buy[["cik", "owner_cik", "gun"]].drop_duplicates()
    buyers = _farkli_alici(pairs, dates, cols, 90)
    tk = k.tenk.assign(value=k.tenk.going_concern.astype(float))
    per = f[f.form.isin(PERIODIC)].groupby(["cik", "gun"]).size().reset_index()[["cik", "gun"]]
    epoch = pd.Timestamp("1970-01-01")
    son_rapor = per.assign(value=(per.gun - epoch).dt.days.astype(float))  # son raporun kullanılabilir Cuma'sı (gün)
    son = _deger(son_rapor, dates, cols, 400)
    gecen = pd.DataFrame(np.broadcast_to((dates - epoch).days.to_numpy(float)[:, None], son.shape), index=dates, columns=cols) - son
    rs = k.splits[k.splits.ratio <= 1 / panel.SPLIT_MIN]
    return {
        "alici_sayisi_90g": buyers,
        "aktivist_13d": _son_gunlerde(f[f.form.isin(D13)], dates, cols, 90),
        "yeni_13g": _son_gunlerde(f[f.form.isin(G13)], dates, cols, 90),
        "son_rapordan_gun": gecen,
        "devamlilik": _deger(tk, dates, cols, 400).fillna(0) > 0,
        "gec_rapor": _son_gunlerde(f[f.form.isin(NT_FORMS)], dates, cols, 180),
        "cikarilma": _son_gunlerde(f[(f.form == "8-K") & items.str.contains(r"\b3\.01\b")], dates, cols, 180),
        "ihrac_90g": _son_gunlerde(k.ihrac[k.ihrac.form.isin(ISSUE)], dates, cols, 90),
        "ters_bolunme": _son_gunlerde(rs, dates, cols, 365),
    }


def _farkli_alici(pairs: pd.DataFrame, dates, cols, gun_sayisi: int) -> pd.DataFrame:
    """Cuma t'de son `gun_sayisi` günde (hafta penceresi, _son_gunlerde ile aynı) alımı kullanılabilir olmuş farklı alıcı sayısı."""
    win = int(np.ceil(gun_sayisi / 7))
    pairs = pairs[pairs.cik.isin(set(cols))]
    i = dates.get_indexer(pd.DatetimeIndex(pairs.gun))
    pairs = pairs.assign(i=i)[i >= 0]
    spread = pd.concat([pairs.assign(i=pairs.i + k) for k in range(win)], ignore_index=True)
    spread = spread[spread.i < len(dates)].drop_duplicates(["cik", "owner_cik", "i"])
    n = spread.groupby(["i", "cik"]).size().unstack("cik")
    return n.reindex(index=range(len(dates)), columns=cols).fillna(0).set_axis(dates, axis=0)


def hesapla(d: Duzenek, k: Kaynaklar, etf: pd.DataFrame | None = None) -> dict[str, pd.DataFrame]:
    dates, cols = d.tarihler, d.sutunlar
    etf = d.etf_persembe if etf is None else etf
    o = fiyat_olculeri(d, etf) | temel_olculer(k, dates, cols, d.hisse_sayisi) | olay_olculeri(k, dates, cols)
    ev = d.evren
    mom_sira = o["momentum_12_1"].where(ev).rank(axis=1, pct=True)
    o["momentum_sira"] = mom_sira
    o["yukselis"] = (mom_sira >= 0.80) & (o["zirve_uzaklik"] >= -0.25)
    o["is_iyilesiyor"] = (o["gelir_buyume"] >= 0.20) & (o["gelir_ivme"] > 0)
    o["dipten_kalkti"] = o["dip_kat"] >= 2.0
    o["sektor"] = o["sektor_12_1"] > o["spy_12_1"]
    o["iceriden"] = (o["alici_sayisi_90g"] >= 2) | o["aktivist_13d"] | o["yeni_13g"]
    o["yakin_haber"] = o["son_rapordan_gun"].between(56, 100)
    o["hisse_basma"] = o["ihrac_90g"] | (o["hisse_artisi_12a"] >= 0.20)
    burn = o["faaliyet_nakit_ceyrek"]
    o["nakit_sikintisi"] = (burn < 0) & (o["nakit"] < -4 * burn)
    o["dusen_bicak"] = (o["zirve_uzaklik"] <= -0.70) & (o["ort26_uzaklik"] < 0)
    o["ucuzluk_tuzagi"] = (o["gelir_buyume"] <= -0.20) & (o["net_kar"] < 0) & (o["net_kar"] < o["net_kar_once"])
    o["olumlu_sayisi"] = sum(o[n].astype(int) for n in OLUMLU)
    o["kesin_ret"] = o["devamlilik"] | o["gec_rapor"] | o["cikarilma"]
    o["dikkat_sayisi"] = sum(o[n].astype(int) for n in DIKKAT)
    return o


def kaydet(o: dict[str, pd.DataFrame], ad: str = "isaretler") -> None:
    path = CACHE / ad
    path.mkdir(parents=True, exist_ok=True)
    for n, df in o.items():
        df.astype("float32").to_parquet(path / f"{n}.parquet")


def yukle(adlar: list[str] | None = None, ad: str = "isaretler") -> dict[str, pd.DataFrame]:
    path = CACHE / ad
    names = adlar or [p.stem for p in path.glob("*.parquet")]
    return {n: pd.read_parquet(path / f"{n}.parquet") for n in names}
