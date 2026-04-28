# mapper/lookup.py

import json


def _parse_dataset(local_file, source_label):
    """
    Parses a single ATT&CK STIX JSON file and returns a lookup dictionary.

    source_label is either "Enterprise" or "ICS" and is stored on every
    entry so the output report can show which dataset each match came from.

    The parsing logic is identical to v1.0 — filter for attack-pattern type,
    skip revoked/deprecated entries, extract the technique ID, tactics, and
    description — with source_label added as a new field.
    """
    with open(local_file, "r") as f:
        raw_data = json.load(f)

    lookup = {}

    for obj in raw_data["objects"]:
        if obj.get("type") != "attack-pattern":
            continue

        if obj.get("revoked") or obj.get("x_mitre_deprecated"):
            continue

        technique_id = None
        for ref in obj.get("external_references", []):
            if ref.get("source_name") in ("mitre-attack", "mitre-ics-attack"):
                technique_id = ref.get("external_id")
                break

        if not technique_id:
            continue

        tactics = [
            phase["phase_name"].replace("-", " ").title()
            for phase in obj.get("kill_chain_phases", [])
        ]

        entry = {
            "id": technique_id,
            "name": obj["name"],
            "tactics": ", ".join(tactics),
            "source": source_label,
            "description": obj.get("description", "")[:200],
            "url": f"https://attack.mitre.org/techniques/{technique_id.replace('.', '/')}/"
        }

        lookup[obj["name"].lower()] = entry

        for alias in obj.get("x_mitre_aliases", []):
            lookup[alias.lower()] = entry

    return lookup


def build_combined_lookup():
    """
    Builds and merges lookup dictionaries from both the Enterprise and ICS
    datasets into a single unified dictionary.

    If a keyword exists in both datasets (unlikely but possible), the ICS
    entry takes precedence since we are testing against ICS-focused reports.

    Returns the merged lookup and a breakdown of how many techniques came
    from each dataset.
    """
    enterprise_lookup = _parse_dataset("enterprise-attack.json", "Enterprise")
    ics_lookup = _parse_dataset("ics-attack.json", "ICS")

    # Merge: start with Enterprise, let ICS overwrite any conflicts
    combined = {**enterprise_lookup, **ics_lookup}

    enterprise_count = len(set(v["id"] for v in enterprise_lookup.values()))
    ics_count = len(set(v["id"] for v in ics_lookup.values()))

    print(f"[+] Loaded {enterprise_count} Enterprise techniques and {ics_count} ICS techniques.")
    print(f"[+] Combined lookup: {len(combined)} searchable keywords.")

    return combined