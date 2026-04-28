# mapper/downloader.py

import os
import json
import requests

DATASETS = {
    "enterprise": {
        "url": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
        "local_file": "enterprise-attack.json"
    },
    "ics": {
        "url": "https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json",
        "local_file": "ics-attack.json"
    }
}


def download_dataset(dataset_name):
    """
    Downloads a named ATT&CK dataset if it does not already exist locally.

    dataset_name must be either "enterprise" or "ics".

    Both datasets are STIX2 JSON bundles published by MITRE on GitHub.
    Enterprise covers traditional IT environments (T1xxx techniques).
    ICS covers industrial control system environments (T0xxx techniques).

    The local file check means each dataset downloads only once and is
    reused on all subsequent runs.
    """
    config = DATASETS[dataset_name]
    local_file = config["local_file"]

    if not os.path.exists(local_file):
        print(f"[*] Downloading ATT&CK {dataset_name.upper()} dataset...")
        response = requests.get(config["url"])
        response.raise_for_status()
        with open(local_file, "w") as f:
            json.dump(response.json(), f)
        print(f"[+] {dataset_name.upper()} dataset downloaded.")
    else:
        print(f"[*] ATT&CK {dataset_name.upper()} dataset found locally. Skipping download.")


def download_all():
    """
    Downloads both Enterprise and ICS datasets.
    Called once at startup from main.py.
    """
    for name in DATASETS:
        download_dataset(name)