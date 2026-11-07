# When Is a Data Point Actually Strange?

![Project visualization](visualization.svg)

**Field:** Data Science  
**Date:** 2026-11-07  
**Type:** Reproducible computational demonstration

## The big question

> How does the outlier threshold change flagged observations?

## Why this is interesting

Z-score screening depends on distributional assumptions.

The experiment explores how a mathematical or algorithmic assumption
shapes the results. It is intended to inspire deeper investigation,
not to claim a new scientific discovery.

## What I built

- A working Python model or algorithm
- A deterministic computational experiment
- A CSV dataset containing 31 evaluated observations
- A custom SVG visualization
- A reproducibility check and automated tests

## Method

- Generated 250 baseline points and 12 injected outliers.

The experiment uses random seed `104861633174083`.

All observations are synthetic or algorithmically generated.
No human participant data were collected.

## Results

| Metric | Value |
|---|---:|
| Observations | 31 |
| First output | 42.00000 |
| Last output | 5.00000 |
| Mean output | 13.93548 |
| Output range | 37.00000 |
| Endpoint slope | -12.33333 |

Across the evaluated range, the output **decreased**.

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
