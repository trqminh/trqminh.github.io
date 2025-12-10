import csv
import re
from html import escape
from pathlib import Path

CSV_PATH = Path("data/all_pubs.csv")
OUTPUT_PATH = Path("data/selected_pubs.html")
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


def parse_authors(raw: str):
    raw = raw.strip().strip('"')
    if ";" in raw:
        parts = [p.strip() for p in raw.split(";") if p.strip()]
        sep = ";"
    else:
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        sep = ","

    display_names = []
    bib_names = []
    for part in parts:
        name = part
        if sep == ";" and "," in part:
            last, first = [p.strip() for p in part.split(",", 1)]
            name = f"{first} {last}"
        display_names.append(name)
        bib_names.append(name.replace("*", ""))
    return display_names, bib_names


def render_authors_html(names):
    rendered = []
    for name in names:
        cls = "author me" if "minh tran" in name.lower() else "author"
        rendered.append(f'<span class="{cls}">{escape(name)}</span>')
    return ", ".join(rendered)


def build_bibtex(row: dict, bib_authors: list[str]) -> str:
    title = row.get("Title", "").strip()
    publication = row.get("Publication", "").strip()
    year = row.get("Year", "").strip()
    pages = row.get("Pages", "").strip()
    volume = row.get("Volume", "").strip()
    number = row.get("Number", "").strip()
    publisher = row.get("Publisher", "").strip()
    type_val = row.get("Type", "").strip().lower()
    slug = slugify(title)
    first_author_token = slugify(bib_authors[0]) if bib_authors else "pub"
    key = f"{first_author_token}{year}{slug.split('_')[0]}"

    if "journal" in type_val:
        fields = [
            f"title={{{{{title}}}}}",
            f"author={{{{{' and '.join(bib_authors)}}}}}",
            f"journal={{{{{publication}}}}}",
            f"year={{{{{year}}}}}",
        ]
        if volume:
            fields.append(f"volume={{{{{volume}}}}}")
        if number:
            fields.append(f"number={{{{{number}}}}}")
        if pages:
            fields.append(f"pages={{{{{pages}}}}}")
        if publisher:
            fields.append(f"publisher={{{{{publisher}}}}}")
        entry_type = "@article"
    else:
        fields = [
            f"title={{{{{title}}}}}",
            f"author={{{{{' and '.join(bib_authors)}}}}}",
            f"booktitle={{{{{publication}}}}}",
            f"year={{{{{year}}}}}",
        ]
        if pages:
            fields.append(f"pages={{{{{pages}}}}}")
        if publisher:
            fields.append(f"publisher={{{{{publisher}}}}}")
        entry_type = "@inproceedings"

    fields_text = ",\n  ".join(fields)
    return f"""{entry_type}{{{key},
  {fields_text}
}}"""


def render_publication(row: dict) -> str:
    title = row.get("Title", "").strip()
    authors_display, bib_authors = parse_authors(row.get("", ""))
    authors_html = render_authors_html(authors_display)
    publication = row.get("Publication", "").strip()
    abbrev = row.get("Abbreviate", "").strip()
    year = row.get("Year", "").strip()

    main_link = row.get("Page") or row.get("Paper") or row.get("Code") or "#"
    paper_link = row.get("Paper", "").strip()
    code_link = row.get("Code", "").strip()
    page_link = row.get("Page", "").strip()

    image_src = pick_thumbnail(title)
    conference_line = f"{abbrev} &middot; {year} &middot;"
    bibtex = build_bibtex(row, bib_authors)

    links_html = []
    if page_link:
        links_html.append(f'<a href="{escape(page_link)}" class="pub-link">Project page</a>')
    if paper_link:
        links_html.append(f'<a href="{escape(paper_link)}" class="pub-link">Paper</a>')
    if code_link:
        links_html.append(f'<a href="{escape(code_link)}" class="pub-link">Code</a>')

    links_block = "\n        ".join(links_html)

    return f"""
                <div class="publication">
                    <img src="{escape(image_src)}" ></img>
                    <div class="pub-info">
                        <p><strong><a href="{escape(main_link)}">{escape(title)}</a></strong><br>
                        {authors_html}<br>
                        <span class="conference">{escape(conference_line)}</span><br>
                        </p>
                        <div class="pub-links">
        {links_block}
                        </div>
                    </div>
                </div>
""".rstrip()


def main() -> None:
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = [
            row for row in csv.DictReader(f) if row.get("Selected", "").strip().lower() == "yes"
        ]

    rendered = [render_publication(row) for row in rows]
    OUTPUT_PATH.write_text("\n\n".join(rendered), encoding="utf-8")
    print(f"Wrote {len(rows)} selected publications to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
