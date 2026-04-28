# mapper/reporter.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime


def generate_report(matched_ttps, output_dir="output", source_filename="report"):
    """
    Generates three output files:
      1. CSV  — structured TTP table, easy to open anywhere
      2. Excel — same table, formatted for stakeholder sharing
      3. PNG  — tactic frequency bar chart

    The source column (Enterprise or ICS) is new in v1.1 and makes
    the dataset split visible in the output without requiring the reader
    to know the T-ID namespace conventions.
    """
    if not matched_ttps:
        print("[-] No TTPs found. Nothing to export.")
        return

    df = pd.DataFrame(matched_ttps)

    # Reorder columns — source column is new in v1.1
    column_order = ["id", "name", "tactics", "source", "confidence", "match_type", "description", "url"]
    df = df[[col for col in column_order if col in df.columns]]
    df.columns = [col.replace("_", " ").title() for col in df.columns]

    # Sort by confidence, then technique ID
    confidence_order = {"High": 0, "Medium": 1, "Low": 2}
    df["_sort"] = df["Confidence"].map(confidence_order)
    df = df.sort_values(["_sort", "Id"]).drop(columns=["_sort"])

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    base_name = os.path.splitext(os.path.basename(source_filename))[0]

    csv_path = os.path.join(output_dir, f"{base_name}_ttp_map_{timestamp}.csv")
    xlsx_path = os.path.join(output_dir, f"{base_name}_ttp_map_{timestamp}.xlsx")
    chart_path = os.path.join(output_dir, f"{base_name}_tactic_chart_{timestamp}.png")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False)
    print(f"[+] CSV saved:   {csv_path}")
    print(f"[+] Excel saved: {xlsx_path}")

    _generate_tactic_chart(df, chart_path, base_name)

    print(f"\n{'='*60}")
    print(df.to_string(index=False))

    return df


def _generate_tactic_chart(df, chart_path, title_label):
    """
    Generates a horizontal bar chart showing tactic frequency —
    how many techniques were identified per ATT&CK tactic.

    Horizontal bars are used instead of vertical because tactic names
    are long strings that overlap badly on a vertical x-axis.

    Each bar is color-coded by dataset source: blue for Enterprise,
    orange for ICS, making the framework split immediately visible.

    The chart is saved as a PNG file alongside the CSV and Excel outputs.
    It is also the natural screenshot to include in the Substack post and
    GitHub README.
    """
    # A single technique can belong to multiple tactics (comma-separated).
    # We explode these so each tactic gets its own row for counting.
    tactic_rows = []

    for _, row in df.iterrows():
        tactics = [t.strip() for t in str(row.get("Tactics", "")).split(",")]
        source = row.get("Source", "Enterprise")
        for tactic in tactics:
            if tactic:
                tactic_rows.append({"tactic": tactic, "source": source})

    if not tactic_rows:
        print("[-] No tactic data to chart.")
        return

    tactic_df = pd.DataFrame(tactic_rows)

    # Count techniques per tactic per source
    counts = tactic_df.groupby(["tactic", "source"]).size().unstack(fill_value=0)

    # Sort by total count descending
    counts["total"] = counts.sum(axis=1)
    counts = counts.sort_values("total", ascending=True).drop(columns="total")

    # Plot
    fig, ax = plt.subplots(figsize=(10, max(5, len(counts) * 0.5)))

    colors = {"Enterprise": "#4C72B0", "ICS": "#DD8452"}
    counts.plot(
        kind="barh",
        ax=ax,
        color=[colors.get(col, "#888888") for col in counts.columns],
        width=0.6
    )

    ax.set_xlabel("Technique Count", fontsize=11)
    ax.set_ylabel("")
    ax.set_title(f"ATT&CK Tactic Coverage — {title_label}", fontsize=13, fontweight="bold")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.legend(title="Dataset", loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close()

    print(f"[+] Tactic chart saved: {chart_path}")