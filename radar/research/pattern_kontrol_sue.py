import numpy as np, pandas as pd
from radar.research import panel, fundamentals
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import by_filing, load_fin
from radar.research import pattern_arama as A
p=panel.build(); price,raw=p["price"],p["raw"]
fin=fundamentals.plain(load_fin())
eps=by_filing(fin,["EarningsPerShareDiluted","EarningsPerShareBasic"],[1])
d=pit(eps.rename(columns={"accepted":"date"}).assign(value=eps.cur-eps.prev)[["cik","date","value"]],price.index,price.columns,FUNDAMENTAL_MAX_AGE)
sue_adj=(d/price.where(price>0)).clip(-1,1); sue_raw=(d/raw.where(raw>0)).clip(-1,1)
fr=pd.read_parquet(A.FRAME,columns=["tarih","islem_tutari","getiri_13h","sue_fiyat"]).reset_index()
fr=fr[(fr.islem_tutari>=1e6)&fr.getiri_13h.notna()].copy()
from radar.research.pattern_testi import cost
fr["net"]=fr.getiri_13h-2*cost(fr.islem_tutari).to_numpy()
ti=price.index.get_indexer(fr.tarih); ci=price.columns.get_indexer(fr.cik.astype(str))
for nm,S in [("adj",sue_adj),("raw",sue_raw)]:
    v=S.to_numpy()[ti,ci]; fr[nm]=v
spy=__import__('radar.research.context',fromlist=['x']).etf_prices(panel.fridays())["SPY"]; dates=panel.fridays()
def res(col):
    rows=[]
    for t,g in fr.groupby("tarih"):
        g=g.dropna(subset=[col])
        if len(g)<10: continue
        sel=g.nsmallest(10,col); i=dates.searchsorted(t)
        rows.append((t.month,sel.net.mean(), spy.iloc[i+13]/spy.iloc[i]-1 if i+13<len(spy) else np.nan))
    d=pd.DataFrame(rows,columns=["ay","r","spy"]).dropna()
    return {k:round(float(np.prod(1+d[d.ay.isin(m)].r)**(4/len(d[d.ay.isin(m)]))-1),3) for k,m in A.CHAINS.items()}
print("çerçevedeki sue_fiyat (sıra)", res("sue_fiyat"))
print("yeniden hesap, düzeltilmiş fiyatla", res("adj"))
print("yeniden hesap, HAM fiyatla (sızıntısız)", res("raw"))
print("iki tanımın Spearman uyumu", fr[["adj","raw"]].corr(method="spearman").iloc[0,1])
