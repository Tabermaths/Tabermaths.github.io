# Bernardin TAMO AMOUGOU: master CV

This directory contains the maintainable source and audit trail for the public master CV. The website and PDF share structured factual data instead of maintaining two independent prose documents.

## Source audit

### Strongest sources

- `Bernardin_Up_to_date_(short)/main.tex` and `Bernardin_TAMO_AMOUGOU_CV/main.tex` supplied the clearest baseline for education, core roles, teaching, awards and skills.
- The more recent company-specific CV variants helped corroborate current methods, software and research-engineering language. Their vacancy-specific positioning and impact claims were not carried over automatically.
- The website repository supplied the current biography, research direction, teaching record, news, profile links, bibliography and talk records.
- Publisher records were treated as authoritative for the two peer-reviewed papers: IEEE SSP 2025, DOI `10.1109/SSP64130.2025.11073283`, and SSVM 2025, DOI `10.1007/978-3-031-92366-1_9`.
- The AIMS Cameroon valedictorian announcement and current institutional/event pages were used to corroborate the corresponding distinction and selected presentations.
- The shared CVs and Eloi Tanguy CV were used only as design references. Biographical content belonging to other people was excluded.

### Reconciliation and editorial decisions

- Replaced the Einstein demonstration content in `assets/json/resume.json` with Bernardin's reconciled record.
- Consolidated repeated Neuromatch and university teaching entries into three chronological teaching records.
- Removed private phone numbers, street addresses, referee details, nationality, date of birth and photographs from the public CV.
- Removed generic “data scientist enthusiast” wording, long degree-module inventories, old classroom projects and vacancy-specific objective statements.
- Excluded unsupported percentage improvements, audience-size claims, pass-rate claims and other numerical impact statements found only in tailored variants.
- Excluded Project Sueza impact claims and an unverified under-review paper until an authoritative record is available.
- Kept the dual PhD open-ended as `2023-present` because supplied sources disagree on the expected completion year.
- Kept publication metadata in BibTeX and linked the website/PDF to DOI and arXiv records rather than duplicating hand-written citations.
- Labelled the equivariant VAE work as current research; no publication status is claimed.
- The website presents the complete reconciled record. The four-page PDF selects four presentations, six principal awards and two advanced training schools to remain readable.

## Source-of-truth architecture

| Content                                                                           | Authoritative file                     | Consumers                                   |
| --------------------------------------------------------------------------------- | -------------------------------------- | ------------------------------------------- |
| Profile, education, roles, projects, teaching, awards, service, skills, languages | `assets/json/resume.json`              | `/cv/` and PDF generator                    |
| Peer-reviewed publications                                                        | `_bibliography/papers.bib`             | Publications page, `/cv/` and PDF generator |
| Talks and posters                                                                 | `_bibliography/talks.bib`              | Talks page, `/cv/` and PDF generator        |
| Web presentation                                                                  | `_layouts/cv.liquid`, `_sass/_cv.scss` | Responsive `/cv/` page                      |
| PDF presentation                                                                  | `cv/latex/`                            | Downloadable A4 PDF                         |

The PDF generator is `cv/scripts/generate_cv.py`. It reads the JSON and BibTeX records, writes `cv/latex/generated/content.tex`, and leaves the generated source committed for inspection.

## Content and design rationale

The headline positions Bernardin as a mathematically grounded researcher whose work joins machine learning, Bayesian imaging and uncertainty quantification. The sequence gives recent research, peer-reviewed outputs and implementational evidence priority while preserving teaching, mathematical education and awards for academic readers.

The website uses the al-folio theme's existing colour variables and typography. The PDF uses the site's light-mode accent (`#00369F`) with restrained rules, one-column reading order, selectable text and no decorative rating systems. A compact date/content grid supports scanning without creating an ATS-hostile sidebar.

## Build

From the repository root:

```sh
make -C cv all
```

This regenerates the modular TeX source, compiles the PDF with `latexmk`, copies it to `assets/pdf/Bernardin_Tamo_Amougou_CV.pdf`, and checks that text extraction succeeds.

## Facts requiring manual verification

- `[VERIFY DATE]` Expected dual-PhD completion: sources variously imply 2026 and 2027. The public CV therefore says `2023-present`.
- `[VERIFY ROLE TITLE]` Confirm whether the current Heriot-Watt teaching appointment should publicly be called ATER, teacher, tutor, teaching assistant, or a combination.
- `[VERIFY ROLE TITLE AND DATES]` Confirm the formal MAP5 title and precise start/end months; public material is not fully consistent.
- `[VERIFY DATE]` Confirm precise months for the Hausdorff Center internship and Neuromatch appointments if month-level dates are desired.
- `[VERIFY PUBLICATION STATUS]` Confirm whether the equivariant self-supervised VAE has a citable preprint or formal manuscript status. It is currently labelled only as current research.
- `[VERIFY AWARD WORDING]` Confirm the official title and year of the AIMS Cameroon “Gender Balance Prize, Three Minute Thesis”.
- `[VERIFY QUALIFICATION NAMES]` Confirm the exact official award names for the CETIC and ENS Yaoundé qualifications; cautious descriptive wording is used meanwhile.
- `[VERIFY LANGUAGE LEVEL]` Confirm whether `English: Fluent (C1)` and `German: Basic` should remain public.
- `[VERIFY CONTACT]` Confirm that `bt2027@hw.ac.uk` is the preferred long-term public email address.
- `[ADD DOI OR ARXIV LINK]` Add an archival link for any future preprint before changing its status on the public CV.

## Validation record

| Check                     | Result                                                                           |
| ------------------------- | -------------------------------------------------------------------------------- |
| Structured JSON parses    | Passed locally                                                                   |
| Prettier repository check | Passed locally                                                                   |
| LaTeX compilation         | Passed locally with `latexmk`                                                    |
| PDF length and size       | Four A4 pages; 10 pt base type                                                   |
| PDF visual inspection     | All four rendered pages inspected at high resolution                             |
| PDF text extraction       | Passed with Poppler; reading order retained                                      |
| PDF hyperlinks            | DOI, arXiv, contact and professional links embedded                              |
| LaTeX layout warnings     | No overfull/underfull boxes or visible warning conditions                        |
| Greyscale legibility      | Accent retains sufficient tonal contrast; all content remains text-labelled      |
| Responsive structure      | Single-column mobile rules and horizontal overflow protections present           |
| Light/dark mode           | Uses the theme's existing colour variables; no hard-coded web background colours |
| Jekyll production build   | Passed in GitHub Actions; the local workspace has no Ruby/Jekyll runtime         |
| Repository source links   | Passed in GitHub Actions                                                         |

## Files created or modified

- `_pages/cv.md`
- `_layouts/cv.liquid`
- `_sass/_cv.scss`
- `_config.yml`
- `assets/json/resume.json`
- `_bibliography/papers.bib`
- `_bibliography/talks.bib`
- `assets/pdf/Bernardin_Tamo_Amougou_CV.pdf`
- `cv/.gitignore`
- `cv/README.md`
- `cv/Makefile`
- `cv/scripts/generate_cv.py`
- `cv/scripts/validate_cv.py`
- `cv/latex/main.tex`
- `cv/latex/preamble.tex`
- `cv/latex/generated/content.tex`
