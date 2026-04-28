# main.py

import sys
import os
from mapper.downloader import download_all
from mapper.lookup import build_combined_lookup
from mapper.extractor import extract_text_from_file
from mapper.engine import extract_ttps
from mapper.reporter import generate_report


def main():
    """
    Entry point for APT TTP Mapper v1.1.

    Usage: python main.py <path_to_report.pdf or .txt>
    Example: python main.py sample_reports/cisa_advisory_aa26-097a.pdf

    Each import pulls from the mapper package — one module per responsibility.
    main() itself contains no logic beyond orchestration: it calls each module
    in sequence and passes results from one to the next.
    """
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_report.pdf or .txt>")
        print("Example: python main.py sample_reports/cisa_advisory_aa26-097a.pdf")
        sys.exit(1)

    report_path = sys.argv[1]

    if not os.path.exists(report_path):
        print(f"[-] File not found: {report_path}")
        sys.exit(1)

    print(f"\n[*] APT TTP Mapper v1.1 — Starting analysis")
    print(f"[*] Input: {report_path}\n")

    # Step 1: Download datasets
    download_all()

    # Step 2: Build combined Enterprise + ICS lookup
    technique_lookup = build_combined_lookup()

    # Step 3: Extract text (handles text-layer and scanned PDFs)
    print(f"\n[*] Extracting text from report...")
    report_text = extract_text_from_file(report_path)
    print(f"[+] Extracted {len(report_text):,} characters.")

    # Step 4: Run TTP matching engine
    print(f"\n[*] Running TTP extraction...")
    matched_ttps = extract_ttps(report_text, technique_lookup)

    # Step 5: Generate CSV, Excel, and chart
    print(f"\n[*] Generating report...")
    generate_report(matched_ttps, source_filename=report_path)


if __name__ == "__main__":
    main()