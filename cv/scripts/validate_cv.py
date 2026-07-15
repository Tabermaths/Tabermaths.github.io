#!/usr/bin/env python3
"""Run deterministic consistency checks for the structured and PDF CV."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
RESUME_PATH = REPO_ROOT / "assets" / "json" / "resume.json"
PAPERS_PATH = REPO_ROOT / "_bibliography" / "papers.bib"
TALKS_PATH = REPO_ROOT / "_bibliography" / "talks.bib"
PDF_PATH = REPO_ROOT / "assets" / "pdf" / "Bernardin_Tamo_Amougou_CV.pdf"
LOG_PATH = REPO_ROOT / "cv" / "latex" / "build" / "main.log"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout


def year(value: str) -> int:
    match = re.fullmatch(r"(\d{4})(?:-(\d{2}))?", value)
    require(match is not None, f"Invalid ISO-like date: {value!r}")
    if match.group(2):
        require(1 <= int(match.group(2)) <= 12, f"Invalid month in date: {value!r}")
    return int(match.group(1))


def check_reverse_chronology(items: list[dict[str, Any]], field: str, label: str) -> None:
    years = [year(str(item[field])) for item in items]
    require(years == sorted(years, reverse=True), f"{label} is not reverse chronological: {years}")


def bib_keys(path: Path) -> set[str]:
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", path.read_text(encoding="utf-8")))


def main() -> None:
    resume = json.loads(RESUME_PATH.read_text(encoding="utf-8"))
    basics = resume["basics"]
    meta = resume["meta"]

    require(basics["name"] == "Bernardin TAMO AMOUGOU", "Professional name is inconsistent")
    require(not basics.get("phone"), "A private phone number must not appear in the public source")
    require(not basics["location"].get("address"), "A street address must not appear in the public source")
    require(not basics["location"].get("postalCode"), "A postcode must not appear in the public source")
    require("[VERIFY" not in RESUME_PATH.read_text(encoding="utf-8"), "Verification placeholders must stay out of public data")

    profiles = basics["profiles"]
    require(len({item["network"] for item in profiles}) == len(profiles), "Duplicate profile network")
    require(len({item["url"] for item in profiles}) == len(profiles), "Duplicate profile URL")
    require(all(item["url"].startswith("https://") for item in profiles), "Profile links must use HTTPS")

    for section, field in (("education", "startDate"), ("work", "startDate"), ("teaching", "startDate"), ("awards", "date"), ("training", "date")):
        check_reverse_chronology(resume[section], field, section)

    for section in ("education", "work", "teaching"):
        for item in resume[section]:
            start = year(item["startDate"])
            if item.get("endDate"):
                require(start <= year(item["endDate"]), f"End date precedes start date in {section}: {item}")

    require(set(meta["selectedPublicationKeys"]) <= bib_keys(PAPERS_PATH), "Selected publication key is missing")
    require(set(meta["selectedPresentationKeys"]) <= bib_keys(TALKS_PATH), "Selected presentation key is missing")
    require(set(meta["pdfAwardTitles"]) <= {item["title"] for item in resume["awards"]}, "Selected PDF award is missing")
    require(set(meta["pdfTrainingNames"]) <= {item["name"] for item in resume["training"]}, "Selected PDF training is missing")

    require(PDF_PATH.is_file(), "Compiled PDF is missing")
    pdf_info = command("pdfinfo", str(PDF_PATH))
    require(re.search(r"^Pages:\s+4$", pdf_info, re.MULTILINE) is not None, "PDF must be four pages")
    require("A4" in pdf_info, "PDF must use A4 pages")

    extracted = command("pdftotext", "-layout", str(PDF_PATH), "-")
    for expected in (basics["name"], "Research profile", "Peer-reviewed publications", "Technical and mathematical skills"):
        require(expected in extracted, f"Extracted PDF text is missing {expected!r}")

    embedded_urls = command("pdfinfo", "-url", str(PDF_PATH))
    for expected in (
        f"mailto:{basics['email']}",
        "https://doi.org/10.1109/SSP64130.2025.11073283",
        "https://doi.org/10.1007/978-3-031-92366-1_9",
        "https://arxiv.org/abs/2502.19194",
        "https://arxiv.org/abs/2502.05127",
    ):
        require(expected in embedded_urls, f"PDF hyperlink is missing {expected}")

    log_text = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    warning_pattern = r"Overfull|Underfull|LaTeX Warning|Package .* Warning"
    require(re.search(warning_pattern, log_text) is None, "LaTeX emitted a layout-affecting warning")

    print("CV validation passed: structured data, chronology, privacy, bibliography keys, four-page PDF, text and hyperlinks")


if __name__ == "__main__":
    main()
