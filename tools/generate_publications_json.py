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


VENUE_OVERRIDES = {"IEEE transactions on medical imaging": "IEEE Transactions on Medical Imaging"}


def format_venue(row: dict) -> tuple[str, str]:
    """Turn the raw Publication column into a display venue plus any award marker."""
    raw = row.get("Publication", "").strip()
    abbrev = row.get("Abbreviate", "").strip()
    year = row.get("Year", "").strip()

    award = ""
    match = re.search(r"\\textbf\{([^}]*)\}", raw)
    if match:
        award = match.group(1).strip()
        raw = re.sub(r",?\s*\\textbf\{[^}]*\}", "", raw)

    full = raw.strip().strip(",").strip()
    full = re.sub(r"^The\s+", "", full)
    full = re.sub(r"^(19|20)\d{2}\s+", "", full)
    full = re.sub(r"^\d+(st|nd|rd|th)\s+", "", full)
    full = re.sub(r"^Proceedings of (the\s+)?", "", full)
    full = re.sub(r"\s*\([A-Za-z0-9\-]+\)\s*$", "", full)
    full = re.sub(r"\s*[\u2013\u2014-]\s*[A-Z]{2,}\s+(19|20)\d{2}\s*$", "", full)
    full = re.sub(r",?\s*(19|20)\d{2}\s*$", "", full)
    full = full.strip().strip(",").strip()
    full = VENUE_OVERRIDES.get(full, full)

    if not full:
        full = abbrev
    elif abbrev and abbrev.lower() not in full.lower():
        full = f"{full} ({abbrev})"

    venue = f"{full}, {year}".strip(", ") if year else full
    return venue, award


def parse_authors(raw: str) -> list[str]:
    raw = raw.strip().strip('"')
    if ";" in raw:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
    else:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
    return parts


def build_entry(row: dict) -> dict:
    title = row.get("Title", "").strip()
    venue, award = format_venue(row)
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
    group = row.get("Group", "").strip()

    return {
        "title": title,
        "authors": parse_authors(row.get("", "")),
        "venue": venue,
        "thumbnail": thumbnail,
        "selected": selected,
        "group": group,
        "award": award,
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
