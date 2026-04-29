# APT TTP Mapper

A Python tool that extracts and maps adversary tactics, techniques, and procedures (TTPs) from threat intelligence reports to the [MITRE ATT&CK Enterprise and ICS frameworks](https://attack.mitre.org/).

Built as a practical complement to threat intelligence analysis — automating the TTP extraction process that analysts typically perform manually when reviewing adversary campaign reports.

---

## What It Does

- Accepts a threat report as input (PDF, scanned PDF, or plain text)
- Downloads and merges the ATT&CK Enterprise and ICS datasets on first run
- Runs a two-pass extraction engine:
  - **Pass 1** — scans for explicit ATT&CK Technique IDs (T1xxx and T0xxx) → High confidence
  - **Pass 2** — scans prose for technique name keywords → Medium confidence
- Labels every match by source dataset (Enterprise or ICS)
- Outputs a structured CSV, Excel report, and tactic frequency bar chart

---

## v1.0 vs. v1.1 — Before/After on CISA AA26-097A

| | v1.0 | v1.1 |
|---|---|---|
| Explicit T-IDs found | 2 / 4 | 4 / 4 |
| ICS techniques (T0xxx) | 0 | 2 |
| Total unique TTPs | 9 | 12 |
| Scanned PDF support | No | Yes (OCR) |
| Tactic frequency chart | No | Yes |
| Codebase structure | Single script | Multi-module package |

---

## Project Structure

```
apt-ttp-mapper/
├── main.py                  # Entry point
├── mapper/
│   ├── __init__.py
│   ├── downloader.py        # Downloads Enterprise + ICS ATT&CK datasets
│   ├── lookup.py            # Builds combined technique lookup dictionary
│   ├── extractor.py         # Text extraction (PDF, scanned PDF via OCR, txt)
│   ├── engine.py            # Two-pass TTP matching engine
│   └── reporter.py          # CSV, Excel, and tactic frequency chart output
├── requirements.txt
├── README.md
├── sample_reports/          # Drop input reports here
└── output/                  # Results land here
```

---

## Installation

**Requirements:** Python 3.9+

```bash
git clone https://github.com/shankar-bettadapura/apt-ttp-mapper.git
cd apt-ttp-mapper

python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**Tesseract OCR** is required for scanned PDF support. Download and install from:
https://github.com/UB-Mannheim/tesseract/wiki

After installing, update the Tesseract path in `mapper/extractor.py` if your installation path differs from the default:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## Usage

```bash
python main.py <path_to_report.pdf or .txt>
```

**Examples:**

```bash
# PDF input
python main.py sample_reports/cisa_advisory_aa26-097a.pdf

# Plain text input
python main.py sample_reports/report.txt
```

On first run, the tool automatically downloads the ATT&CK Enterprise and ICS datasets (~20MB combined) and caches them locally. Subsequent runs use the cached files.

**Output files** are saved to the `/output` directory with timestamped filenames:
```
output/
├── cisa_advisory_aa26-097a_ttp_map_20260427_1501.csv
├── cisa_advisory_aa26-097a_ttp_map_20260427_1501.xlsx
└── cisa_advisory_aa26-097a_tactic_chart_20260427_1501.png
```

---

## Sample Output

| ID | Technique | Tactic | Source | Confidence | Match Type |
|----|-----------|--------|--------|------------|------------|
| T0883 | Internet Accessible Device | Initial Access | ICS | High | Explicit T-ID |
| T0885 | Commonly Used Port | Command And Control | ICS | High | Explicit T-ID |
| T1219 | Remote Access Tools | Command And Control | Enterprise | High | Explicit T-ID |
| T1565 | Data Manipulation | Impact | Enterprise | High | Explicit T-ID |
| T0889 | Modify Program | Persistence | ICS | Medium | Keyword Match |
| T1566 | Phishing | Initial Access | Enterprise | Medium | Keyword Match |

---

## Dependencies

| Library | Purpose |
|---------|---------|
| requests | Downloads ATT&CK datasets |
| pandas | Structures results, exports CSV/Excel |
| pdfplumber | Extracts text from PDF files |
| pytesseract | OCR for scanned PDFs |
| pdf2image | Converts scanned PDF pages to images for OCR |
| Pillow | Image processing backend |
| matplotlib | Tactic frequency bar chart |
| openpyxl | Excel file generation backend |

---

## Tested Against

- CISA Advisory AA26-097A — Iranian-Affiliated Cyber Actors Exploit PLCs Across US Critical Infrastructure (April 2026)

---

## Limitations

- **Keyword false positives** — Medium confidence matches reflect language alignment, not confirmed technique use. All keyword matches should be reviewed by an analyst before use in a formal product.
- **Inference is a human function** — the tool maps what is explicitly described, not what is analytically implied from described behavior.
- **ATT&CK version drift** — the cached datasets reflect the version available at download time. Delete `enterprise-attack.json` and `ics-attack.json` to force a refresh when MITRE releases a new version.
- **Scanned PDF accuracy** — OCR accuracy depends on scan quality. Low-resolution or rotated scans may produce degraded text extraction.

---

## Roadmap

- v1.2: NLP-based semantic matching to surface implied techniques beyond keyword hits
- v1.2: ATT&CK version check at startup with automatic refresh prompt
- v1.3: HTML report output via Jinja2 templates
- v1.3: Batch mode for processing multiple reports and comparing TTP overlap across campaigns

---

## Background

Built as a practical extension of threat intelligence work covering Iranian APT operations against U.S. critical infrastructure. Tested against CISA Advisory AA26-097A — [Iranian-Affiliated Cyber Actors Exploit Programmable Logic Controllers Across US Critical Infrastructure](https://www.cisa.gov/news-events/cybersecurity-advisories/aa26-097a).

Full writeup covering the v1.0 findings and the v1.1 improvements is available on [Substack](https://shankarbettadapura.substack.com).

---

## Author

**Shankar Bettadapura**
Cybersecurity & GRC | Threat Intelligence | AI Risk & Governance

[LinkedIn](https://www.linkedin.com/in/shankar-bettadapura) · [Substack](https://shankarbettadapura.substack.com) · [GitHub](https://github.com/shankar-bettadapura)
