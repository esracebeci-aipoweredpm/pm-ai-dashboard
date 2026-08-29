#!/usr/bin/env python3
"""
Haftalık AI x PM dashboard üretici.

Kullanım:
    python3 scripts/build.py weeks/2026-08-01_2026-08-07

data.json dosyasını okur, templates/index-template.html.j2 şablonunu doldurur
ve aynı klasöre index.html olarak yazar.
"""
import json
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent


def build_week(week_dir: Path):
    data_path = week_dir / "data.json"
    if not data_path.exists():
        print(f"HATA: {data_path} bulunamadı.")
        sys.exit(1)

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Kaynağı olmayan kanallar dashboard'da gösterilmez — bir kanal ancak
    # ilk kaynağı eklendiğinde görünür olur.
    channels = [ch for ch in data["channels"] if ch["cards"]]

    total_sources = sum(len(ch["cards"]) for ch in channels)

    # url_label verilmemişse otomatik türet (https:// ve www. olmadan)
    for ch in channels:
        for card in ch["cards"]:
            if not card.get("url_label"):
                label = card["url"].replace("https://", "").replace("http://", "").replace("www.", "")
                card["url_label"] = label.rstrip("/")

    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    template = env.get_template("index-template.html.j2")

    html = template.render(
        week_label=data["week_label"],
        date_range_title=data["date_range_title"],
        date_range_pill=data["date_range_pill"],
        channels=channels,
        themes=data.get("themes", []),
        total_sources=total_sources,
    )

    out_path = week_dir / "index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Oluşturuldu: {out_path} ({total_sources} kaynak)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python3 scripts/build.py weeks/<hafta-klasörü>")
        sys.exit(1)
    build_week(Path(sys.argv[1]))
