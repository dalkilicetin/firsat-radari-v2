"""Komut satiri girisi:  python calistir.py <komut> [arguman]"""
import argparse
import sys


def henuz_yok(ad):
    print(f"'{ad}' henuz yok")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Piyasa mekanizmalari laboratuvari")
    alt = ap.add_subparsers(dest="komut")
    alt.add_parser("ornek", help="repodaki ornek verinin ozeti")
    alt.add_parser("katalog", help="kriz katalogu incelemesi")
    sim = alt.add_parser("sim", help="simulasyon deneyleri")
    sim.add_argument("deney", help="kalibre | S1..S6")
    ger = alt.add_parser("gercek", help="gercek ornek kontrolleri")
    ger.add_argument("ad", help="R1 | R2 | R3")
    alt.add_parser("kirilma", help="kirilma noktasi")
    alt.add_parser("kosullar", help="kenetlenme + gelgit kosullari")
    alt.add_parser("rapor", help="laboratuvar raporu")
    alt.add_parser("dip", help="dipten toparlanma kontrol listesi taramasi")
    a = ap.parse_args(argv)
    if a.komut is None:
        ap.print_help()
        return 0
    if a.komut == "ornek":
        from mekanizma.veri import ornek
        return ornek.ozet_yaz()
    if a.komut == "sim":
        from mekanizma.sim import deneyler
        return deneyler.calistir(a.deney)
    if a.komut == "gercek":
        from mekanizma import gercek
        return gercek.calistir(a.ad)
    if a.komut == "kirilma":
        from mekanizma.sim import kirilma_deney
        kirilma_deney.kirilma()
        return 0
    if a.komut == "kosullar":
        from mekanizma.sim import kosullar
        kosullar.kosullar()
        return 0
    if a.komut == "rapor":
        from mekanizma.rapor import lab_raporu
        print(lab_raporu.uret())
        return 0
    if a.komut == "dip":
        print("Dip Radarı kuralları artık tek kaynakta: main dalında dip/kontrol.js (testler: node --test dip/kontrol.test.js).")
        return 0
    if a.komut == "katalog":
        from tarih import inceleme
        print(inceleme.uret())
        return 0
    return henuz_yok(a.komut)


if __name__ == "__main__":
    sys.exit(main())
