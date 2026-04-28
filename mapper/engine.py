# mapper/engine.py

import re


def extract_ttps(report_text, technique_lookup):
    """
    Two-pass TTP extraction engine. Logic is identical to v1.0 with one
    addition: each matched entry now carries a source field ("Enterprise"
    or "ICS") inherited from the lookup entry, so the output report can
    show which ATT&CK dataset each match came from.

    Pass 1 — Explicit T-IDs (High confidence):
        Regex scans for T1xxx and T0xxx IDs.
        The pattern is updated to catch both four-digit namespaces.

    Pass 2 — Keyword matches (Medium confidence):
        Scans prose against all keywords in the combined lookup.
        Five-character floor applied. High confidence hits are not
        overwritten by keyword matches on the same technique.
    """
    report_lower = report_text.lower()
    matched_ttps = {}

    # -------------------------------------------------------------------------
    # Pass 1: Explicit T-IDs
    # Updated pattern captures both T0xxx (ICS) and T1xxx (Enterprise).
    # The original pattern was anchored to T1 implicitly — now it matches
    # any T followed by 4 digits, which covers both namespaces.
    # -------------------------------------------------------------------------
    tid_pattern = re.compile(r'\bT\d{4}(?:\.\d{3})?\b')
    explicit_ids = set(tid_pattern.findall(report_text))

    id_to_entry = {v["id"]: v for v in technique_lookup.values()}

    for tid in explicit_ids:
        if tid in id_to_entry:
            entry = id_to_entry[tid].copy()
            entry["match_type"] = "Explicit T-ID"
            entry["confidence"] = "High"
            matched_ttps[tid] = entry

    # -------------------------------------------------------------------------
    # Pass 2: Keyword scan
    # -------------------------------------------------------------------------
    for keyword, entry in technique_lookup.items():
        if len(keyword) < 5:
            continue

        if keyword in report_lower:
            tid = entry["id"]
            if tid not in matched_ttps:
                entry_copy = entry.copy()
                entry_copy["match_type"] = "Keyword Match"
                entry_copy["confidence"] = "Medium"
                matched_ttps[tid] = entry_copy

    results = list(matched_ttps.values())

    enterprise_hits = sum(1 for r in results if r.get("source") == "Enterprise")
    ics_hits = sum(1 for r in results if r.get("source") == "ICS")

    print(f"[+] Identified {len(results)} unique TTPs ({enterprise_hits} Enterprise, {ics_hits} ICS).")
    return results