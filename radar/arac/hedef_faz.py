"""Aylık yenilemede başlangıç haftasına duyarlılık: 4 farklı başlangıç haftası (faz) → reports/research/arac_hedef_1a_faz.json

PYTHONPATH=. python radar/arac/hedef_faz.py
"""
import os, json; os.environ["RADAR_YZ_VADE"]="1a"
import numpy as np, pandas as pd
from radar.arac import analiz, yz, hedef
from radar.arac.analiz import Veri
v=Veri.yukle(); S=pd.read_parquet(yz.OUT/"skorlar.parquet"); P=analiz.puan(v, analiz.secilen_ayar()); tab=v.tablo
tar=pd.DatetimeIndex(S.index.get_level_values(0).unique())
out={}
for ad in ["kural_10","kural_10_risk","kural_5_risk","kural30_B_10_risk"]:
    n,risk,b=hedef.VARYANTLAR[ad]
    for bas,yl in (("2016-2022",(2016,2022)),("2023-2026",(2023,2100))):
        ks=[]
        for faz in range(4):
            qs=[t for t in tar[(tar.year>=yl[0])&(tar.year<=yl[1])][faz::4] if tab["net_1a"].loc[t].notna().any()]
            r=np.array([float(tab["net_1a"].loc[t, hedef.secim(v,P,S,t,n,risk,b)].mean()) for t in qs]); spy=np.array([float(tab["kiyas_1a"].at[t,"borsa"]) for t in qs])
            y=len(r)*4/52; a=np.prod(1+r)**(1/y)-1; s=np.prod(1+spy)**(1/y)-1; d=np.cumprod(1+r); dd=(d/np.maximum.accumulate(d)-1).min()
            ks.append(dict(faz=faz,yillik=float(a),borsa=float(s),kat=float(a/s),dusus=float(dd)))
        out[f"{ad}|{bas}"]=ks
        print(ad,bas," ".join(f"{k['yillik']*100:+.0f}%/{k['kat']:.1f}x/dd{k['dusus']*100:.0f}" for k in ks))
json.dump(out,open("reports/research/arac_hedef_1a_faz.json","w"),indent=1)
