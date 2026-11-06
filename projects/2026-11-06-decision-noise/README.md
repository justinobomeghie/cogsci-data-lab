# Why Do We Sometimes Choose the Worse Option?

![Project visualization](visualization.svg)

**Field:** Cognitive Science  
**Date:** 2026-11-06  
**Type:** Reproducible computational demonstration

## The big question

> How does decision noise change choice probabilities?

## Why this is interesting

A softmax model describes stochastic choices.

The experiment explores how a mathematical or algorithmic assumption
shapes the results. It is intended to inspire deeper investigation,
not to claim a new scientific discovery.

## What I built

- A working Python model or algorithm
- A deterministic computational experiment
- A CSV dataset containing 40 evaluated observations
- A custom SVG visualization
- A reproducibility check and automated tests

## Method

- Evaluated the stated mathematical model.

The experiment uses random seed `136615942710017`.

All observations are synthetic or algorithmically generated.
No human participant data were collected.

## Results

| Metric | Value |
|---|---:|
| Observations | 40 |
| First output | 1.00000 |
| Last output | 0.59267 |
| Mean output | 0.72649 |
| Output range | 0.40733 |
| Endpoint slope | -0.10444 |

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
