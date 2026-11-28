#!/usr/bin/env python3
"""Reproduce descriptive statistics from the saved source data."""
import csv
from collections import defaultdict
from pathlib import Path

path = Path(__file__).with_name("observations.csv")
with path.open(newline="") as f:
    rows = list(csv.DictReader(f))

assert len(rows) >= 12
groups = defaultdict(list)

for row in rows:
    groups[row["country"]].append(
        (int(row["year"]), float(row["value"]))
    )

for country, observations in sorted(groups.items()):
    observations.sort()
    first, last = observations[0], observations[-1]
    print(
        country,
        "observations:", len(observations),
        "first:", first,
        "last:", last,
        "change:", round(last[1]-first[1], 3)
    )

print("PASS: published observations loaded and analyzed")
