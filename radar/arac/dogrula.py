"""Test düzeneğinin gerçek veride doğrulanması → reports/research/arac_dogrulama.md

1. Sızıntı: girdiler Cuma T'de kesilip işaretler yeniden hesaplanır; T'deki değerler tam veriyle aynı olmalı.
2. Hayatta kalma: evrende sonradan borsadan çıkan hisseler var mı; iflas edenler −%100 sayılıyor mu.
3. Bilinen değerler: piyasa değeri ve getiriler bağımsız hesapla karşılaştırılır.
4. Masraf: net = (1 − c)² (1 + brüt) − 1.

python -m radar.arac.dogrula
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive, config
from radar.arac import isaretler
from radar.arac.duzenek import Duzenek, masrafli

OUT = config.ROOT / "reports" / "research" / "arac_dogrulama.md"
KESIM = ["2014-09-05", "2018-03-02", "2021-11-05", "2025-05-02"]


def main() -> str:
    d = Duzenek.yukle()
    k = isaretler.Kaynaklar.yukle(d)
    full = isaretler.hesapla(d, k)
    L = ["# Test düzeneği doğrulaması", ""]

    L += ["## 1. Sızıntı testi (girdiler o tarihte kesilerek)", "", "| Tarih | Karşılaştırılan değer | Farklı |", "|---|---|---|"]
    ok_all = True
    for T in pd.to_datetime(KESIM):
        cut = isaretler.hesapla(d, k.kes(T))
        n = bad = 0
        names = []
        for name in full:
            a, b = full[name].loc[T].astype(float), cut[name].loc[T].astype(float)
            diff = ~(np.isclose(a, b, equal_nan=True))
            n += len(a)
            if diff.any():
                bad += int(diff.sum())
                names.append(name)
        ok_all &= bad == 0
        L.append(f"| {T.date()} | {n:,} | {bad} {names[:5] if names else ''} |")
    L += ["", "Sonuç: " + ("geçti — hiçbir işaret gelecekteki belgeden etkilenmiyor." if ok_all else "KALDI — yukarıdaki işaretler incelenmeli."), ""]

    ev = d.evren
    sec = d.sec.set_index(d.sec.cik.astype(str)).reindex(d.sutunlar)
    cikan = sec.status.eq("çıktı").to_numpy()
    batan = sec.bankrupt.fillna(False).to_numpy(bool)
    L += ["## 2. Hayatta kalma yanlılığı", "", "| Yıl | Haftalık evren (ort.) | Sonradan borsadan çıkan | İşlem tutarı FINRA'dan |",
          "|---|---|---|---|"]
    kaynak = d.islem_kaynagi
    for y in range(2013, 2027):
        m = ev.index.year == y
        e = ev[m]
        L.append(f"| {y} | {e.sum(axis=1).mean():.0f} | {e.loc[:, cikan].sum(axis=1).mean():.0f} | "
                 f"{(e & kaynak[m].eq('finra')).sum(axis=1).mean():.0f} |")
    br = d.brut("3a")
    b_ev = br.where(ev).loc[:, batan]
    L += ["", f"İflas eden ve evrende bulunmuş hisse: {int(ev.loc[:, batan].any().sum())}; bunların 3 aylık getirisi −%100 olan hisse-hafta: "
          f"{int((b_ev <= -0.999).sum().sum())}.", ""]

    L += ["## 3. Bilinen değerler", "", "| Kontrol | Beklenen | Bulunan | Durum |", "|---|---|---|---|"]
    sym = sec.symbol
    def c_of(s):
        return sym.index[sym == s][0]
    # Piyasa değeri: AAPL 7 Haziran 2024 (perşembe kapanışı 194,48 $ × ~15,33 Mr hisse ≈ 2,98 tn $)
    v = d.piyasa_degeri.at[pd.Timestamp("2024-06-07"), c_of("AAPL")]
    L.append(f"| AAPL piyasa değeri 2024-06-06 | 2,9–3,05 tn $ | {v / 1e12:.2f} tn $ | {'tamam' if 2.9e12 <= v <= 3.05e12 else 'KONTROL'} |")
    v = d.piyasa_degeri.at[pd.Timestamp("2024-06-07"), c_of("JNJ")]
    L.append(f"| JNJ piyasa değeri 2024-06-06 | 350–365 Mr $ | {v / 1e9:.0f} Mr $ | {'tamam' if 3.5e11 <= v <= 3.65e11 else 'KONTROL'} |")
    # Getiri: SPY 13 hafta, arşivdeki günlük düzeltilmiş fiyattan bağımsız hesap
    spy = archive.load("prices", columns=["symbol", "date", "adjclose"], filters=[("symbol", "in", ["SPY"])]).set_index("date").adjclose
    t0, t1 = pd.Timestamp("2019-01-04"), pd.Timestamp("2019-01-04") + pd.Timedelta(weeks=13)
    exp = spy.loc[:t1].iloc[-1] / spy.loc[:t0].iloc[-1] - 1
    got = d.kiyas("3a")["borsa"].at[t0]
    L.append(f"| SPY 3 ay 2019-01-04 | {exp:+.4f} | {got:+.4f} | {'tamam' if abs(exp - got) < 1e-4 else 'KONTROL'} |")
    L.append("")

    L += ["## 4. Masraf", ""]
    brut, oran = d.brut("3a"), d.masraf_orani
    net = d.net("3a")
    chk = masrafli(brut, oran)
    L.append(f"Net getiri bağımsız formülle aynı: {'evet' if np.allclose(net.fillna(0), chk.fillna(0)) else 'HAYIR'}; "
             f"evrende ortalama tek yön masraf: %{oran.where(ev).stack().mean() * 100:.2f}.")
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return OUT.read_text()


if __name__ == "__main__":
    main()
