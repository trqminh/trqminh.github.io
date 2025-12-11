import csv
import json
import re
from pathlib import Path

CSV_PATH = Path("data/all_pubs.csv")
OUTPUT_PATH = Path("publications.json")
THUMB_DIR = Path("pub_thumbnails")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "publication"


def pick_thumbnail(title: str) -> str:
    slug = slugify(title)
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        candidate = THUMB_DIR / f"{slug}{ext}"
        if candidate.exists():
            return str(candidate).replace("\\", "/")
    return str((THUMB_DIR / f"{slug}.png")).replace("\\", "/")


def parse_authors(raw: str) -> list[str]:
    raw = raw.strip().strip('"')
    if ";" in raw:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
    else:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts


def build_entry(row: dict) -> dict:
    title = row.get("Title", "").strip()
    abbrev = row.get("Abbreviate", "").strip()
    year = row.get("Year", "").strip()
    venue = f"{abbrev} {year}".strip() if abbrev or year else row.get("Publication", "").strip()
    thumbnail = row.get("thumbnail", "").strip()
    if not thumbnail:
        thumbnail = pick_thumbnail(title)

    paper_link = row.get("Paper", "").strip()
    code_link = row.get("Code", "").strip()
    project_link = row.get("Page", "").strip()

    links = {}
    if paper_link:
        links["pdf"] = paper_link
    if code_link:
        links["code"] = code_link
    if project_link:
        links["project"] = project_link

    selected = 1 if row.get("Selected", "").strip().lower() == "yes" else 0

    return {
        "title": title,
        "authors": parse_authors(row.get("", "")),
        "venue": venue,
        "thumbnail": thumbnail,
        "selected": selected,
        "award": "",
        "links": links,
    }


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        publications = [build_entry(row) for row in reader]

    OUTPUT_PATH.write_text(json.dumps({"publications": publications}, indent=2), encoding="utf-8")
    print(f"Wrote {len(publications)} entries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
