"""Telefon öncelikli statik site: haftalık liste, hisse kartları, karne, otopsi (GitHub Pages).

Girdi: haftalik.veri() sözlüğü. Çıktı: site/ klasörü (index.html, karne.html, otopsi.html, hisse/*.html, otopsi/*.html, stil.css).
"""

from __future__ import annotations

import html
import shutil
from pathlib import Path

from radar import config

OUT = config.ROOT / "site"

# Sade çizgi simgeler (24×24, stroke = currentColor)
IKON = {
    "yukselis": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "is_iyilesiyor": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "dipten_kalkti": '<path d="M12 19V5"/><path d="M6 11l6-6 6 6"/><path d="M4 21h16"/>',
    "sektor": '<rect x="3" y="11" width="5" height="10" rx="1"/><rect x="10" y="6" width="5" height="15" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/>',
    "iceriden": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M17 11v6M14 14h6"/>',
    "yakin_haber": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "ret": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "dikkat": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/>',
    "belge": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    "liste": '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/>',
    "karne": '<path d="M9 4h6v3H9z"/><path d="M7 5H5v16h14V5h-2"/><path d="M9 13l2 2 4-4"/>',
    "otopsi": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.5-4.5"/>',
    "geri": '<path d="M15 5l-7 7 7 7"/>',
    "ileri": '<path d="M9 5l7 7-7 7"/>',
    "piyasa": '<path d="M3 12h4l3-7 4 14 3-7h4"/>',
    "tamam": '<path d="M5 12l5 5 9-10"/>',
    "yok": '<path d="M6 12h12"/>',
    "carpi": '<path d="M7 7l10 10M17 7L7 17"/>',
}


def ikon(ad: str, boyut: int = 20, cls: str = "") -> str:
    return (f'<svg class="ikon {cls}" width="{boyut}" height="{boyut}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IKON[ad]}</svg>')


def e(x) -> str:
    return html.escape("" if x is None else str(x))


def yuzde(x, isaret=True, ondalik=0, bos="—") -> str:
    if x is None:
        return bos
    v = x * 100
    s = f"{abs(v):.{ondalik}f}".replace(".", ",")
    if not isaret:
        return f"%{s}"
    return ("+" if v > 0 else "−" if v < 0 else "") + f"%{s}"


BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def _son_kelime(n: int) -> str:
    n = abs(int(n))
    if n == 0:
        return "sıfır"
    if n % 10:
        return BIRLER[n % 10]
    if n % 100:
        return ONLAR[(n % 100) // 10]
    if n % 1000:
        return "yüz"
    return "bin" if n % 1_000_000 else "milyon"


def _son_unlu(kelime: str) -> str:
    return next(c for c in reversed(kelime) if c in "aeıioöuü")


def bulunma(n: int) -> str:
    """Sayıya bulunma eki: 10'da, 20'de, 3'te, 40'ta."""
    k = _son_kelime(n)
    sert = k[-1] in "çfhkpsşt"
    unlu = "a" if _son_unlu(k) in "aıou" else "e"
    return f"{n}'{'t' if sert else 'd'}{unlu}"


def ayrilma(n: int) -> str:
    """Sayıya ayrılma eki (iyelikten sonra): %99'undan, %40'ından, %3'ünden → iyelik + 'nden/ndan'."""
    k = _son_kelime(n)
    u = _son_unlu(k)
    v = {"a": "ı", "ı": "ı", "o": "u", "u": "u", "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[u]
    d = "a" if u in "aıou" else "e"
    return f"{n}'{'s' if k[-1] in 'aeıioöuü' else ''}{v}nd{d}n"


def iyelik(n: int) -> str:
    """Sayıya 3. tekil iyelik eki: 1'i, 2'si, 3'ü, 6'sı, 10'u."""
    k = _son_kelime(n)
    u = _son_unlu(k)
    v = {"a": "ı", "ı": "ı", "o": "u", "u": "u", "e": "i", "i": "i", "ö": "ü", "ü": "ü"}[u]
    return f"{n}'{'s' if k[-1] in 'aeıioöuü' else ''}{v}"


def oran_metni(p: float | None, iyelikli: bool = False) -> str:
    """0,6 → "10'da 6" (iyelikli: "10'da 6'sı"); küçük oranlar "N'de 1"."""
    if p is None:
        return "—"
    if p <= 0:
        return "hiçbiri"
    if p >= 0.095:
        x = round(p * 10)
        return f"{bulunma(10)} {iyelik(x) if iyelikli else x}"
    n = round(1 / p)
    return f"{bulunma(n)} {iyelik(1) if iyelikli else 1}"


def para(x) -> str:
    if x is None:
        return "—"
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " $"


def noktalar(n: int, toplam: int = 6) -> str:
    return '<span class="nokta" aria-label="{0} / {1}">{2}</span>'.format(n, toplam, "●" * n + "○" * (toplam - n))


CSS = """
:root{--zemin:#F5F5F1;--kart:#FFFFFF;--cizgi:#E2E3DE;--ince:#EEEFEA;--yazi:#1B1F24;--soluk:#4A525C;--mavi:#1F4FB8;
--mavi-zemin:#EEF2FB;--mavi-koyu:#163A8A;--turuncu:#A3400B;--turuncu-zemin:#FDF0E8;--turuncu-koyu:#8A3509;--sari:#6B4E00;
--sari-zemin:#FBF4DF;--gri-zemin:#F0F0EC}
@media (prefers-color-scheme:dark){:root{--zemin:#121417;--kart:#1B1E23;--cizgi:#2C3038;--ince:#262A31;--yazi:#E8EAED;
--soluk:#A9B0BA;--mavi:#8FB0FF;--mavi-zemin:#1E2A44;--mavi-koyu:#B9CCFF;--turuncu:#FFA36B;--turuncu-zemin:#3A2418;
--turuncu-koyu:#FFC29C;--sari:#F0CF73;--sari-zemin:#352D14;--gri-zemin:#24272D}}
*{box-sizing:border-box}
body{margin:0;background:var(--zemin);color:var(--yazi);font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
-webkit-text-size-adjust:100%;line-height:1.5}
a{color:var(--mavi)}
.sayfa{max-width:640px;margin:0 auto;padding:20px 16px 48px;display:flex;flex-direction:column;gap:16px}
.ust{display:flex;flex-direction:column;gap:2px}
.etiket{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--mavi)}
h1{margin:0;font-size:28px;line-height:1.15}
h2{margin:0;font-size:19px;line-height:1.3;display:flex;align-items:center;gap:8px}
.alt{font-size:14px;color:var(--soluk)}
.sekme{display:flex;gap:6px;background:var(--ince);padding:4px;border-radius:999px;position:sticky;top:8px;z-index:5}
.sekme a{flex:1;display:flex;align-items:center;justify-content:center;gap:6px;padding:11px 4px;border-radius:999px;
color:var(--soluk);text-decoration:none;font-size:14px;font-weight:500;min-height:44px}
.sekme a.aktif{background:var(--kart);color:var(--yazi);font-weight:600;box-shadow:0 1px 2px rgba(0,0,0,.06)}
.kart{background:var(--kart);border:1px solid var(--cizgi);border-radius:16px;padding:16px;display:flex;flex-direction:column;gap:10px}
a.kart{color:var(--yazi);text-decoration:none}
a.kart:active{transform:scale(.995)}
.ikon{flex:none}
.satir{display:flex;align-items:center;gap:12px}
.sira{width:32px;height:32px;flex:none;border-radius:999px;background:var(--yazi);color:var(--zemin);display:flex;
align-items:center;justify-content:center;font-weight:700;font-size:14px}
.sembol{font-weight:700;font-size:18px}
.kucuk{font-size:13px;color:var(--soluk)}
.rozet{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.r-mavi{background:var(--mavi-zemin);color:var(--mavi-koyu)}.r-gri{background:var(--gri-zemin);color:var(--soluk)}
.r-turuncu{background:var(--turuncu-zemin);color:var(--turuncu-koyu)}.r-sari{background:var(--sari-zemin);color:var(--sari)}
.nokta{font-size:15px;letter-spacing:2px;color:var(--mavi)}
.isaretler{display:flex;gap:6px;flex-wrap:wrap}
.isaretler .ikon{color:var(--soluk)}.isaretler .acik{color:var(--mavi)}
.izgara{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.izgara3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.kutu{background:var(--zemin);border-radius:12px;padding:10px 12px;display:flex;flex-direction:column;gap:2px;min-width:0}
.kutu.mavi{background:var(--mavi-zemin)}
.sayi{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:18px}
.arti{color:var(--mavi)}.eksi{color:var(--turuncu)}
.cizgili{border-top:1px solid var(--ince);padding-top:10px}
.madde{display:flex;gap:12px;align-items:flex-start}
.daire{width:28px;height:28px;flex:none;border-radius:999px;display:flex;align-items:center;justify-content:center}
.d-mavi{background:var(--mavi-zemin);color:var(--mavi)}.d-gri{background:var(--gri-zemin);color:var(--soluk)}
.d-turuncu{background:var(--turuncu-zemin);color:var(--turuncu)}
.cubuk{height:10px;background:var(--ince);border-radius:999px;overflow:hidden}
.cubuk span{display:block;height:10px;background:var(--mavi);border-radius:999px}
.cubuk.t span{background:var(--turuncu)}
.uyari{background:var(--turuncu-zemin);border-color:transparent;color:var(--turuncu-koyu)}
.bilgi{background:var(--mavi-zemin);border-color:transparent;color:var(--mavi-koyu)}
details summary{cursor:pointer;font-weight:600;padding:4px 0;min-height:32px}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;line-height:1.8;color:var(--soluk)}
.geri{display:inline-flex;align-items:center;gap:4px;font-weight:600;text-decoration:none;padding:10px 0;min-height:44px}
.yol{display:flex;flex-direction:column}
.yol .adim{display:flex;gap:12px}
.yol .cizgi{width:18px;display:flex;flex-direction:column;align-items:center}
.yol .top{width:14px;height:14px;border-radius:999px;margin-top:4px;background:var(--mavi)}
.yol .bag{flex:1;width:2px;background:var(--cizgi)}
.yol .icerik{padding-bottom:14px}
footer{font-size:12px;color:var(--soluk);line-height:1.6}
@media (min-width:720px){.sayfa{max-width:760px}}
"""


def _sekme(aktif: str, kok: str = "") -> str:
    items = [("index.html", "Liste", "liste"), ("karne.html", "Karne", "karne"), ("otopsi.html", "Otopsi", "otopsi")]
    return '<nav class="sekme">' + "".join(
        f'<a href="{kok}{u}" class="{"aktif" if a == aktif else ""}">{ikon(i, 18)}{a}</a>' for u, a, i in items) + "</nav>"


def _sayfa(baslik: str, govde: str, kok: str = "") -> str:
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#F5F5F1"><title>{e(baslik)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{kok}stil.css"></head><body><main class="sayfa">{govde}
<footer>Yatırım tavsiyesi değildir; bir analiz aracıdır. Veriler: SEC, FINRA, borsa fiyatları. Son karar her zaman sizindir.</footer>
</main></body></html>"""


def _ust(baslik: str, alt: str) -> str:
    return f'<header class="ust"><div class="etiket">Fırsat Radarı</div><h1>{e(baslik)}</h1><div class="alt">{e(alt)}</div></header>'


def _sayi(x, cls_otomatik=True, isaret=True) -> str:
    c = "" if x is None or not cls_otomatik else ("arti" if x > 0 else "eksi" if x < 0 else "")
    return f'<span class="sayi {c}">{yuzde(x, isaret)}</span>'


ISARET_ADI = {"yukselis": "Yükselişi sürüyor", "is_iyilesiyor": "İşleri iyileşiyor", "dipten_kalkti": "Dipten kalktı",
              "sektor": "Sektörü yükselişte", "iceriden": "İçeriden alım var", "yakin_haber": "Yakında bilanço var"}


def liste_sayfasi(v: dict) -> str:
    p = v["piyasa"]
    g = [_ust("Bu haftanın listesi", f"{v['tarih_metni']} · {v['veri_metni']}"), _sekme("Liste")]
    g.append(f"""<section class="kart"><h2>{ikon('piyasa')}Piyasanın hali</h2>
<div style="font-size:17px;font-weight:600;line-height:1.35">{e(p['baslik'])}</div>
<div class="izgara3"><div class="kutu"><div class="kucuk">Son 1 ay</div>{_sayi(p['ay'])}</div>
<div class="kutu"><div class="kucuk">Son 1 yıl</div>{_sayi(p['yil'])}</div>
<div class="kutu"><div class="kucuk">Dalgalanma</div><span style="font-weight:600" class="{'eksi' if p['dalga'] == 'Yüksek' else ''}">{e(p['dalga'])}</span></div></div>
<div class="kucuk" style="font-size:14px">{e(p['metin'])}</div></section>""")
    g.append(f'<section style="display:flex;flex-direction:column;gap:10px"><h2>{ikon("liste")}Öneriler '
             f'<span class="kucuk" style="font-weight:400">· {len(v["liste"])} hisse</span></h2>'
             '<div class="kucuk">Simgeler 6 işareti gösterir; mavi olanlar bu hissede var. Karta dokununca ayrıntı açılır.</div>')
    for h in v["liste"]:
        isa = "".join(f'<span title="{e(ISARET_ADI[n])}">{ikon(n, 18, "acik" if h["isaretler"][n] else "")}</span>'
                      for n in ISARET_ADI)
        g.append(f"""<a class="kart" href="hisse/{e(h['sembol'])}.html"><div class="satir"><div class="sira">{h['sira']}</div>
<div style="flex:1;min-width:0"><div class="sembol">{e(h['sembol'])}</div><div class="kucuk">{e(h['ad'])} · {e(h['sektor'])} · {e(h['buyukluk'])}</div></div>
{_rozet_aciklama(h)}</div><div style="font-size:15px">{e(h['neden'])}</div>
<div class="satir" style="justify-content:space-between;flex-wrap:wrap;gap:8px"><div class="isaretler">{isa}</div>
<div class="kucuk">{noktalar(h['olumlu'])} · {e(h['degisim'])}</div></div></a>""")
    if v.get("cikanlar"):
        g.append('<div class="kart" style="font-size:14px"><b>Listeden çıkanlar</b>' +
                 "".join(f'<div class="cizgili"><b>{e(c["sembol"])}</b> {e(c["neden"])}</div>' for c in v["cikanlar"]) + "</div>")
    g.append("</section>")
    a = v["alinmaz"]
    blk = f'<section class="kart"><h2>{ikon("ret")}Alınmaz ve dikkat</h2>'
    blk += ('<div class="kucuk" style="font-size:14px">Geçmiş testte (2013–2022) bu uyarıların hiçbiri kaybettirenleri kazandıranlardan '
            'yeterince ayıramadı; bu yüzden hisseler listeden otomatik çıkarılmıyor, uyarı olarak gösteriliyor.</div>')
    blk += f'<div class="kucuk" style="font-weight:700;color:var(--turuncu-koyu)">Ciddi uyarı · şirket güvenilirliği</div>'
    blk += "".join(f'<div class="madde cizgili"><div style="min-width:52px;font-weight:700">{e(x["sembol"])}</div><div style="font-size:14px">{e(x["neden"])}</div></div>'
                   for x in a["kesin"]) or '<div class="kucuk">Bu hafta yok.</div>'
    blk += f'<div class="kucuk" style="font-weight:700;color:var(--sari);padding-top:6px">Dikkat · tek başına ret sebebi değil</div>'
    blk += "".join(f'<div class="madde cizgili"><div style="min-width:52px;font-weight:700">{e(x["sembol"])}</div><div style="font-size:14px">{e(x["neden"])}</div></div>'
                   for x in a["dikkat"]) or '<div class="kucuk">Bu hafta yok.</div>'
    g.append(blk + "</section>")
    if v.get("yaklasan"):
        g.append(f'<section class="kart"><h2>{ikon("yakin_haber")}Yaklaşan önemli günler</h2>' + "".join(
            f'<div class="madde cizgili"><div class="rozet r-mavi" style="min-width:64px;justify-content:center">{e(y["tarih"])}</div>'
            f'<div><div style="font-weight:700">{e(y["sembol"])}</div><div class="kucuk" style="font-size:14px">{e(y["ne"])}</div></div></div>'
            for y in v["yaklasan"]) + '<div class="kucuk">Tarihler son rapor tarihinden tahmin edilmiştir.</div></section>')
    return _sayfa("Fırsat Radarı — Bu hafta", "".join(g))


def _rozet_aciklama(h: dict) -> str:
    if h.get("dikkat"):
        return f'<span class="rozet r-sari">{ikon("dikkat", 14)}Dikkat</span>'
    if h.get("yeni_aciklama"):
        return f'<span class="rozet r-mavi">{ikon("belge", 14)}Yeni açıklama</span>'
    return ""


def kart_sayfasi(v: dict, h: dict) -> str:
    g = [f'<a class="geri" href="../index.html">{ikon("geri", 18)}Listeye dön</a>']
    g.append(f"""<header class="kart"><div class="etiket">Listede {h['sira']}. sıra</div>
<div><h1>{e(h['sembol'])}</h1><div class="alt">{e(h['ad'])} · {e(h['sektor'])} · {e(h['buyukluk'])}</div></div>
<div style="font-size:16px">{e(h['ozet'])}</div>
<div class="izgara"><div class="kutu mavi"><div class="kucuk" style="color:var(--mavi-koyu);font-weight:600">3 ay için</div>
<div class="kucuk">{e(h['vade_3a'])}</div></div><div class="kutu mavi"><div class="kucuk" style="color:var(--mavi-koyu);font-weight:600">6 ay için</div>
<div class="kucuk">{e(h['vade_6a'])}</div></div></div></header>""")
    rows = []
    for n in ISARET_ADI:
        on = h["isaretler"][n]
        rows.append(f'<div class="madde cizgili"><div class="daire {"d-mavi" if on else "d-gri"}">{ikon(n, 16)}</div>'
                    f'<div><div style="font-weight:600">{e(ISARET_ADI[n] if on else h["isaret_yok"][n])}</div>'
                    f'<div class="kucuk" style="font-size:14px">{e(h["isaret_metni"][n])}</div></div></div>')
    g.append(f'<section class="kart"><h2>Neden listede? <span class="kucuk" style="font-weight:400">· 6 işaretten {iyelik(h["olumlu"])}</span></h2>{"".join(rows)}</section>')
    b = h["benzer"]
    if b:
        g.append(
                 f"""<section class="kart"><h2>Geçmişte buna benzeyenler</h2>
<div class="kucuk" style="font-size:14px">2013–2022 arasında aynı işaretleri taşıyan {b['adet_metni']} hisse-hafta (borsadan çıkmış ve batmış şirketler dahil). Masraflar düşülmüş sonuçlar:</div>
{_cubuk('3 ayda borsadan çok kazandıran', b['borsayi_gecen_3a'])}
{_cubuk('6 ayda borsadan çok kazandıran', b['borsayi_gecen_6a'])}
{_cubuk("3 ayda dönemin en çok kazandıranlarına giren", b['kazanan_3a'], not_="Rastgele seçilse 20'de 1 olurdu.")}
{_cubuk("3 ayda %30'dan fazla değer kaybeden", b['sert_kayip_3a'], turuncu=True)}
<div class="kucuk" style="font-size:14px">Ortadaki hisse 3 ayda <b>{yuzde(b['medyan_3a'])}</b>, 6 ayda <b>{yuzde(b['medyan_6a'])}</b> getirdi.</div></section>""")
    ac = h.get("aciklamalar") or []
    g.append(f'<section class="kart"><h2>{ikon("belge")}Resmî açıklamalar <span class="kucuk" style="font-weight:400">· son 30 gün, SEC</span></h2>' +
             ("".join(f'<div class="madde cizgili"><div class="rozet r-gri" style="min-width:64px;justify-content:center">{e(x["tarih"])}</div>'
                      f'<div style="font-size:14px">{e(x["ne"])}</div></div>' for x in ac) or '<div class="kucuk">Önemli açıklama yok.</div>') + "</section>")
    g.append(f'<section class="kart uyari"><h2>{ikon("dikkat")}Neden almamalı?</h2>' +
             "".join(f'<div style="font-size:15px">{e(x)}</div>' for x in h["almamali"]) + "</section>")
    g.append(f'<details class="kart"><summary>Ayrıntılar (kesin sayılar ve kaynaklar)</summary><div class="mono">{e(h["ayrinti"])}</div></details>')
    return _sayfa(f"{h['sembol']} — Fırsat Radarı", "".join(g), "../")


def _cubuk(etiket: str, p: float | None, not_: str = "", turuncu: bool = False) -> str:
    w = 0 if p is None else max(0, min(100, round(p * 100)))
    return (f'<div style="display:flex;flex-direction:column;gap:6px"><div class="satir" style="justify-content:space-between;font-size:14px">'
            f'<span>{e(etiket)}</span><b>{e(oran_metni(p))}</b></div><div class="cubuk {"t" if turuncu else ""}"><span style="width:{w}%"></span></div>'
            + (f'<div class="kucuk">{e(not_)}</div>' if not_ else "") + "</div>")


def karne_sayfasi(v: dict) -> str:
    k = v["karne"]
    g = [_ust("Karne", "Önerdiğimiz listeler gerçekte ne yaptı? Listeler yayın günü kilitlenir."), _sekme("Karne")]
    for blok in k["bloklar"]:
        s = blok["ozet"]
        kutular = [
            ("Ortadaki hissenin getirisi · 3 ay", _sayi(s.get("medyan_3a")), f"Borsa: {yuzde(s.get('borsa_3a'))}"),
            ("Ortadaki hissenin getirisi · 6 ay", _sayi(s.get("medyan_6a")), f"Borsa: {yuzde(s.get('borsa_6a'))}"),
            ("Borsadan fazla · 3 ay", _sayi(s.get("fazla_borsa_3a")), f"Sektörüne göre {yuzde(s.get('fazla_sektor_3a'))}"),
            ("Benzer büyüklüktekilerden fazla", _sayi(s.get("fazla_esit_3a")), "3 ay ortalaması"),
            ("En çok kazandıranlardan listede", f'<span class="sayi">{e(oran_metni(s.get("kazanan_orani_3a")))}</span>', "Rastgele: 20'de 1"),
            ("Tamamen kaçırılan kazanan", f'<span class="sayi eksi">{e(oran_metni(s.get("tamamen_kacirilan")))}</span>', "Hiç listeye girmedi"),
            ("En büyük düşüş", _sayi(s.get("en_buyuk_dusus")), "Çeyrek başı listeleri"),
            ("Masraflar", f'<span class="sayi">yılda {yuzde(s.get("masraf_yillik"), False, 1)}</span>', "Getiriden düşüldü"),
            ("Liste ne kadar değişiyor", f'<span class="sayi">haftada {s.get("haftalik_yeni_hisse") or 0:.1f}</span>'.replace(".", ","), f"Çeyrekte {s.get('ceyreklik_yeni_hisse') or 0:.1f} hisse".replace(".", ",")),
            ("Borsayı geçen hafta", f'<span class="sayi">{e(oran_metni(s.get("borsayi_gecen_3a")))}</span>', "3 aylık sonuçlar"),
            ("Çeyrek başında alıp tutsaydık", _sayi(s.get("zincir_yillik")), f"Yıllık; borsa {yuzde(s.get('zincir_borsa_yillik'))}"),
            ("Kazananların yakalanan kısmı", f'<span class="sayi">{yuzde(s.get("yakalanan_pay_medyan"), False)}</span>', "Listeye girdikten sonraki pay (orta değer)"),
        ]
        g.append(f'<section class="kart"><h2>{e(blok["baslik"])}</h2><div class="kucuk" style="font-size:14px">{e(blok["aciklama"])}</div><div class="izgara">' +
                 "".join(f'<div class="kutu"><div class="kucuk">{e(a)}</div>{b}<div class="kucuk">{e(c)}</div></div>' for a, b, c in kutular) +
                 "</div>" + (f'<div class="kucuk">Borsadan fazla getirinin %90 güven aralığı: {yuzde(s["ga90_fazla_borsa_3a"][0])} … {yuzde(s["ga90_fazla_borsa_3a"][1])}</div>'
                             if s.get("ga90_fazla_borsa_3a") else "") + "</section>")
    if k.get("listeler"):
        g.append(f'<section style="display:flex;flex-direction:column;gap:10px"><h2>Liste liste</h2>')
        for x in k["listeler"]:
            g.append(f"""<article class="kart"><div class="satir" style="justify-content:space-between"><b>{e(x['tarih'])}</b><span class="kucuk">{e(x['yakalanan'])}</span></div>
<div class="izgara3 kucuk"><div>Bizim 10 hisse</div><div>Borsa (S&amp;P)</div><div>Dönemin en iyi 3'ü</div>
{_sayi(x['bizim_3a'])}{_sayi(x['borsa_3a'], False)}<span class="sayi" style="color:var(--soluk)">{yuzde(x['en_iyi3_3a'])}</span></div>
<div class="kucuk">3 aylık sonuç. 6 ay: {e(x['bizim_6a_metni'])}</div></article>""")
        g.append("</section>")
    g.append("""<details class="kart" open><summary>Test nasıl yapılıyor? (kurallar)</summary><ol style="margin:8px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:8px;font-size:14px;color:var(--soluk)">
<li><b>Batanlar da sayılır.</b> O gün borsada olan her hisse teste girer; sonradan batan, borsadan çıkan ya da satın alınan şirketler dahil. Batan şirketin hissesi sıfır sayılır.</li>
<li><b>Yalnızca o gün bilinen bilgi.</b> Belgeler SEC'e kabul edildiği andan sonra kullanılır; perşembe 16:00'dan (New York) sonra gelen belge sonraki haftaya kalır.</li>
<li><b>Gerçekçi alış fiyatı.</b> Rapordan sonra alınabilecek ilk fiyattan (cuma kapanışı) alınmış sayılır.</li>
<li><b>Masraflar düşülür.</b> Alırken ve satarken; az işlem gören hissede masraf daha yüksektir.</li>
<li><b>Üç karşılaştırma.</b> Borsa (S&amp;P 500), hissenin kendi sektörü ve benzer büyüklükteki hisselerin ortalaması.</li>
<li><b>Ayar ve sınav ayrı.</b> Kurallar 2013–2022 verisiyle ayarlandı; 2023–2026 bir kez, en sonda sınav olarak açıldı. Şimdi her cuma canlı kayıt.</li>
<li><b>Her deneme kayıtlı.</b> Denenen bütün ayarlar deftere yazıldı.</li></ol></details>""")
    return _sayfa("Fırsat Radarı — Karne", "".join(g))


def otopsi_sayfasi(v: dict) -> str:
    o = v["otopsi"]
    g = [_ust("Otopsi", f"{o['donem_metni']} en çok kazandıranları. Neden yükseldiler, biz ne kadarını yakalayabilirdik?"), _sekme("Otopsi")]
    g.append('<section class="kart bilgi"><b>En önemli ayrım</b><div style="font-size:14px">Bir hissenin çeyrekte %200 yükselmesi, '
             'bu %200\'ün önceden yakalanabileceği anlamına gelmez. Her kartta iki sayı var: <b>toplam yükseliş</b> ve işaret görüldükten '
             'sonra alınsaydı elde edilecek <b>yakalanabilir getiri</b>.</div></section>')
    for x in o["kartlar"]:
        g.append(f"""<a class="kart" href="otopsi/{e(x['id'])}.html"><div class="satir" style="justify-content:space-between">
<div class="sembol">{e(x['sembol'])}</div><span class="rozet r-gri">{e(x['tur'])}</span></div>
<div class="izgara"><div class="kutu"><div class="kucuk">Toplam yükseliş</div>{_sayi(x['toplam'])}</div>
<div class="kutu mavi"><div class="kucuk" style="color:var(--mavi-koyu)">Yakalanabilir getiri</div>{_sayi(x.get('yakalanabilir')) if x.get('yakalanabilir') is not None else '<span class="sayi">yok</span>'}</div></div>
<div style="font-size:14px;color:var(--soluk)">{e(x['ozet'])}</div>
<div class="kart {'bilgi' if x['yakalandi'] else 'uyari'}" style="padding:10px 12px;font-size:14px"><b>{e(x['hukum'])}</b> {e(x['hukum_neden'])}</div>
<div class="satir" style="gap:4px;font-weight:600;color:var(--mavi);font-size:14px">Otopsi kartını aç {ikon('ileri', 16)}</div></a>""")
    return _sayfa("Fırsat Radarı — Otopsi", "".join(g))


def otopsi_detay(v: dict, x: dict) -> str:
    g = [f'<a class="geri" href="../otopsi.html">{ikon("geri", 18)}Otopsi listesine dön</a>']
    g.append(f'<header class="kart"><div class="etiket">Otopsi kartı · {e(x["donem"])}</div><h1>{e(x["sembol"])}</h1>'
             f'<div class="alt">{e(x["ad"])} · {e(x["sektor"])} · Tür: {e(x["tur"])}</div></header>')
    d = x.get("dort")
    if d:
        g.append(f"""<section class="kart"><h2>Dört sonuç</h2><div class="izgara">
<div class="kutu"><div class="kucuk">İlk güvenilir işaret</div><b>{e(d['tarih'])}</b><div class="kucuk">Fiyat o gün {e(d['isaret_fiyati'])}</div></div>
<div class="kutu"><div class="kucuk">Alınabilecek ilk fiyat</div><b>{e(d['giris'])}</b><div class="kucuk">{e(d['giris_not'])}</div></div>
<div class="kutu mavi"><div class="kucuk" style="color:var(--mavi-koyu)">Alıştan sonraki getiri</div><span class="sayi">3 ay {yuzde(d['net_3a'], bos='henüz yok')}</span><span class="sayi" style="font-size:15px">6 ay {yuzde(d['net_6a'], bos='henüz yok')}</span></div>
<div class="kutu mavi"><div class="kucuk" style="color:var(--mavi-koyu)">Borsadan fazla (3 ay)</div><span class="sayi">{yuzde(d['fazla_borsa'], bos='henüz yok')}</span><div class="kucuk">Sektörüne göre {yuzde(d['fazla_sektor'], bos='henüz yok')}</div></div>
</div><div class="kucuk">Getiriler alış ve satış masrafları düşülmüş olarak.</div></section>""")
        adimlar = "".join(f'<div class="adim"><div class="cizgi"><div class="top" style="background:{a["renk"]}"></div><div class="bag"></div></div>'
                          f'<div class="icerik"><div style="font-weight:600;font-size:14px">{e(a["etiket"])} <span class="sayi" style="font-size:14px">{e(a["fiyat"])}</span></div>'
                          f'<div class="kucuk">{e(a["not"])}</div></div></div>' for a in x["yol"])
        g.append(f'<section class="kart"><h2>Yakalanabilir getiri</h2><div class="yol">{adimlar}</div>'
                 f'<div class="kutu" style="font-size:14px">{e(x["yol_ozet"])}</div></section>')
    g.append(f'<section class="kart"><h2>1 · Kazanç hikâyesi</h2><div style="font-size:15px"><b>Neden yükseldi?</b> {e(x["hikaye"])}</div>'
             '<div class="kucuk">Yükselişin kaynağı</div><div class="isaretler">' +
             "".join(f'<span class="rozet {"r-mavi" if on else "r-gri"}">{e(ad)}</span>' for ad, on in x["kaynak"]) + "</div>" +
             (_cubuk("Yükselişin tek bir haftadan gelen kısmı", x["tek_hafta"], not_=x.get("tek_hafta_not", ""), turuncu=True) if x.get("tek_hafta") is not None else "") +
             "</section>")
    bilgi = "".join(f'<div class="madde"><div class="daire {"d-mavi" if b["var"] else "d-turuncu"}" style="width:22px;height:22px">'
                    f'{ikon("tamam" if b["var"] else "carpi", 13)}</div><div style="font-size:14px">{e(b["metin"])}</div></div>' for b in x["bilinen"])
    g.append(f'<section class="kart"><h2>2 · İlk yakalanabilir işaret</h2><div style="font-size:15px">{e(x["ilk_metin"])}</div>'
             f'<div class="kucuk">O gün yatırımcının gerçekten ulaşabildiği bilgi</div>{bilgi}</section>')
    bz = x.get("benzer")
    if bz:
        g.append(f'<section class="kart"><h2>3 · Aynı görünüp yükselmeyenler</h2><div style="font-size:15px">{e(bz["metin"])}</div>' +
                 "".join(f'<div class="madde cizgili"><div style="min-width:52px;font-weight:700">{e(t["sembol"])}</div>'
                         f'<div class="sayi eksi" style="font-size:14px">{yuzde(t["net"])}</div></div>' for t in bz["ornek"]) +
                 (f'<div class="kart bilgi" style="padding:10px 12px;font-size:14px"><b>Kazananı ayıran:</b> {e(bz["ayiran"])}</div>' if bz.get("ayiran") else "") +
                 (f'<div class="kart uyari" style="padding:10px 12px;font-size:14px"><b>Yanılmanın ortak nedeni:</b> {e(bz["neden"])}</div>' if bz.get("neden") else "") +
                 "</section>")
    g.append(f'<details class="kart"><summary>Ayrıntılar (kesin sayılar ve kaynaklar)</summary><div class="mono">{e(x["ayrinti"])}</div></details>')
    return _sayfa(f"{x['sembol']} otopsi — Fırsat Radarı", "".join(g), "../")


def yaz(v: dict, out: Path = OUT) -> Path:
    if out.exists():
        shutil.rmtree(out)
    (out / "hisse").mkdir(parents=True)
    (out / "otopsi").mkdir()
    (out / "stil.css").write_text(CSS.strip() + "\n")
    (out / ".nojekyll").write_text("")
    (out / "index.html").write_text(liste_sayfasi(v))
    (out / "karne.html").write_text(karne_sayfasi(v))
    (out / "otopsi.html").write_text(otopsi_sayfasi(v))
    for h in v["liste"]:
        (out / "hisse" / f"{h['sembol']}.html").write_text(kart_sayfasi(v, h))
    for x in v["otopsi"]["kartlar"]:
        (out / "otopsi" / f"{x['id']}.html").write_text(otopsi_detay(v, x))
    return out
