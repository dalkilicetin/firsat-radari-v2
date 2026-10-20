"""Klasik Fırsat Radarı'nın (v5.16, main) geçmişte yeniden kurulabilen çekirdeğinin testi → reports/research/klasik_radar_test.md

Klasik radarın "★ 10'u" listesi (app.js top10) birkaç kaynağı puanla birleştirir. Bu testte YALNIZCA fiyat ve bilançodan
o güne kadar bilinen veriyle yeniden kurulabilenler vardır; haber, analist, skandal, Finnhub'ın o günkü bilanço anlık görüntüsü
(marj dönüşü, EPS sürprizi vb.) ve "aday / conviction" puanları geçmişte YOK ve test dışıdır.

Kurulanlar (scanner.mjs + app.js, aynen):
- Evren: klasik evren = S&P 500 ∪ Nasdaq-100 ∪ Russell 1000 (≈1.000–1.100 hisse). Geçmiş üyelik listesi yok; her tarihte piyasa
  değeri en yüksek 1.100 hisse (o günkü değerle, banka/sigorta/GYO dahil, sonradan çıkanlar dahil) kullanılır.
- mom = 12-3 ay getirisi (52 hafta önce → 13 hafta önce), pull = 3-1 ay (13 hafta önce → ay başı). mom yüzdeliği ≥ 0,7 VE
  pull yüzdeliği ≤ 0,5 (düzeltme yapmış) VE sağlam (piyasa değeri ≥ 2 Mr$ ve F/K var = son 12 ay net kâr > 0).
  Sıra: (mom yüzdeliği + düzeltme yüzdeliği) azalan; ilk 15 hisse 10 − 0,15·sıra puan alır.
- Şok: günlük düşüş ≤ −%8 (−%50'nin altı bölünme sayılır, şok değil) siddet = 100 + |düşüş|; aylık düşüş ≤ −%12 siddet = |düşüş|;
  dev (≥ 50 Mr$) +30, 2 Mr$ altı −25 (endeks +20 bonusu geçmiş üyelik listesi olmadığından yok); ilk 15; piyasa değeri ≥ 2 Mr$ ve
  günlük değişimi bilinenler 7 + min(|günlük|/5, 3) puan alır.
- Ceza: en zayıf %40 momentum (mom yüzdeliği < 0,4) ve şok değilse −4.
- Çeşitlilik: aynı sektörden en fazla 3 (sektör = SIC'ten sektör ETF'i; uygulamadaki Finnhub sektörü yerine).
- Çıktı: en fazla 10.

Üç varyant (önceden yazıldı): A = yalnızca Trend+Düzeltme; B = Trend + Şok, kodda yazıldığı gibi (aylık düşüş kayıtları da
puan alır: yorumda "çıkarıldı" yazıyor ama kod günlük değişimi bilinen her aylık düşüşü almaya devam ediyor); C = Trend + yalnızca günlük şok.

Test: aynı düzenek (perşembe kesimi, cuma kapanışı alış, masraf, 13 / 26 hafta, batanlar dahil), aynı 3 yıl.
python -m radar.arac.klasik
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import archive, config
from radar.arac import analiz, isaretler, temel
from radar.arac.duzenek import VADE, Duzenek
from radar.research import fundamentals
from radar.research.road1 import by_filing

R = config.ROOT / "reports" / "research"
EVREN_N = 1100
KURAL_OGRENME_BASI = pd.Timestamp("2026-07-12")  # v5.16 kuralı 12.07–10.10.2026 gece verisinden çıkarıldı
YIL = 3
SEKTOR_EN_FAZLA = 3


def net_kar_12ay(d: Duzenek) -> pd.DataFrame:
    """Son 12 ay net kâr: son yıllık değer + (son çeyrek-içi birikimli − geçen yılın aynı birikimlisi); o gün yayımlanmış rapora göre."""
    fin = fundamentals.plain(d.finans)
    fin = fin[fin.uom.isin(["USD", "shares"])]
    fin = fin.assign(gun=isaretler.kullanilabilir(fin.accepted).to_numpy())
    gun = fin.drop_duplicates("adsh").set_index("adsh").gun
    parts = []
    fy = by_filing(fin, isaretler.NET_INCOME, [4]).assign(tur="fy")
    parts.append(fy)
    for q in (1, 2, 3):
        parts.append(by_filing(fin, isaretler.NET_INCOME, [q]).assign(tur="ytd"))
    ev = pd.concat(parts, ignore_index=True)
    ev = ev[ev.qtrs.isin([1, 2, 3, 4])].assign(cik=lambda x: x.cik.astype(str))
    ev["gun"] = ev.adsh.map(gun)
    ev = ev.dropna(subset=["gun"]).sort_values(["cik", "gun", "accepted", "adsh"], kind="stable")
    ev["fy_cur"] = np.where(ev.tur == "fy", ev.cur, np.nan)
    ev["ytd"] = np.where(ev.tur == "fy", 0.0, (ev.cur - ev.prev.fillna(ev.cur * 0)).where(ev.prev.notna()))
    ev["fy_cur"] = ev.groupby("cik").fy_cur.ffill()
    ev["ytd"] = ev.groupby("cik").ytd.ffill().fillna(0.0)
    ev["value"] = ev.fy_cur + ev.ytd
    ev = ev.dropna(subset=["value"])
    return isaretler._deger(ev[["cik", "gun", "value", "accepted", "adsh"]], d.tarihler, d.sutunlar, 450)


def gunluk_degisim(d: Duzenek) -> pd.DataFrame:
    """Perşembe günü (kesim günü) günlük düşüş/yükseliş %: arşivdeki günlük düzeltilmiş kapanıştan; hisse başına CIK."""
    sec = d.sec.assign(cik=d.sec.cik.astype(str))
    bar = d.tarihler - pd.Timedelta(days=1)
    act = archive.load("prices", columns=["symbol", "date", "adjclose"])
    act = act.merge(sec[sec.status == "aktif"][["symbol", "cik"]], on="symbol")[["cik", "date", "adjclose"]]
    try:
        ex = archive.load("prices_exited", columns=["cik", "date", "adjclose"]).assign(cik=lambda x: x.cik.astype(str))
        act = pd.concat([act, ex], ignore_index=True)
    except Exception:
        pass
    act = act.sort_values(["cik", "date"], kind="stable")
    act["ch"] = act.groupby("cik").adjclose.pct_change() * 100
    act = act[act.date.isin(set(bar))].drop_duplicates(["cik", "date"], keep="last")
    w = act.pivot(index="date", columns="cik", values="ch").reindex(bar)
    w.index = d.tarihler
    return w.reindex(columns=d.sutunlar)


def kur(d: Duzenek) -> dict:
    P = d.persembe["price"]
    mcap = d.piyasa_degeri
    ok = d.uye & P.notna() & d.cuma["price"].notna() & mcap.notna()
    sira = mcap.where(ok).rank(axis=1, ascending=False, method="first")
    evren = ok & (sira <= EVREN_N)
    bar = P.index - pd.Timedelta(days=1)
    pos = np.searchsorted(bar.to_numpy(), (bar.to_period("M").start_time).to_numpy(), side="left") - 1
    ay_basi = pd.DataFrame(np.where(pos[:, None] >= 0, P.to_numpy()[np.clip(pos, 0, None)], np.nan), index=P.index, columns=P.columns)
    r13 = P / P.shift(13) - 1
    mom = P.shift(13) / P.shift(52) - 1
    pull = ay_basi / P.shift(13) - 1
    mtd = P / ay_basi - 1
    pct = lambda x: (x.where(evren).rank(axis=1, method="min") - 1) / x.where(evren).count(axis=1).to_numpy()[:, None]
    mom_pct = pct(mom)
    duz_pct = 1 - pct(pull)
    ni = net_kar_12ay(d)
    saglam = evren & (mcap >= 2e9) & (ni > 0)
    gun = gunluk_degisim(d)
    return dict(P=P, mcap=mcap, evren=evren, mom_pct=mom_pct, duz_pct=duz_pct, saglam=saglam, mtd=mtd * 100, gun=gun, ni=ni)


def liste(d: Duzenek, k: dict, t: pd.Timestamp, varyant: str) -> list[str]:
    mp, dp = k["mom_pct"].loc[t], k["duz_pct"].loc[t]
    ev, sag = k["evren"].loc[t], k["saglam"].loc[t]
    trend = ((mp >= 0.7) & (dp >= 0.5) & sag).fillna(False)
    tl = (mp + dp)[trend].sort_values(ascending=False).index[:15]
    puan: dict[str, float] = {}
    rol: dict[str, set] = {}
    for i, c in enumerate(tl):
        puan[c] = puan.get(c, 0) + 10 - i * 0.15
        rol.setdefault(c, set()).add("trend")
    if varyant in ("B", "C"):
        gun, mtd, mc = k["gun"].loc[t], k["mtd"].loc[t], k["mcap"].loc[t] / 1e6
        rows = []
        for c in ev[ev].index:
            g, a = gun.get(c, np.nan), mtd.get(c, np.nan)
            gv = g if (pd.notna(g) and g > -50) else np.nan
            if pd.notna(gv) and gv <= -8:
                s = 100 + abs(gv)
            elif varyant == "B" and pd.notna(a) and a <= -12:
                s = abs(a)
            else:
                continue
            m = mc.get(c, 0)
            if m >= 50000:
                s += 30
            if 0 < m < 2000:
                s -= 25
            rows.append((c, s, gv, m))
        rows.sort(key=lambda r: -r[1])
        for c, s, gv, m in rows[:15]:
            if pd.isna(gv) or m < 2000:
                continue
            puan[c] = puan.get(c, 0) + 7 + min(abs(gv) / 5, 3)
            rol.setdefault(c, set()).add("sok")
    for c in list(puan):
        if mp.get(c, 1) < 0.4 and "sok" not in rol[c]:
            puan[c] -= 4
    sek, per, out = d.sektor_etf, {}, []
    for c, p in sorted(((c, p) for c, p in puan.items() if p > 0), key=lambda x: -x[1]):
        s = sek.get(c, "IWM")
        if per.get(s, 0) >= SEKTOR_EN_FAZLA:
            continue
        per[s] = per.get(s, 0) + 1
        out.append(c)
        if len(out) == 10:
            break
    return out


def p(x) -> str:
    return "—" if x is None or pd.isna(x) else f"{'+' if x > 0 else '−' if x < 0 else ''}%{abs(x) * 100:.0f}"


def olc(d: Duzenek, k: dict, listeler: dict, bas: pd.Timestamp, son: pd.Timestamp) -> dict:
    v = analiz.Veri.yukle()  # analiz aracının evreni (ortak kıyas için)
    out = {}
    pos = {t: i for i, t in enumerate(d.tarihler)}
    for vade, h in VADE.items():
        brut, net = d.brut(vade), d.net(vade)
        spy = d.kiyas(vade)["borsa"]
        ev = k["evren"]
        kaz = (brut.where(ev).rank(axis=1, pct=True) >= 0.95)
        kaz_ortak = v.kazanan(vade)
        haftalar = [t for t in d.tarihler if bas <= t <= son and net.loc[t].where(ev.loc[t]).notna().any()]
        qs = list(analiz.ceyrek_baslari(pd.DatetimeIndex(haftalar), (bas.year, 2100)))
        temiz = lambda t: t + pd.Timedelta(weeks=h) <= KURAL_OGRENME_BASI
        rows, hw = [], []
        for t in haftalar:
            pk = listeler.get(t, [])
            n = net.loc[t, pk].dropna()
            if n.empty:
                continue
            hw.append({"t": t, "ort": n.mean(), "med": n.median(), "spy": spy.at[t], "temiz": temiz(t), "adet": len(n),
                       "kazanan": int(kaz.loc[t, n.index].sum()), "geçti": int((n > spy.at[t]).sum()), "sert": int((n < -0.30).sum())})
        H = pd.DataFrame(hw)
        # çeyrek başı tablosu
        for t0 in qs:
            if t0 not in pos or net.loc[t0].where(ev.loc[t0]).isna().all():
                continue
            pk = listeler.get(t0, [])
            n = net.loc[t0, pk]
            rows.append({"tarih": t0, "ort": n.mean(), "spy": spy.at[t0], "n": len(pk), "temiz": temiz(t0),
                         "kazanan": int(kaz.loc[t0, pk].sum()) if pk else 0, "secim": list(pk)})
        # yakalama: çeyrek başı kazananları, çeyrek içinde listeye giren
        top = got = got_o = tot_o = 0
        got_t = top_t = 0
        for t0 in qs:
            i0 = pos[t0]
            if i0 + h >= len(d.tarihler):
                continue
            seen = {c for s in d.tarihler[i0: i0 + h] for c in listeler.get(s, [])}
            kz = kaz.loc[t0][kaz.loc[t0]].index
            top += len(kz); got += sum(c in seen for c in kz)
            if temiz(t0):
                top_t += len(kz); got_t += sum(c in seen for c in kz)
            ko = kaz_ortak.loc[t0][kaz_ortak.loc[t0]].index
            tot_o += len(ko); got_o += sum(c in seen for c in ko)
        out[vade] = dict(hafta=H, ceyrek=pd.DataFrame(rows), yakalama=got / max(top, 1), yakalama_temiz=got_t / max(top_t, 1),
                         yakalama_ortak=got_o / max(tot_o, 1), kazanan_sayisi=top)
    return out


def ozet(res: dict, vade: str, temiz: bool | None) -> dict:
    H = res[vade]["hafta"]
    if temiz is True:
        H = H[H.temiz]
    n = max(H.adet.sum(), 1)
    return dict(hafta=len(H), medyan=float(H.med.mean()), ort=float(H.ort.mean()), spy=float(H.spy.mean()),
                fazla=float((H.ort - H.spy).mean()), gecen_hafta=float((H.ort > H.spy).mean()),
                kazanan_orani=float(H.kazanan.sum() / n), borsayi_gecen=float(H["geçti"].sum() / n), sert_kayip=float(H.sert.sum() / n))


def main() -> dict:
    d = Duzenek.yukle(daralt=False)
    k = kur(d)
    son = d.brut("3a").dropna(how="all").index.max()
    bas = son - pd.DateOffset(years=YIL)
    tum = [t for t in d.tarihler if t >= bas - pd.Timedelta(weeks=1)]
    rep = {"pencere": f"{bas.date()} … {son.date()}", "varyantlar": {}}
    md = [f"# Klasik Radar (v5.16) — son 3 yılın her haftası, görmediği verilerle ({bas.date()} … {son.date()})", ""]
    sonuc_ceyrek = {}
    for var, ad in (("A", "A · yalnızca Trend+Düzeltme"), ("B", "B · Trend + Şok (kodda yazıldığı gibi)"), ("C", "C · Trend + yalnızca günlük şok")):
        ls = {t: liste(d, k, t, var) for t in tum if k["evren"].loc[t].any()}
        res = olc(d, k, ls, bas, son)
        rep["varyantlar"][var] = {v_: {"tumu": ozet(res, v_, None), "temiz": ozet(res, v_, True), "yakalama": res[v_]["yakalama"],
                                       "yakalama_temiz": res[v_]["yakalama_temiz"], "yakalama_ortak_evren": res[v_]["yakalama_ortak"],
                                       "kazanan_sayisi": res[v_]["kazanan_sayisi"]} for v_ in VADE}
        sonuc_ceyrek[var] = res["3a"]["ceyrek"]
        sonuc_ceyrek[var + "_6"] = res["6a"]["ceyrek"]
        sonuc_ceyrek[var + "_liste"] = ls
    (R / "klasik_radar_test.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
    # ---- rapor ----
    for var, ad in (("A", "A · yalnızca Trend+Düzeltme"), ("B", "B · Trend + Şok (kodda yazıldığı gibi)"), ("C", "C · Trend + yalnızca günlük şok")):
        r = rep["varyantlar"][var]
        md += [f"## {ad}", "", "| Ölçü | 3 ay (tümü) | 3 ay (kural öğrenilmeden önceki) | 6 ay (tümü) | 6 ay (kural öğrenilmeden önceki) |", "|---|---|---|---|---|"]
        rows = [("Hafta sayısı", "hafta", lambda x: str(x)), ("Ortadaki hissenin getirisi", "medyan", p), ("Ortalama getiri", "ort", p),
                ("Borsa (SPY)", "spy", p), ("Borsadan fazla", "fazla", p), ("Listenin borsayı geçtiği hafta oranı", "gecen_hafta", p),
                ("Listedeki hissenin kazanan çıkma oranı (kendi evreninde en iyi %5)", "kazanan_orani", p),
                ("Listedeki hissenin borsayı geçme oranı", "borsayi_gecen", p), ("Listedeki hissenin %30'dan fazla kaybetme oranı", "sert_kayip", p)]
        for adl, key, f in rows:
            md.append(f"| {adl} | {f(r['3a']['tumu'][key])} | {f(r['3a']['temiz'][key])} | {f(r['6a']['tumu'][key])} | {f(r['6a']['temiz'][key])} |")
        md.append(f"| **Yakalama oranı** (çeyrek içinde listeye giren kazanan) | {p(r['3a']['yakalama'])} | {p(r['3a']['yakalama_temiz'])} | {p(r['6a']['yakalama'])} | {p(r['6a']['yakalama_temiz'])} |")
        md.append(f"| Analiz Radarı'nın evrenindeki kazananları yakalama | {p(r['3a']['yakalama_ortak_evren'])} | | {p(r['6a']['yakalama_ortak_evren'])} | |")
        md.append("")
    sym = d.sec.assign(cik=d.sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
    md += ["## Çeyrek çeyrek (varyant B, kodda yazıldığı gibi): 10 hisse ve 3 ay getirisi", "",
           "| Çeyrek başı | 10 hisse ort. 3 ay | Borsa | Kural öğrenilmeden önce mi | Seçilenler |", "|---|---|---|---|---|"]
    for r in sonuc_ceyrek["B"].itertuples():
        md.append(f"| {r.tarih:%d.%m.%Y} | {p(r.ort)} | {p(r.spy)} | {'evet' if r.temiz else 'hayır (kural bu dönemden öğrenildi)'} | "
                  f"{', '.join(sym.get(c, c) for c in r.secim)} |")
    (R / "klasik_radar_test.md").write_text("\n".join(md) + "\n")
    pd.concat({v_: sonuc_ceyrek[v_].assign(secim=lambda x: x.secim.apply(lambda s: ", ".join(sym.get(c, c) for c in s))) for v_ in ("A", "B", "C")}).to_csv(R / "klasik_radar_ceyrekler.csv")
    print("\n".join(md[:60]))
    return rep


if __name__ == "__main__":
    main()
