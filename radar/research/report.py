"""Sinyal raporları: her sinyal iki evrende (tümü, yatırılabilir) ve üç vadede tek başına değerlendirilir.

    python -m radar.research.report road3     → reports/research/road3.md
"""

from __future__ import annotations

import sys
import time

import pandas as pd

from radar import config
from radar.research import evaluate as ev
from radar.research import panel

REPORT_DIR = config.ROOT / "reports" / "research"
SHOW = ["1a", "3a", "1y"]


def universes(p: dict) -> dict[str, pd.DataFrame]:
    member = panel.membership(p["securities"], p["price"].index, p["price"].columns) & p["price"].notna()
    investable = member & (p["raw"] >= 5) & ((p["dollar_volume"] >= 1e6) | p["dollar_volume"].isna())
    return {"tümü": member, "yatırılabilir (≥5 $, ≥1 M$/gün)": investable}


def verdict(rows: list[dict], kind: str) -> str:
    """3 aylık vadede kaba hüküm; ağırlıklar 4. aşamada belirlenecek."""
    r = next((x for x in rows if x["vade"] == "3a"), None)
    if not r:
        return "veri yetersiz"
    t = r.get("t" if kind == "olay" else "IC_t", 0)
    eff = r.get("ort_fazla" if kind == "olay" else "IC", 0)
    if abs(t) >= 3:
        return ("güçlü pozitif" if eff > 0 else "güçlü negatif")
    if abs(t) >= 2:
        return ("zayıf pozitif" if eff > 0 else "zayıf negatif")
    return "anlamlı değil"


def build(signals: dict[str, pd.DataFrame], p: dict, title: str, notes: dict[str, str] | None = None) -> str:
    notes = notes or {}
    price, sec = p["price"], p["securities"]
    lines = [f"# {title}", "",
             f"Dönem: 2015 → {ev.HOLDOUT_START.date()} öncesi (son dönem kullanılmadı). Fazla getiri: aynı evrenin "
             "haftalık medyanına göre. Olay sinyallerinde t değeri örtüşmeyen haftalarla hesaplanır. "
             "Hüküm 3 aylık vadeye göredir: |t| ≥ 3 güçlü, ≥ 2 zayıf.", ""]
    summary = []
    for name, sig in signals.items():
        is_event = sig.dtypes.iloc[0] == bool
        lines += [f"## {name}", ""]
        if name in notes:
            lines += [notes[name], ""]
        for uni_name, uni in universes(p).items():
            if is_event:
                res = ev.evaluate_event(sig & uni, price, sec, name, universe=uni)
                cols = ["olay", "ort_fazla", "medyan_fazla", "t", "isabet"]
            else:
                res = ev.evaluate(sig.where(uni), price, sec, name, universe=uni)
                cols = ["ort_hisse", "IC", "IC_t", "fark", "isabet_ilk10"]
            tb = res.table().reindex(SHOW)[cols]
            v = verdict(res.rows, "olay" if is_event else "sürekli")
            summary.append({"Sinyal": name, "Evren": uni_name, "Tür": "olay" if is_event else "sürekli",
                            "3a etki": tb.loc["3a", "ort_fazla" if is_event else "IC"],
                            "3a t": tb.loc["3a", "t" if is_event else "IC_t"], "Hüküm": v})
            lines += [f"**{uni_name}** — {v}", "", tb.to_markdown(), "",
                      "Yıllara göre (3a): " + ", ".join(f"{y}: {x:+.3f}" for y, x in res.yearly.get("3a", {}).items()), ""]
    head = [f"# {title}", "", "## Özet", "", pd.DataFrame(summary).to_markdown(index=False), ""]
    return "\n".join(head + lines[2:])


def main(which: str) -> None:
    t = time.time()
    p = panel.build()
    if which == "road3":
        from radar.research import road3
        sig, title = road3.signals(p), "3. yol: kurumsal sinyaller"
        notes = {k: f"8-K Madde {k.split('_')[1]}: {road3.EIGHT_K_ITEMS[k.split('_')[1]]}; son 30 gün içinde dosyalandıysa olay."
                 for k in sig if k.startswith("8k_")}
        notes |= {"icerden_alim_kumesi_3plus": "Son 90 günde en az 3 farklı içeriden kişinin açık piyasa alımı (≥10 bin $, fiyat > 0).",
                  "ust_yonetici_alimi_90g": "Son 90 günde CEO/CFO/başkanın açık piyasa alımı.",
                  "geri_alim_getirisi": "Son yıllık hisse geri alım tutarı / piyasa değeri.",
                  "kurumsal_sahip_degisimi": "13F: kurumsal sahip sayısının çeyreklik değişimi (dönem sonu + 46 gün).",
                  "kurumsal_hisse_degisimi_payi": "13F: kurumların tuttuğu hisse değişimi / dolaşımdaki hisse."}
    else:
        raise SystemExit(f"bilinmeyen rapor: {which}")
    md = build(sig, p, title, notes)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"{which}.md").write_text(md)
    print(md.split("## ", 2)[1][:4000])
    print(f"{round(time.time() - t)} sn")


if __name__ == "__main__":
    main(sys.argv[1])
