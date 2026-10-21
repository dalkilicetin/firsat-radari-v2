import numpy as np


def blok_bootstrap_ga(x, blok=None, n=2000, ga=0.90, tohum=0):
    """Hareketli blok bootstrap ile ortalamanin guven araligi. n_gozlem < 4 ise (nan, nan)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    m = len(x)
    if m < 4:
        return float("nan"), float("nan")
    b = blok or max(1, int(np.ceil(m ** (1 / 3))))
    rng = np.random.default_rng(tohum)
    nb = int(np.ceil(m / b))
    bas = rng.integers(0, m - b + 1, size=(n, nb))
    idx = (bas[:, :, None] + np.arange(b)[None, None, :]).reshape(n, -1)[:, :m]
    ort = x[idx].mean(axis=1)
    a = (1 - ga) / 2
    return float(np.quantile(ort, a)), float(np.quantile(ort, 1 - a))


def ozet(x, tohum=0):
    """n, ort, medyan, isabet (x>0 orani), std, min, max, ga_alt, ga_ust."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) == 0:
        return dict(n=0, ort=None, medyan=None, isabet=None, std=None, min=None, max=None, ga_alt=None, ga_ust=None)
    lo, hi = blok_bootstrap_ga(x, tohum=tohum)
    f = lambda v: None if np.isnan(v) else float(v)
    return dict(n=int(len(x)), ort=float(x.mean()), medyan=float(np.median(x)), isabet=float((x > 0).mean()),
                std=float(x.std(ddof=1)) if len(x) > 1 else None, min=float(x.min()), max=float(x.max()),
                ga_alt=f(lo), ga_ust=f(hi))
