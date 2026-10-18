import numpy as np, pandas as pd
from radar.research import pattern_arama as A
blocks=A.load(); F=A.FEATS
def run(col,sign,pool,cap=None):
    rows=[]
    for b in blocks:
        m=b["pools"][pool]; x=b["X"][m][:,F.index(col)]; s=x if sign>0 else 1-x; ok=np.isfinite(s)
        if ok.sum()<10: continue
        r=b["net"][m][ok]; top=np.argpartition(-s[ok],9)[:10]; rr=r[top]
        if cap: rr=np.minimum(rr,cap)
        rows.append({"t":b["t"],"ay":b["ay"],"yil":b["yil"],"r":rr.mean(),"med":np.median(rr),"spy":b["spy"]})
    return pd.DataFrame(rows)
def chain(d,months):
    d=d[d.ay.isin(months)].dropna(); y=len(d)/4
    w=np.cumprod(1+d.r); dd=(w/np.maximum.accumulate(w)-1).min()
    yr=(1+d.set_index('yil')[['r','spy']]).groupby(level=0).prod()-1
    return dict(cagr=round(np.prod(1+d.r)**(1/y)-1,3), spy=round(np.prod(1+d.spy)**(1/y)-1,3), dd=round(dd,2), yil_ustu=f"{int((yr.r>yr.spy).sum())}/{len(yr)}")
for name,col,sign,pool in [("A: kâr açıklaması sonrası en çok cezalandırılan (tümü)","sue_fiyat",-1,"tümü"),("B: büyük hisselerde momentum","momentum_12_1",1,"büyük")]:
    print('==',name)
    for lab,cap in [("normal",None),("tek seçim en çok +%100 sayılırsa",1.0)]:
        d=run(col,sign,pool,cap)
        print(' ',lab,{k:chain(d,v) for k,v in A.CHAINS.items()})
    d=run(col,sign,pool)
    dx=d[~d.yil.isin([2020,2021])]
    print('  2020-21 hariç',{k:chain(dx,v) for k,v in A.CHAINS.items()})
    for a,z in [(2010,2014),(2015,2019),(2020,2022),(2023,2026)]:
        dd=d[(d.yil>=a)&(d.yil<=z)]
        print(f'  {a}-{z}',{k:chain(dd,v)['cagr'] for k,v in A.CHAINS.items()},'spy',{k:chain(dd,v)['spy'] for k,v in A.CHAINS.items()})
    print('  seçilen hisselerin medyan 3 aylık getirisi', round(d.med.median(),3))
