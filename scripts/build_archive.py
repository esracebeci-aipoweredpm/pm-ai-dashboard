#!/usr/bin/env python3
"""
Tüm haftaları listeleyen ana/arşiv sayfası üretici.

Kullanım:
    python3 scripts/build_archive.py

weeks/ altındaki her hafta klasöründeki data.json'u okuyup
templates/archive-template.html.j2 şablonunu doldurur ve
pm-ai-dashboard/index.html (proje kökü) olarak yazar.

Yeni bir hafta eklendiğinde veya bir haftanın data.json'u
güncellendiğinde bu script yeniden çalıştırılmalı.
"""
import json
import re
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent


def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", "", html)


def build_archive():
    weeks = []
    weeks_dir = ROOT / "weeks"
    for week_dir in sorted(weeks_dir.iterdir(), reverse=True):
        data_path = week_dir / "data.json"
        if not data_path.exists():
            continue
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_sources = sum(len(ch["cards"]) for ch in data["channels"])
        themes = data.get("themes", [])
        preview = strip_tags(themes[0]) if themes else ""

        weeks.append({
            "folder": week_dir.name,
            "week_label": data["week_label"],
            "date_range_title": data["date_range_title"],
            "total_sources": total_sources,
            "preview": preview,
        })

    if not weeks:
        print("HATA: weeks/ altında data.json içeren hiçbir hafta bulunamadı.")
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    template = env.get_template("archive-template.html.j2")
    html = template.render(weeks=weeks)

    out_path = ROOT / "index.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Oluşturuldu: {out_path} ({len(weeks)} hafta)")


if __name__ == "__main__":
    build_archive()
