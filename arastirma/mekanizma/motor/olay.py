"""Olay calismasi: sinyal gunleri -> ayiklanmis olaylar -> ileri getiri, MAE, bolum tablosu, kosul kirilimi."""
import numpy as np
import pandas as pd

from mekanizma.ayarlar import MALIYET_BP
from mekanizma.motor import sonuc
from mekanizma.motor.istatistik import ozet


def ayikla(sinyal, bekleme):
    """Ilk True alinir, sonraki `bekleme` bar yok sayilir."""
    v = sinyal.fillna(False).to_numpy(bool)
    sec, i = [], 0
    while i < len(v):
        if v[i]:
            sec.append(i)
            i += bekleme + 1
        else:
            i += 1
    return sinyal.index[sec]


def bolumle(olaylar, idx, bosluk=126):
    """Aralari `bosluk` bardan az olan olaylar ayni bolumde. Seri: olay tarihi -> bolum no (0'dan)."""
    pos = idx.get_indexer(olaylar)
    b, no, onceki = [], -1, None
    for p in pos:
        if onceki is None or p - onceki >= bosluk:
            no += 1
        b.append(no)
        onceki = p
    return pd.Series(b, index=olaylar, dtype=int)


def _f(v):
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)


def olay_testi(adj, sinyal, ufuklar, bekleme, kosullar=None, kesif_bitis=None, bolum_bosluk=126, tip="endeks"):
    ol = ayikla(sinyal, bekleme)
    ileri = sonuc.ileri_getiri(adj, ufuklar)
    maliyet = 2 * MALIYET_BP[tip] / 1e4
    bol = bolumle(ol, adj.index, bolum_bosluk) if len(ol) else pd.Series(dtype=int)
    ilk = ol[~bol.duplicated().to_numpy()] if len(ol) else ol
    cikti = dict(n_olay=int(len(ol)), n_bolum=int(bol.nunique()) if len(ol) else 0, ufuk={})
    for h in ufuklar:
        tum = ileri[h].dropna()
        mae_h = sonuc.mae(adj, h)
        o = ileri[h].reindex(ol).dropna()
        ib = ileri[h].reindex(ilk).dropna()
        kosulsuz = float(tum.mean()) if len(tum) else None
        d = dict(olay=ozet(o), bolum=ozet(ib), kosulsuz_ort=kosulsuz,
                 fark_olay=_f(o.mean() - kosulsuz) if len(o) and kosulsuz is not None else None,
                 fark_bolum=_f(ib.mean() - kosulsuz) if len(ib) and kosulsuz is not None else None,
                 net_ort_olay=_f(o.mean() - maliyet) if len(o) else None,
                 mae_olay=ozet(mae_h.reindex(ol).dropna()), mae_kosulsuz=_f(mae_h.dropna().mean()))
        if kesif_bitis is not None:
            kb = pd.Timestamp(kesif_bitis)
            d["kesif"] = ozet(o[o.index <= kb])
            d["dogrulama"] = ozet(o[o.index > kb])
        if kosullar:
            kir = {}
            for ad, k in kosullar.items():
                kk = k.reindex(ol)
                kir[ad] = {str(deg): ozet(o[kk.reindex(o.index) == deg]) for deg in sorted(kk.dropna().unique(), key=str)}
            d["kosul"] = kir
        cikti["ufuk"][str(h)] = d
    cikti["olay_tablosu"] = [dict(tarih=str(t.date()), bolum=int(bol[t]),
                                  **{f"g{h}": _f(ileri[h].get(t, np.nan)) for h in ufuklar}) for t in ol]
    return cikti


def isi_haritasi(adj, x, y, x_kova, y_kova, ufuk, bekleme, bolum_bosluk=126):
    """x ve y serilerini kovalara bol; her hucrede ayiklanmis olaylarin ileri getiri/MAE ozeti."""
    ileri = sonuc.ileri_getiri(adj, [ufuk])[ufuk]
    mae_s = sonuc.mae(adj, ufuk)
    hucre = []
    for i in range(len(x_kova) - 1):
        for j in range(len(y_kova) - 1):
            xs = (x <= x_kova[i]) & (x > x_kova[i + 1]) if x_kova[0] > x_kova[-1] else (x >= x_kova[i]) & (x < x_kova[i + 1])
            ys = (y >= y_kova[j]) & (y < y_kova[j + 1])
            ol = ayikla(xs & ys, bekleme)
            r = ileri.reindex(ol).dropna()
            hucre.append(dict(x=[x_kova[i], x_kova[i + 1]], y=[y_kova[j], y_kova[j + 1]], n=int(len(r)),
                              bolum_n=int(bolumle(r.index, adj.index, bolum_bosluk).nunique()) if len(r) else 0,
                              medyan=_f(r.median()) if len(r) else None, isabet=_f((r > 0).mean()) if len(r) else None,
                              mae_medyan=_f(mae_s.reindex(r.index).median()) if len(r) else None))
    return hucre
