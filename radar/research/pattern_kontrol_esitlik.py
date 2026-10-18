import numpy as np, pandas as pd
from radar.research import pattern_arama as A
blocks=A.load()
F=A.FEATS
def run(cols,signs,pool,noise=None,seed=0,ret_picks=False):
    rng=np.random.default_rng(seed); out=[];picks=[]
    for b in blocks:
        m=b["pools"][pool]; X=b["X"][m][:,cols]; s=np.where(np.asarray(signs)>0,X,1-X)
        sc=np.nanmean(s,axis=1) if len(cols)>1 else s[:,0]; ok=np.isfinite(sc)
        if ok.sum()<A.N: out.append(np.nan); continue
        sc=sc[ok]; r=b["net"][m][ok]
        if noise: sc=sc+rng.uniform(0,1e-6,len(sc))
        top=np.argpartition(-sc,A.N-1)[:A.N]; out.append(r[top].mean()); picks.append((b["t"],r[top], sc[top], (sc>=sc[top].min()).sum()))
    return np.array(out),picks
for name,cols,signs,pool in [("piyango −temettu",[F.index("temettu_verimi")],[-1],"piyango"),("piyango −borc",[F.index("borc_ozsermaye")],[-1],"piyango"),("tümü −sue",[F.index("sue_fiyat")],[-1],"tümü"),("büyük +mom",[F.index("momentum_12_1")],[1],"büyük")]:
    r0,p0=run(cols,signs,pool)
    ev0=A.evaluate(blocks,r0)
    rs=[A.evaluate(blocks,run(cols,signs,pool,noise=True,seed=k)[0]) for k in range(5)]
    ties=np.median([p[3] for p in p0])
    allr=np.concatenate([p[1] for p in p0]); 
    print(name,'orijinal şub/mar CAGR',round(ev0['subat_cagr'],3),round(ev0['mart_cagr'],3),'| rastgele eşitlik bozma:',[ (round(e['subat_cagr'],3),round(e['mart_cagr'],3)) for e in rs],'| eşit puanlı aday medyanı',ties,'| tek seçim getirisi medyan %.3f max %.1f, >%%300 olan %d'%(np.median(allr),allr.max(),(allr>3).sum()))
