#!/usr/bin/env python3
"""Generate the modular LaTeX CV from the website's structured CV data.

The authoritative non-publication data lives in assets/json/resume.json.
Publication and presentation metadata remain in the two Jekyll-Scholar BibTeX
files. The generated TeX is committed so the CV remains easy to inspect and
compile even without running this script first.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RESUME_PATH = REPO_ROOT / "assets" / "json" / "resume.json"
PAPERS_PATH = REPO_ROOT / "_bibliography" / "papers.bib"
TALKS_PATH = REPO_ROOT / "_bibliography" / "talks.bib"
OUTPUT_PATH = REPO_ROOT / "cv" / "latex" / "generated" / "content.tex"


def latex_escape(value: Any) -> str:
    """Escape plain text for LaTeX while keeping UTF-8 names readable."""

    text = "" if value is None else str(value)
    text = (
        text.replace("\u2011", "-")
        .replace("\u2013", "--")
        .replace("\u2014", "--")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", "``")
        .replace("\u201d", "''")
    )
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def latex_url(value: str) -> str:
    """Escape URL characters that retain special meaning in macro arguments."""

    return (
        value.replace("%", r"\%")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("&", r"\&")
    )


def linked(label: str, url: str | None) -> str:
    escaped_label = latex_escape(label)
    if not url:
        return escaped_label
    return rf"\href{{{latex_url(url)}}}{{{escaped_label}}}"


def year_range(start_date: str, end_date: str, *, current: bool = True) -> str:
    start = (start_date or "")[:4]
    end = (end_date or "")[:4]
    if not end:
        return f"{start}--present" if current else start
    if start == end:
        return start
    return f"{start}--{end}"


def strip_bib_value(value: str) -> str:
    value = value.strip()
    while len(value) >= 2 and (
        (value[0] == "{" and value[-1] == "}")
        or (value[0] == '"' and value[-1] == '"')
    ):
        value = value[1:-1].strip()
    return value.replace("{", "").replace("}", "")


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    """Parse the simple, repository-owned BibTeX files without a dependency."""

    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        text = re.sub(r"\A---\s*\n---\s*\n", "", text, count=1)

    entries: dict[str, dict[str, str]] = {}
    entry_start = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
    cursor = 0
    while match := entry_start.search(text, cursor):
        entry_type, key = match.group(1).lower(), match.group(2)
        open_brace = text.find("{", match.start())
        depth = 0
        close_brace = -1
        for index in range(open_brace, len(text)):
            if text[index] == "{":
                depth += 1
            elif text[index] == "}":
                depth -= 1
                if depth == 0:
                    close_brace = index
                    break
        if close_brace < 0:
            raise ValueError(f"Unclosed BibTeX entry {key} in {path}")

        body = text[match.end() : close_brace]
        fields: dict[str, str] = {"ENTRYTYPE": entry_type, "ID": key}
        position = 0
        while position < len(body):
            field_match = re.search(r"([A-Za-z][\w-]*)\s*=\s*", body[position:])
            if not field_match:
                break
            name = field_match.group(1).lower()
            value_start = position + field_match.end()
            if value_start >= len(body):
                break

            delimiter = body[value_start]
            if delimiter == "{":
                depth = 0
                value_end = value_start
                for value_end in range(value_start, len(body)):
                    if body[value_end] == "{":
                        depth += 1
                    elif body[value_end] == "}":
                        depth -= 1
                        if depth == 0:
                            value_end += 1
                            break
            elif delimiter == '"':
                value_end = value_start + 1
                while value_end < len(body):
                    if body[value_end] == '"' and body[value_end - 1] != "\\":
                        value_end += 1
                        break
                    value_end += 1
            else:
                comma = body.find(",", value_start)
                value_end = len(body) if comma < 0 else comma

            fields[name] = strip_bib_value(body[value_start:value_end])
            position = value_end + 1

        entries[key] = fields
        cursor = close_brace + 1

    return entries


def author_name(raw_name: str) -> str:
    name = raw_name.strip()
    if "," in name:
        last, first = (part.strip() for part in name.split(",", maxsplit=1))
        name = f"{first} {last}"
    escaped = latex_escape(name)
    if name.casefold() == "bernardin tamo amougou".casefold():
        return rf"\textbf{{{escaped}}}"
    return escaped


def author_list(raw_authors: str) -> str:
    authors = [author_name(name) for name in raw_authors.split(" and ") if name.strip()]
    if len(authors) <= 1:
        return "".join(authors)
    if len(authors) == 2:
        return f"{authors[0]} and {authors[1]}"
    return f"{', '.join(authors[:-1])}, and {authors[-1]}"


def compact_items(items: list[str]) -> str:
    if not items:
        return ""
    lines = [r"\begin{CVItems}"]
    lines.extend(rf"  \item {latex_escape(item)}" for item in items)
    lines.append(r"\end{CVItems}")
    return "\n".join(lines)


def entry(
    date: str,
    title: str,
    meta: str,
    summary: str = "",
    highlights: list[str] | None = None,
    url: str | None = None,
) -> str:
    body_parts = []
    if summary:
        body_parts.append(latex_escape(summary))
    if highlights:
        body_parts.append(compact_items(highlights))
    body = "\n\n".join(body_parts)
    return rf"""
\needspace{{5\baselineskip}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}>{{\raggedright\arraybackslash}}p{{0.145\linewidth}}@{{\hspace{{0.018\linewidth}}}}X@{{}}}}
  \CVDate{{{latex_escape(date)}}} & \textbf{{{linked(title, url)}}} \\
  & \CVMeta{{{latex_escape(meta)}}} \\
  & \begin{{minipage}}[t]{{\linewidth}}{body}\end{{minipage}}
\end{{tabularx}}
\vspace{{0.28em}}
""".strip()


def compact_entry(
    date: str,
    title: str,
    meta: str,
    detail: str = "",
    url: str | None = None,
) -> str:
    """Render a concise two- or three-line entry for space-efficient sections."""

    detail_row = (rf"  & {latex_escape(detail)} \\" + "\n") if detail else ""
    return rf"""
\needspace{{3\baselineskip}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}>{{\raggedright\arraybackslash}}p{{0.145\linewidth}}@{{\hspace{{0.018\linewidth}}}}X@{{}}}}
  \CVDate{{{latex_escape(date)}}} & \textbf{{{linked(title, url)}}} \\
  & \CVMeta{{{latex_escape(meta)}}} \\
{detail_row}\end{{tabularx}}
\vspace{{0.22em}}
""".strip()


def skill_table(skills: list[dict[str, Any]]) -> str:
    rows = []
    for item in skills:
        name = latex_escape(item["name"])
        level = latex_escape(item["level"])
        keywords = latex_escape(" - ".join(item["keywords"]))
        rows.append(
            rf"\textbf{{{name}}} {{\scriptsize\color{{Muted}}({level})}} & {keywords} \\[0.24em]"
        )
    return "\n".join(
        [
            r"\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{0.29\linewidth}@{\hspace{0.02\linewidth}}X@{}}",
            *rows,
            r"\end{tabularx}",
        ]
    )


def publication_entry(record: dict[str, str]) -> str:
    authors = author_list(record.get("author", ""))
    title = latex_escape(record.get("title", ""))
    venue = latex_escape(record.get("booktitle", ""))
    year = latex_escape(record.get("year", ""))
    pages = latex_escape(record.get("pages", ""))
    doi = record.get("doi", "")
    arxiv = record.get("arxiv", "")
    links = []
    if doi:
        links.append(rf"\href{{{latex_url('https://doi.org/' + doi)}}}{{DOI}}")
    if arxiv:
        links.append(rf"\href{{{latex_url('https://arxiv.org/abs/' + arxiv)}}}{{arXiv}}")
    link_text = r" \textbar{} ".join(links)
    pages_text = rf", pp. {pages}" if pages else ""
    return rf"""
\needspace{{4\baselineskip}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}>{{\raggedright\arraybackslash}}p{{0.145\linewidth}}@{{\hspace{{0.018\linewidth}}}}X@{{}}}}
  \CVDate{{{year}}} & \textbf{{{title}}} \\
  & {authors}. \emph{{{venue}}}{pages_text}. {link_text}
\end{{tabularx}}
\vspace{{0.38em}}
""".strip()


def presentation_entry(record: dict[str, str]) -> str:
    date_bits = [record.get("month", "").strip(), record.get("year", "").strip()]
    date = " ".join(bit for bit in date_bits if bit)
    title = record.get("title", "")
    venue = record.get("booktitle", "")
    note = record.get("note", "")
    meta = " - ".join(part for part in (note, venue) if part)
    return compact_entry(date, title, meta, url=record.get("html", ""))


def section(title: str) -> str:
    return rf"\CVSection{{{latex_escape(title)}}}"


def profile_link(profile: dict[str, str]) -> str:
    return linked(profile["network"], profile["url"])


def build_content(resume: dict[str, Any]) -> str:
    papers = parse_bibtex(PAPERS_PATH)
    talks = parse_bibtex(TALKS_PATH)
    basics = resume["basics"]
    meta = resume["meta"]
    output: list[str] = [
        "% AUTO-GENERATED by cv/scripts/generate_cv.py. Do not edit by hand.",
        r"\begin{center}",
        rf"{{\fontsize{{23}}{{26}}\selectfont\bfseries {latex_escape(basics['name'])}}}",
        r"\par\vspace{0.35em}",
        rf"{{\large\color{{Accent}}\bfseries {latex_escape(basics['label'])}}}",
        r"\par\vspace{0.65em}",
    ]

    contact = [
        latex_escape(basics["location"]["city"]),
        linked(basics["email"], f"mailto:{basics['email']}"),
        linked("Website", basics["url"]),
    ]
    contact.extend(profile_link(profile) for profile in basics["profiles"])
    output.extend(
        [
            rf"{{\small {' \\textbullet{} '.join(contact)}}}",
            r"\end{center}",
            r"\vspace{0.35em}",
            section("Research profile"),
            latex_escape(basics["summary"]),
            r"\par\vspace{0.35em}",
        ]
    )

    research_areas = resume["interests"][0]["keywords"]
    output.append(r"\textbf{Core areas:} " + r" \textbullet{} ".join(latex_escape(item) for item in research_areas))

    output.append(section("Education"))
    for item in resume["education"]:
        meta_parts = [item["area"], item["institution"], item["location"]]
        detail_parts = []
        if item.get("score"):
            detail_parts.append(item["score"])
        if item.get("summary"):
            detail_parts.append(item["summary"])
        if item["studyType"] == "Dual PhD candidate" and item.get("courses"):
            detail_parts.append(item["courses"][0])
        output.append(
            compact_entry(
                year_range(item["startDate"], item["endDate"]),
                item["studyType"],
                " - ".join(part for part in meta_parts if part),
                "; ".join(part.rstrip(".") for part in detail_parts) + ("." if detail_parts else ""),
                item.get("url", ""),
            )
        )

    output.append(section("Research and professional experience"))
    for item in resume["work"]:
        output.append(
            entry(
                year_range(item["startDate"], item["endDate"]),
                item["position"],
                f"{item['name']} - {item['location']}",
                item.get("summary", ""),
                item.get("highlights", [])[:3],
                item.get("url", ""),
            )
        )

    output.append(section("Peer-reviewed publications"))
    for key in meta["selectedPublicationKeys"]:
        if key not in papers:
            raise KeyError(f"Publication key {key!r} is missing from {PAPERS_PATH}")
        output.append(publication_entry(papers[key]))

    output.append(section("Current and selected research projects"))
    for item in resume["projects"]:
        output.append(
            compact_entry(
                item["status"],
                item["name"],
                item["summary"],
                item.get("highlights", [""])[0],
                item.get("url", ""),
            )
        )

    output.append(section("Teaching and supervision"))
    for item in resume["teaching"]:
        output.append(
            compact_entry(
                year_range(item["startDate"], item["endDate"]),
                item["position"],
                f"{item['institution']} - {item['location']}",
                " ".join(item.get("highlights", [])[:2]),
                item.get("url", ""),
            )
        )

    output.append(section("Selected talks, posters and presentations"))
    for key in meta["selectedPresentationKeys"]:
        if key not in talks:
            raise KeyError(f"Presentation key {key!r} is missing from {TALKS_PATH}")
        output.append(presentation_entry(talks[key]))

    output.append(section("Awards, scholarships and distinctions"))
    pdf_award_titles = set(meta["pdfAwardTitles"])
    for item in (award for award in resume["awards"] if award["title"] in pdf_award_titles):
        output.append(
            compact_entry(
                item["date"],
                item["title"],
                " - ".join(part for part in (item["awarder"], item.get("summary", "")) if part),
                url=item.get("url", ""),
            )
        )

    output.append(section("Scientific service and leadership"))
    for item in resume["volunteer"]:
        output.append(
            compact_entry(
                year_range(item["startDate"], item["endDate"]),
                item["position"],
                item["organization"],
                item.get("summary", ""),
                item.get("url", ""),
            )
        )

    output.append(section("Technical and mathematical skills"))
    output.append(skill_table(resume["skills"]))

    output.append(section("Advanced training and languages"))
    pdf_training_names = set(meta["pdfTrainingNames"])
    for item in (training for training in resume["training"] if training["name"] in pdf_training_names):
        output.append(
            compact_entry(
                item["date"],
                item["name"],
                f"{item['provider']} - {item['location']}",
                url=item.get("url", ""),
            )
        )
    language_text = r" \textbullet{} ".join(
        rf"\textbf{{{latex_escape(item['language'])}}}: {latex_escape(item['fluency'])}" for item in resume["languages"]
    )
    output.extend([r"\vspace{0.2em}", language_text, r"\par\vspace{0.4em}", r"\CVReferencesNote"])

    return "\n\n".join(output).strip() + "\n"


def main() -> None:
    resume = json.loads(RESUME_PATH.read_text(encoding="utf-8"))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_content(resume), encoding="utf-8")
    print(f"Generated {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
