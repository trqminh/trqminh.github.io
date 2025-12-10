import csv
from pathlib import Path

CSV_PATH = Path("data/all_pubs.csv")
OUTPUT_PATH = Path("data/pubs_latex.txt")
SELECTED_OUTPUT_PATH = Path("data/selected_pubs_latex.txt")

LATEX_ESCAPE = str.maketrans(
    {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
)


def escape_tex(text: str) -> str:
    return text.translate(LATEX_ESCAPE)


def venue_tag(abbreviate: str, year: str) -> str:
    tag = abbreviate.strip() if abbreviate else ""
    return f"{tag} {year}".strip()


def format_links(row: dict) -> str:
    links = []
    for label, field in (("paper", "Paper"), ("code", "Code"), ("page", "Page")):
        url = row.get(field, "").strip()
        if url:
            links.append(rf"\href{{{url}}}{{{label}}}")
    return r"\,[" + ", ".join(links) + "] \\" if links else r"\\"


def format_item(row: dict) -> str:
    authors = escape_tex(row.get("", "").strip('" '))
    authors = authors.replace("Minh Tran", r"\underline{Minh Tran}")
    title = escape_tex(row.get("Title", ""))
    publication = escape_tex(row.get("Publication", ""))
    abbreviate = escape_tex(row.get("Abbreviate", ""))
    year = row.get("Year", "").strip()
    venue = venue_tag(abbreviate, year)
    links = format_links(row)
    details_parts = [p for p in [publication, year] if p]
    details = ", ".join(details_parts)
    return "\n".join(
        [
            rf"\item[\textbf{{{venue}}}]",
            rf"\textbf{{{title}}}",
            links+"\\",
            rf"{{\it {authors}}} \\",
            rf"{{\small \textit{{{details}}}}}",
            "",
        ]
    )


def main() -> None:
    header_all = "\n".join(
        [
            r"\vspace{0.2cm}",
            r"\section{\textbf{Publications}}",
            "",
        ]
    )
    header_selected = "\n".join(
        [
            r"\vspace{0.2cm}",
            r"\section{\textbf{Selected Publications} \hfill \textcolor{darkblue} {\scriptsize \href{https://scholar.google.com/citations?user=AmQwXDUAAAAJ}{Full List}}}",
            "",
        ]
    )

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    def group_by_type(row_list):
        grouped = {
            "Conference": [],
            "Journal": [],
            "Other": [],
        }
        for row in row_list:
            type_val = row.get("Type", "").strip().lower()
            if "conf" in type_val:
                grouped["Conference"].append(row)
            elif "journal" in type_val:
                grouped["Journal"].append(row)
            else:
                grouped["Other"].append(row)
        return grouped

    groups = group_by_type(rows)
    selected_groups = group_by_type(
        [row for row in rows if row.get("Selected", "").strip().lower() == "yes"]
    )

    options = r"\begin{enumerate}[leftmargin=*, labelsep=0.5em, align=left, widest={\textbf{NeurIPS 2024}}, itemindent=0em, label={\textbf{[\arabic*]}}]"

    def render(group_map, header):
        rendered = [header]
        count = 0
        for section in ("Conference", "Journal", "Other"):
            entries = group_map[section]
            if not entries:
                continue
            nice_title = rf"\noindent{{\large\textit{{{section}s}}}}"
            rendered.append(nice_title)
            # rendered.append(r"\vspace{0.15cm}")
            # rendered.append(r"\rule{\linewidth}{0.2pt}")
            # rendered.append(r"\vspace{0.15cm}")
            rendered.append(options)
            for row in entries:
                rendered.append(format_item(row))
                count += 1
            rendered.append(r"\end{enumerate}")
            rendered.append("")
        return "\n".join(rendered), count

    all_text, all_count = render(groups, header_all)
    OUTPUT_PATH.write_text(all_text, encoding="utf-8")
    selected_text, selected_count = render(selected_groups, header_selected)
    SELECTED_OUTPUT_PATH.write_text(selected_text, encoding="utf-8")

    print(f"Wrote {all_count} entries to {OUTPUT_PATH}")
    print(f"Wrote {selected_count} entries to {SELECTED_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
