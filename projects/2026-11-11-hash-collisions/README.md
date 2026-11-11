# Why Do Hash Tables Sometimes Slow Down?

![Project visualization](visualization.svg)

**Field:** Computer Science  
**Date:** 2026-11-11  
**Type:** Reproducible computational demonstration

## The big question

> How does table occupancy affect collision frequency?

## Why this is interesting

Collisions become more frequent as a table fills.

The experiment explores how a mathematical or algorithmic assumption
shapes the results. It is intended to inspire deeper investigation,
not to claim a new scientific discovery.

## What I built

- A working Python model or algorithm
- A deterministic computational experiment
- A CSV dataset containing 23 evaluated observations
- A custom SVG visualization
- A reproducibility check and automated tests

## Method

- Implemented linear probing in a 257-slot table.

The experiment uses random seed `86432876976638`.

All observations are synthetic or algorithmically generated.
No human participant data were collected.

## Results

| Metric | Value |
|---|---:|
| Observations | 23 |
| First output | 0.00000 |
| Last output | 849.00000 |
| Mean output | 182.82609 |
| Output range | 849.00000 |
| Endpoint slope | 3.85909 |

Across the evaluated range, the output **increased**.

This is a property of this particular model and parameter setting,
not evidence that all real-world systems behave the same way.

## Reproduce it

```bash
python3 reproduce.py
python3 -m unittest discover -s tests -v
```

## What this does NOT prove

- It does not establish causality.
- It does not validate the model against real-world data.
- It does not demonstrate a new scientific discovery.
- Its conclusions are limited to the implemented assumptions.

## Where to go next

1. Change a model assumption and compare the resulting curve.
2. Add uncertainty estimates or sensitivity analysis.
3. Find an appropriate openly licensed empirical dataset.
4. Compare this method with a competing algorithm.
5. Explain what would falsify the model's predictions.

## Project files

- `model.py` — self-contained computational experiment
- `data.csv` — generated observations
- `visualization.svg` — custom data visualization
- `reproduce.py` — checks reproducibility
- `tests/` — automated consistency checks

*Generated computationally by The Curiosity Lab.
Human review and independent empirical validation are encouraged.*
