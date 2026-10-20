"""Otopsi, benzerler, süzgeç ölçümü, sıralama ve karne (analiz_araci_plani.md, bölüm 2–5).

Girdi: radar.arac.hazirla önbelleği. Ayar dönemi 2013–2022; sınav 2023–2026 yalnızca `sinav` çağrısıyla, sıralama ayarı
reports/research/arac_ayar.json olarak commit edildikten sonra açılır.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd

from radar import config
from radar.arac import isaretler
from radar.arac.duzenek import AYAR, SINAV, VADE
from radar.research import context, sectors

R = config.ROOT / "reports" / "research"
AYAR_DOSYA = R / "arac_ayar.json"
LISTE = 10
SEKTOR_EN_FAZLA = 3
ISARET_ESIK = 4  # otopside "ilk güvenilir işaret": 6 işaretten en az 4'ü, kesin ret yok
KAZANAN_SIRA = 0.95


@dataclass
class Veri:
    tablo: dict[str, pd.DataFrame]
    isaret: dict[str, pd.DataFrame]

    @classmethod
    def yukle(cls) -> "Veri":
        path = isaretler.CACHE / "duzenek"
        tablo = {p.stem: pd.read_parquet(p) for p in path.glob("*.parquet")}
        tablo["evren"] = tablo["evren"].fillna(0).astype(bool)
        isa = isaretler.yukle()
        bools = isaretler.OLUMLU + isaretler.KESIN_RET + isaretler.DIKKAT + ["kesin_ret", "aktivist_13d", "yeni_13g"]
        for n in bools:
            if n in isa:
                isa[n] = isa[n].fillna(0).astype(bool)
        return cls(tablo, isa)

    @property
    def tarihler(self) -> pd.DatetimeIndex:
        return self.tablo["evren"].index

    @cached_property
    def sektor(self) -> pd.Series:
        cols = self.tablo["evren"].columns
        sic = sectors.load_sic().reindex(cols).fillna("")
        return pd.Series([context.etf_for_sic(c) for c in sic], index=cols)

    def kazanan(self, vade: str) -> pd.DataFrame:
        b = self.tablo[f"brut_{vade}"].where(self.tablo["evren"])
        return b.rank(axis=1, pct=True) >= KAZANAN_SIRA

    def kaybeden(self, vade: str) -> pd.DataFrame:
        n = self.tablo[f"net_{vade}"]
        return n.lt(self.tablo[f"kiyas_{vade}"]["borsa"], axis=0) & self.tablo["evren"]


def ceyrek_baslari(dates: pd.DatetimeIndex, yillar: tuple[int, int]) -> pd.DatetimeIndex:
    d = dates[(dates.year >= yillar[0]) & (dates.year <= yillar[1]) & dates.month.isin([1, 4, 7, 10])]
    return pd.DatetimeIndex(pd.Series(d).groupby([d.year, d.month]).min().to_numpy())


# --- Sıralama -------------------------------------------------------------------------------------------------

def puan(v: Veri, ayar: dict) -> pd.DataFrame:
    """Kesin ret yok + evrende: Σ ağırlık × işaret − ceza × dikkat sayısı. Eşitlik: yükseliş gücü (momentum sırası)."""
    i = v.isaret
    w = ayar["agirlik"]
    s = sum(i[n].astype(float) * w[n] for n in isaretler.OLUMLU) - ayar["dikkat_cezasi"] * i["dikkat_sayisi"].fillna(0)
    for n in ayar.get("ret", isaretler.KESIN_RET):
        s = s.mask(i[n])
    for n in ayar.get("dikkat_ret", []):
        s = s.mask(i[n])
    s = s.where(v.tablo["evren"]) + 1e-3 * i["momentum_sira"].fillna(0)
    return s


def liste(v: Veri, ayar: dict, dates: pd.DatetimeIndex | None = None, n: int = LISTE) -> dict[pd.Timestamp, list[str]]:
    p = puan(v, ayar)
    dates = p.index if dates is None else dates
    out = {}
    for t in dates:
        row = p.loc[t].dropna().sort_values(ascending=False)
        row = row[row >= ayar.get("en_az_puan", 1)]
        picks, per = [], {}
        for c in row.index:
            s = v.sektor.get(c, "")
            if per.get(s, 0) >= SEKTOR_EN_FAZLA:
                continue
            picks.append(c)
            per[s] = per.get(s, 0) + 1
            if len(picks) == n:
                break
        out[t] = picks
    return out


# --- Karne ----------------------------------------------------------------------------------------------------

def karne(v: Veri, listeler: dict[pd.Timestamp, list[str]], yillar: tuple[int, int]) -> dict:
    tab = v.tablo
    dates = pd.DatetimeIndex([t for t in listeler if yillar[0] <= t.year <= yillar[1]])
    rows = []
    kaz = {h: v.kazanan(h) for h in VADE}
    for t in dates:
        picks = listeler[t]
        if not picks:
            continue
        r = {"tarih": t, "adet": len(picks)}
        for h in VADE:
            net = tab[f"net_{h}"].loc[t, picks]
            if net.isna().all():
                continue
            borsa = tab[f"kiyas_{h}"].loc[t, "borsa"]
            esit = tab[f"kiyas_{h}"].loc[t, "esit"]
            sek = tab[f"sektor_{h}"].loc[t, picks]
            r |= {f"medyan_{h}": net.median(), f"ort_{h}": net.mean(), f"borsa_{h}": borsa,
                  f"fazla_borsa_{h}": net.mean() - borsa, f"fazla_sektor_{h}": (net - sek).mean(),
                  f"fazla_esit_{h}": net.mean() - esit, f"kazanan_orani_{h}": kaz[h].loc[t, picks].mean(),
                  f"borsayi_gecen_{h}": float(net.mean() > borsa),
                  f"masraf_{h}": (tab[f"brut_{h}"].loc[t, picks] - net).mean()}
        rows.append(r)
    w = pd.DataFrame(rows).set_index("tarih")
    # Kaçırılan / yakalanan: çeyrek başı kazananları (evrenin en iyi %5'i, 3 ay)
    q = ceyrek_baslari(v.tarihler, yillar)
    kacan, pay = [], []
    pos = {t: i for i, t in enumerate(v.tarihler)}
    for t0 in q:
        if t0 not in pos or pd.isna(tab["brut_3a"].loc[t0]).all():
            continue
        winners = kaz["3a"].loc[t0]
        winners = winners[winners].index
        weeks = v.tarihler[pos[t0]: pos[t0] + 13]
        seen = {}
        for s in weeks:
            for c in listeler.get(s, []):
                seen.setdefault(c, s)
        for c in winners:
            kacan.append(c not in seen)
            if c in seen:
                total = tab["brut_3a"].at[t0, c]
                end = tab["fiyat_cuma"].at[t0, c] * (1 + total)
                cap = end / tab["fiyat_cuma"].at[seen[c], c] - 1
                if total > 0:
                    pay.append(np.clip(cap / total, -1, 1))
    # Çeyrek başı zinciri: üst üste binmeyen 3 aylık tutuşlar
    chain = w.loc[w.index.isin(q), "ort_3a"].dropna()
    eq = (1 + chain).cumprod()
    dd = float((eq / eq.cummax() - 1).min()) if len(eq) else np.nan
    spy = (1 + w.loc[chain.index, "borsa_3a"]).cumprod()
    yrs = len(chain) / 4
    # Devir hızı
    keys = sorted(listeler)
    keys = [t for t in keys if yillar[0] <= t.year <= yillar[1]]
    weekly_new = [len(set(listeler[b]) - set(listeler[a])) for a, b in zip(keys, keys[1:])]
    qk = [t for t in keys if t in set(q)]
    q_new = [len(set(listeler[b]) - set(listeler[a])) for a, b in zip(qk, qk[1:])]
    out = {"donem": f"{yillar[0]}–{yillar[1]}", "hafta": int(len(w)),
           "medyan_3a": _m(w, "medyan_3a"), "medyan_6a": _m(w, "medyan_6a"),
           "ort_3a": _m(w, "ort_3a"), "ort_6a": _m(w, "ort_6a"),
           "borsa_3a": _m(w, "borsa_3a"), "borsa_6a": _m(w, "borsa_6a"),
           "fazla_borsa_3a": _m(w, "fazla_borsa_3a"), "fazla_borsa_6a": _m(w, "fazla_borsa_6a"),
           "fazla_sektor_3a": _m(w, "fazla_sektor_3a"), "fazla_esit_3a": _m(w, "fazla_esit_3a"),
           "fazla_sektor_6a": _m(w, "fazla_sektor_6a"), "fazla_esit_6a": _m(w, "fazla_esit_6a"),
           "kazanan_orani_3a": _m(w, "kazanan_orani_3a"), "kazanan_orani_6a": _m(w, "kazanan_orani_6a"),
           "rastgele_kazanan_orani": 1 - KAZANAN_SIRA,
           "borsayi_gecen_3a": _m(w, "borsayi_gecen_3a"), "borsayi_gecen_6a": _m(w, "borsayi_gecen_6a"),
           "tamamen_kacirilan": float(np.mean(kacan)) if kacan else None,
           "yakalanan_pay_medyan": float(np.median(pay)) if pay else None,
           "zincir_yillik": float(eq.iloc[-1] ** (1 / yrs) - 1) if yrs else None,
           "zincir_borsa_yillik": float(spy.iloc[-1] ** (1 / yrs) - 1) if yrs else None,
           "en_buyuk_dusus": dd, "masraf_yillik": float(w["masraf_3a"].mean() * 4) if "masraf_3a" in w else None,
           "haftalik_yeni_hisse": float(np.mean(weekly_new)) if weekly_new else None,
           "ceyreklik_yeni_hisse": float(np.mean(q_new)) if q_new else None,
           "ga90_fazla_borsa_3a": _boot(w["fazla_borsa_3a"]) if "fazla_borsa_3a" in w else None}
    return out | {"_haftalik": w}


def _m(w, c):
    return float(w[c].mean()) if c in w and w[c].notna().any() else None


def _boot(x: pd.Series, n: int = 2000, seed: int = 7) -> list[float]:
    """Yıl blokları ile bootstrap %90 güven aralığı (haftalık değerlerin ortalaması)."""
    x = x.dropna()
    years = x.groupby(x.index.year)
    blocks = [g.to_numpy() for _, g in years]
    rng = np.random.default_rng(seed)
    means = [np.concatenate([blocks[i] for i in rng.integers(0, len(blocks), len(blocks))]).mean() for _ in range(n)]
    return [float(np.quantile(means, 0.05)), float(np.quantile(means, 0.95))]


# --- Süzgeç ölçümü ----------------------------------------------------------------------------------------------

def suzgec_olcumu(v: Veri, yillar=AYAR, adim: int = 4) -> pd.DataFrame:
    """Her ret/dikkat işareti: kazananı koruma, kaybedeni eleme, oran (3 ve 6 ay). Örneklem: her 4 haftada bir."""
    dates = v.tarihler[(v.tarihler.year >= yillar[0]) & (v.tarihler.year <= yillar[1])][::adim]
    ev = v.tablo["evren"].loc[dates]
    rows = []
    for h in VADE:
        kaz = v.kazanan(h).loc[dates] & ev
        kay = v.kaybeden(h).loc[dates] & ev
        for n in isaretler.KESIN_RET + isaretler.DIKKAT:
            f = v.isaret[n].loc[dates] & ev
            fk, fy = f.where(kaz).stack().mean(), f.where(kay).stack().mean()
            fa = f.where(ev).stack().mean()
            rows.append({"isaret": n, "vade": h, "grup": "kesin_ret" if n in isaretler.KESIN_RET else "dikkat",
                         "evrende_gorulme": fa, "kazanani_koruma": 1 - fk, "kaybedeni_eleme": fy,
                         "oran": fy / fk if fk > 0 else np.inf,
                         "isaretli_ort_net": v.tablo[f"net_{h}"].loc[dates].where(f).stack().mean(),
                         "isaretsiz_ort_net": v.tablo[f"net_{h}"].loc[dates].where(ev & ~f).stack().mean()})
    return pd.DataFrame(rows)


# --- Benzerler (profil tablosu) ---------------------------------------------------------------------------------

def profil(v: Veri, yillar=AYAR, adim: int = 1) -> pd.DataFrame:
    """6 işaretin her birleşimi için (kesin ret yok, evrende) geçmişte ne oldu: adet, borsayı geçen, en iyi %5'e giren,
    %30'dan fazla kaybeden, medyan net (3/6 ay). Kartlardaki "Geçmişte buna benzeyenler" bu tablodan gelir."""
    dates = v.tarihler[(v.tarihler.year >= yillar[0]) & (v.tarihler.year <= yillar[1])][::adim]
    ok = (v.tablo["evren"] & ~v.isaret["kesin_ret"]).loc[dates]
    code = sum(v.isaret[n].loc[dates].astype(int) << i for i, n in enumerate(isaretler.OLUMLU))
    long = {"kod": code.where(ok).stack()}
    for h in VADE:
        net = v.tablo[f"net_{h}"].loc[dates]
        long[f"net_{h}"] = net.where(ok).stack()
        long[f"gecti_{h}"] = net.gt(v.tablo[f"kiyas_{h}"]["borsa"].loc[dates], axis=0).where(ok & net.notna()).stack()
        long[f"kazanan_{h}"] = v.kazanan(h).loc[dates].where(ok & net.notna()).stack()
    df = pd.DataFrame(long).dropna(subset=["kod", "net_3a"])
    g = df.groupby("kod")
    out = pd.DataFrame({"adet": g.size(), "medyan_3a": g.net_3a.median(), "medyan_6a": g.net_6a.median(),
                        "borsayi_gecen_3a": g.gecti_3a.mean(), "borsayi_gecen_6a": g.gecti_6a.mean(),
                        "kazanan_3a": g.kazanan_3a.mean(), "kazanan_6a": g.kazanan_6a.mean(),
                        "sert_kayip_3a": g.net_3a.apply(lambda s: (s < -0.30).mean())})
    out.index = out.index.astype(int)
    return out


# --- Otopsi ------------------------------------------------------------------------------------------------------

ISARET_METNI = {
    "yukselis": "Yükselişi sürüyordu", "is_iyilesiyor": "İşleri iyileşiyordu", "dipten_kalkti": "Dipten kalkmıştı",
    "sektor": "Sektörü yükselişteydi", "iceriden": "İçeriden alım vardı", "yakin_haber": "Bilanço yaklaşıyordu",
}


def otopsi(v: Veri, listeler: dict, yillar: tuple[int, int], vade: str = "3a", adet: int = 20) -> list[dict]:
    tab, isa = v.tablo, v.isaret
    h = VADE[vade]
    pos = {t: i for i, t in enumerate(v.tarihler)}
    px = tab["fiyat_cuma"]
    wret = np.log(px / px.shift(1))
    out = []
    for t0 in ceyrek_baslari(v.tarihler, yillar):
        if t0 not in pos:
            continue
        b = tab[f"brut_{vade}"].loc[t0].where(tab["evren"].loc[t0]).dropna()
        if b.empty:
            continue
        weeks = v.tarihler[pos[t0]: pos[t0] + h]
        ok = (isa["olumlu_sayisi"] >= ISARET_ESIK) & ~isa["kesin_ret"] & tab["evren"]
        for c in b.sort_values(ascending=False).index[:adet]:
            total = float(b[c])
            end = px.at[t0, c] * (1 + total)
            sig = [s for s in weeks if ok.at[s, c]]
            inlist = [s for s in weeks if c in listeler.get(s, [])]
            lr = wret.loc[weeks[1:], c] if len(weeks) > 1 else pd.Series(dtype=float)
            total_lr = np.log1p(total) if total > -1 else np.nan
            top_week = lr.idxmax() if lr.notna().any() else None
            tek = float(lr.max() / total_lr) if top_week is not None and total_lr and total_lr > 0 else None
            rec = {"tarih": str(t0.date()), "cik": c, "toplam": total, "tek_hafta_payi": None if tek is None else float(np.clip(tek, 0, 1)),
                   "en_buyuk_hafta": None if top_week is None else str(top_week.date()),
                   "kaynak_is": bool(isa["is_iyilesiyor"].loc[weeks, c].any()), "kaynak_sektor": bool(isa["sektor"].loc[weeks, c].any()),
                   "listeye_giris": str(inlist[0].date()) if inlist else None}
            if sig:
                s = sig[0]
                entry = px.at[s, c]
                cap = end / entry - 1
                cost = tab["masraf_orani"].at[s, c]
                rec |= {"ilk_isaret": str(s.date()), "isaret_fiyati": float(tab["ham_persembe"].at[s, c]),
                        "giris_fiyati_duz": float(entry), "yakalanabilir": float(cap),
                        "yakalanabilir_net": float((1 - cost) * (1 + cap) * (1 - cost) - 1),
                        "net_3a": _f(tab["net_3a"].at[s, c]), "net_6a": _f(tab["net_6a"].at[s, c]),
                        "fazla_borsa_3a": _f(tab["net_3a"].at[s, c] - tab["kiyas_3a"].at[s, "borsa"]),
                        "fazla_sektor_3a": _f(tab["net_3a"].at[s, c] - tab["sektor_3a"].at[s, c]),
                        "isaretler": [n for n in isaretler.OLUMLU if isa[n].at[s, c]],
                        "dikkat": [n for n in isaretler.DIKKAT if isa[n].at[s, c]]}
                rec |= _benzerler(v, s, c, ok, vade)
            else:
                ev_ok = bool(tab["evren"].loc[weeks, c].any())
                ret = bool(isa["kesin_ret"].loc[weeks, c].any())
                best = int(isa["olumlu_sayisi"].loc[weeks, c].max()) if ev_ok else None
                rec |= {"ilk_isaret": None, "neden": "evren dışı (küçük ya da az işlem)" if not ev_ok else
                        ("kesin ret işareti" if ret else f"en fazla {best} işaret (en az {ISARET_ESIK} gerekir)")}
            out.append(rec)
    return out


def _f(x):
    return None if pd.isna(x) else float(x)


def _benzerler(v: Veri, s: pd.Timestamp, c: str, ok: pd.DataFrame, vade: str) -> dict:
    """Aynı hafta aynı eşiği geçen diğer hisseler: kaçı kazandırdı, kazananı ne ayırdı, yanılmanın ortak nedeni."""
    tab, isa = v.tablo, v.isaret
    twins = ok.loc[s]
    twins = twins[twins].index.drop(c, errors="ignore")
    net = tab[f"net_{vade}"].loc[s, twins].dropna()
    if net.empty:
        return {"benzer_adet": 0}
    borsa = tab[f"kiyas_{vade}"].at[s, "borsa"]
    losers = net[net < borsa].index
    diff = {}
    for n in isaretler.OLUMLU + isaretler.DIKKAT:
        if len(losers):
            diff[n] = float(isa[n].at[s, c]) - float(isa[n].loc[s, losers].mean())
    ayiran = max(diff, key=lambda k: abs(diff[k])) if diff else None
    dikkat_loser = {n: float(isa[n].loc[s, losers].mean()) for n in isaretler.DIKKAT} if len(losers) else {}
    neden = max(dikkat_loser, key=dikkat_loser.get) if dikkat_loser and max(dikkat_loser.values()) > 0.25 else None
    return {"benzer_adet": int(len(net)), "benzer_gecen": int((net > borsa).sum()),
            "benzer_sert_kayip": int((net < -0.20).sum()), "benzer_medyan": float(net.median()),
            "ayiran_isaret": ayiran, "ayiran_fark": diff.get(ayiran) if ayiran else None,
            "kaybedenlerde_sik_dikkat": neden, "kaybedenlerde_oran": dikkat_loser.get(neden) if neden else None,
            "benzer_ornek": [{"cik": x, "net": float(net[x])} for x in net.sort_values().index[:3]]}


# --- Ayar (yalnızca 2013–2022) -----------------------------------------------------------------------------------

def varyantlar(v: Veri, suz: pd.DataFrame) -> list[dict]:
    """Önceden sayılmış küçük bir aday kümesi; seçim yalnızca ayar dönemi sonucuyla."""
    esit = {n: 1.0 for n in isaretler.OLUMLU}
    dates = v.tarihler[(v.tarihler.year >= AYAR[0]) & (v.tarihler.year <= AYAR[1])]
    ok = (v.tablo["evren"] & ~v.isaret["kesin_ret"]).loc[dates]
    kaz = v.kazanan("3a").loc[dates] & ok
    base = kaz.stack().mean() / ok.stack().mean()
    lift = {}
    for n in isaretler.OLUMLU:
        f = v.isaret[n].loc[dates] & ok
        p = (kaz & f).stack().sum() / max(f.stack().sum(), 1)
        lift[n] = float(np.clip(np.log(max(p / (kaz.stack().sum() / ok.stack().sum()), 1e-3)), -1, 2))
    # Ret kuralını geçemeyen kesin ret işaretleri dikkat grubuna iner (plan, bölüm 3)
    ret = [n for n in isaretler.KESIN_RET if _ret_kalir(suz, n)]
    out = []
    for ad, w, ceza in (("esit_ceza1", esit, 1.0), ("esit_ceza0", esit, 0.0), ("lift_ceza1", lift, 1.0), ("lift_ceza0", lift, 0.0)):
        out.append({"ad": ad, "agirlik": w, "dikkat_cezasi": ceza, "ret": ret, "en_az_puan": 1 if ad.startswith("esit") else 0.0})
    _ = base
    return out


def _ret_kalir(suz: pd.DataFrame, n: str) -> bool:
    r = suz[(suz.isaret == n) & (suz.vade == "3a")].iloc[0]
    return bool(r.kazanani_koruma >= 0.90 and r.oran >= 2.0 and r.isaretli_ort_net <= r.isaretsiz_ort_net)


def ayarla() -> dict:
    v = Veri.yukle()
    suz = suzgec_olcumu(v)
    defter = []
    for a in varyantlar(v, suz):
        k = karne(v, liste(v, a, v.tarihler[(v.tarihler.year >= AYAR[0]) & (v.tarihler.year <= AYAR[1])]), AYAR)
        defter.append({"ayar": a, "karne": {x: y for x, y in k.items() if not x.startswith("_")}})
    best = max(defter, key=lambda d: (d["karne"]["fazla_borsa_3a"] or -9))
    sonuc = {"tarih": str(pd.Timestamp.today().date()),
             "durum": "Sınav dönemi (2023–2026) AÇILMADAN, yalnızca 2013–2022 verisiyle seçildi.",
             "secim_kurali": "Ayar döneminde haftalık ilk 10'un borsadan ortalama fazla getirisi (3 ay, masraf sonrası) en yüksek varyant.",
             "secilen": best["ayar"], "deneme_sayisi": len(defter), "defter": defter,
             "suzgec": suz.round(4).to_dict("records")}
    AYAR_DOSYA.write_text(json.dumps(sonuc, ensure_ascii=False, indent=1, default=_json))
    return sonuc


def _json(x):
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, (pd.Timestamp,)):
        return str(x.date())
    return str(x)


def ayar_kilitli_mi() -> bool:
    """Ayar dosyası git'te commit edilmiş ve değişmemiş olmalı (sınav kilidi)."""
    rel = str(AYAR_DOSYA.relative_to(config.ROOT))
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=config.ROOT, capture_output=True).returncode == 0
    clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", rel], cwd=config.ROOT).returncode == 0
    return tracked and clean


def secilen_ayar() -> dict:
    return json.loads(AYAR_DOSYA.read_text())["secilen"]
