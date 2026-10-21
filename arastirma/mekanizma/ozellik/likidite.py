"""Gelgit (likidite) ozellikleri. Sim'de `likidite` serisi (yuksek = sikilasma), gercekte NFCI benzeri."""


def likidite_degisim(seri, n=63):
    return seri - seri.shift(n)
