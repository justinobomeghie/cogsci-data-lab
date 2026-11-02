#!/usr/bin/env python3
"""Daily evidence-based research using World Bank and NCBI PubMed."""
import csv
import datetime as dt
import html
import json
import math
import statistics
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = dt.datetime.now(dt.timezone.utc).date()

STUDIES = [
    {
        "slug": "education-and-opportunity",
        "field": "Cognitive Science × Education Data",
        "title": "How Has Access to Higher Education Changed?",
        "question": "How has tertiary education enrollment changed across countries?",
        "indicator": "SE.TER.ENRR",
        "unit": "Gross enrollment ratio (%)",
        "pubmed": "educational attainment cognitive development review",
    },
    {
        "slug": "health-and-longevity",
        "field": "Cognitive Science × Public Health",
        "title": "What Can Population Longevity Tell Us?",
        "question": "How have published life-expectancy estimates changed?",
        "indicator": "SP.DYN.LE00.IN",
        "unit": "Life expectancy at birth (years)",
        "pubmed": "cognitive aging population health review",
    },
    {
        "slug": "internet-and-society",
        "field": "Computer Science × Data Science",
        "title": "How Quickly Did the World Get Connected?",
        "question": "How has internet adoption changed across countries?",
        "indicator": "IT.NET.USER.ZS",
        "unit": "Individuals using the internet (% of population)",
        "pubmed": "digital technology cognition systematic review",
    },
    {
        "slug": "research-and-development",
        "field": "Computer Science × Innovation",
        "title": "How Much Do Countries Invest in Research?",
        "question": "How has research and development expenditure evolved?",
        "indicator": "GB.XPD.RSDV.GD.ZS",
        "unit": "Research and development expenditure (% of GDP)",
        "pubmed": "scientific innovation research productivity review",
    },
    {
        "slug": "education-investment",
        "field": "Data Science × Education",
        "title": "How Has Education Investment Changed?",
        "question": "How has government spending on education changed?",
        "indicator": "SE.XPD.TOTL.GD.ZS",
        "unit": "Government expenditure on education (% of GDP)",
        "pubmed": "education investment learning outcomes review",
    },
    {
        "slug": "population-and-change",
        "field": "Data Science × Computational Demography",
        "title": "Can We Understand Population Change?",
        "question": "How have national population estimates changed over time?",
        "indicator": "SP.POP.TOTL",
        "unit": "Total population (people)",
        "pubmed": "population demographic change public health review",
    },
]

COUNTRIES = ["USA", "CAN", "GBR"]
COLORS = ["#38bdf8", "#fbbf24", "#a78bfa"]

def fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "CuriosityLabResearch/1.0 (educational project)",
                 "Accept": "application/json"}
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

def world_bank(indicator):
    url = (
        "https://api.worldbank.org/v2/country/"
        + ";".join(COUNTRIES)
        + "/indicator/" + indicator
        + "?format=json&per_page=1000&date=2000:2025"
    )
    payload = fetch_json(url)
    if not isinstance(payload, list) or len(payload) != 2:
        raise RuntimeError("Unexpected World Bank response")

    records = []
    for item in payload[1] or []:
        value = item.get("value")
        year = item.get("date", "")
        country = item.get("countryiso3code", "")
        if (
            country in COUNTRIES
            and year.isdigit()
            and isinstance(value, (int, float))
            and math.isfinite(value)
        ):
            records.append({
                "country": country,
                "year": int(year),
                "value": float(value),
            })

    if len(records) < 12:
        raise RuntimeError("Not enough real observations for analysis")

    return url, sorted(records, key=lambda x: (x["country"], x["year"]))

def pubmed_search(query):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = base + "esearch.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": 5,
        "retmode": "json",
        "sort": "relevance",
        "tool": "curiosity_lab",
        "email": "research@example.org",
    })

    search = fetch_json(search_url)
    ids = search.get("esearchresult", {}).get("idlist", [])

    if not ids:
        return search_url, []

    summary_url = base + "esummary.fcgi?" + urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json",
        "tool": "curiosity_lab",
        "email": "research@example.org",
    })

    time.sleep(.4)
    summary = fetch_json(summary_url).get("result", {})
    papers = []

    for pmid in ids:
        item = summary.get(pmid, {})
        title = item.get("title", "").strip()
        if not title:
            continue
        authors = item.get("authors", [])
        papers.append({
            "pmid": pmid,
            "title": title,
            "journal": item.get("fulljournalname", ""),
            "date": item.get("pubdate", ""),
            "authors": ", ".join(
                a.get("name", "") for a in authors[:4]
            ),
            "url": "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/",
        })

    return search_url, papers

def svg_chart(records, title, unit):
    w, h = 960, 520
    left, right, top, bottom = 95, 45, 95, 85
    pw, ph = w-left-right, h-top-bottom
    years = [r["year"] for r in records]
    values = [r["value"] for r in records]
    xmin, xmax = min(years), max(years)
    ymin, ymax = min(values), max(values)
    padding = max((ymax-ymin)*.12, .01)
    ymin -= padding
    ymax += padding

    def px(x):
        return left+(x-xmin)/max(xmax-xmin,1)*pw

    def py(y):
        return top+(ymax-y)/max(ymax-ymin,1e-9)*ph

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">',
        '<rect width="100%" height="100%" rx="18" fill="#0b1220"/>',
        '<text x="45" y="40" fill="#67e8f9" font-size="16" '
        'font-family="Arial">THE CURIOSITY LAB / REAL-WORLD DATA</text>',
        f'<text x="45" y="76" fill="white" font-size="25" '
        f'font-family="Arial">{html.escape(title)}</text>',
    ]

    for i in range(6):
        val = ymin+(ymax-ymin)*i/5
        y = py(val)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" '
            f'x2="{w-right}" y2="{y:.1f}" stroke="#334155"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{y+4:.1f}" '
            f'text-anchor="end" fill="#cbd5e1" font-size="13">'
            f'{val:,.1f}</text>'
        )

    for index, country in enumerate(COUNTRIES):
        rows = sorted(
            (r for r in records if r["country"] == country),
            key=lambda r: r["year"]
        )
        if not rows:
            continue
        points = " ".join(
            f'{px(r["year"]):.1f},{py(r["value"]):.1f}'
            for r in rows
        )
        color = COLORS[index]
        parts.append(
            f'<polyline points="{points}" fill="none" '
            f'stroke="{color}" stroke-width="3.5"/>'
        )
        parts.append(
            f'<text x="{left+index*170}" y="{h-48}" '
            f'fill="{color}" font-family="Arial" '
            f'font-size="16">{country}</text>'
        )

    parts.extend([
        f'<text x="{w/2}" y="{h-17}" text-anchor="middle" '
        f'fill="#cbd5e1" font-size="14">Year · {html.escape(unit)}</text>',
        '</svg>'
    ])
    return "\n".join(parts)

def main():
    index = (TODAY.toordinal() - dt.date(2026,1,1).toordinal()) % len(STUDIES)
    study = STUDIES[index]
    folder = ROOT / "evidence" / (TODAY.isoformat() + "-" + study["slug"])

    if folder.exists():
        print("Evidence study already exists:", folder.name)
        return

    print("Fetching published World Bank observations...")
    data_url, records = world_bank(study["indicator"])

    print("Finding related PubMed research...")
    literature_url, papers = pubmed_search(study["pubmed"])

    # Only create the project after source retrieval succeeds.
    folder.mkdir(parents=True)

    with (folder / "observations.csv").open("w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=["country", "year", "value"]
        )
        writer.writeheader()
        writer.writerows(records)

    (folder / "literature.json").write_text(
        json.dumps(papers, indent=2), encoding="utf-8"
    )

    (folder / "chart.svg").write_text(
        svg_chart(records, study["title"], study["unit"]),
        encoding="utf-8"
    )

    findings = []
    for country in COUNTRIES:
        rows = sorted(
            (r for r in records if r["country"] == country),
            key=lambda r: r["year"]
        )
        if len(rows) < 2:
            continue

        first, last = rows[0], rows[-1]
        change = last["value"] - first["value"]
        findings.append(
            f"| {country} | {first['year']} | {last['year']} | "
            f"{first['value']:,.2f} | {last['value']:,.2f} | "
            f"{change:+,.2f} |"
        )

    references = []
    for paper in papers:
        title = paper["title"].replace("|", " ")
        references.append(
            f"- [{title}]({paper['url']}) — "
            f"{paper['authors']}; {paper['journal']} "
            f"({paper['date']}). PMID: {paper['pmid']}"
        )

    if not references:
        references = [
            "No PubMed records were returned for this search."
        ]

    readme = f"""# {study['title']}

![Observed data visualization](chart.svg)

**Field:** {study['field']}  
**Date generated:** {TODAY.isoformat()}  
**Evidence type:** Published statistical observations  
**Data provider:** World Bank  
**Literature index:** NCBI PubMed

## Research question

{study['question']}

## Why this matters

This project investigates a measurable, real-world pattern using
published observations rather than simulated participant data.

## Data provenance

- **Indicator:** {study['indicator']}
- **Measurement:** {study['unit']}
- **Countries:** United States, Canada, United Kingdom
- **Observation years requested:** 2000–2025
- **Retrieved (UTC):** {dt.datetime.now(dt.timezone.utc).isoformat()}
- **Original API response:** {data_url}
- **Indicator metadata:** https://api.worldbank.org/v2/indicator/{study['indicator']}?format=json

Missing values were omitted. No values were interpolated or fabricated.

## Descriptive results

| Country | First year | Last year | First value | Last value | Change |
|---|---:|---:|---:|---:|---:|
{chr(10).join(findings)}

These are differences between each country's first and last
available observations in the requested period. Countries may
have different coverage dates.

The change is expressed in the indicator's own units, not
automatically as a percentage change.

## Related research from PubMed

**Search query:** `{study['pubmed']}`

**Search endpoint:** {literature_url}

{chr(10).join(references)}

These articles are **related literature leads**, not independently
verified support for the numerical results above.

Their titles and bibliographic metadata were retrieved from
PubMed. Full articles were not analyzed, and no claim is made
that these studies establish causality or validate this analysis.

## Reproduce the descriptive analysis

```bash
python3 analyze.py
```

## Limitations

1. This is descriptive analysis, not causal inference.
2. The World Bank may revise historical observations.
3. National statistics can use differing collection methods.
4. Missing years and unequal country coverage affect comparisons.
5. Related PubMed papers may study different populations or outcomes.
6. Data and literature are not independently peer-reviewed by
   this automation.

## Next research questions

- What explains differences between the observed trajectories?
- Are changes robust to using the same start and end years?
- What do the original indicator metadata and source notes say?
- Which related publications directly study these measurements?
- Could a more appropriate statistical model reveal uncertainty?

## Scientific integrity

This project uses real published observations, with their source
URLs recorded. It does not claim a new discovery, a causal
relationship, or original human-subject research.

Automated research preparation requires human review.
"""

    (folder / "README.md").write_text(readme, encoding="utf-8")

    analysis = '''#!/usr/bin/env python3
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
'''
    (folder / "analyze.py").write_text(analysis, encoding="utf-8")

    # Ensure the saved dataset is analyzable before publishing.
    import subprocess
    subprocess.run(
        [sys.executable, str(folder / "analyze.py")],
        check=True
    )

    print("Published-data study created:", folder.name)

if __name__ == "__main__":
    main()
