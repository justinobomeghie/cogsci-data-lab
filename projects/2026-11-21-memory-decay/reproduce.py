#!/usr/bin/env python3
"""Reproduce this project's computational output."""
import csv
import datetime as dt
import importlib.util
from pathlib import Path

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("model",here/"model.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

day=dt.date.fromisoformat(here.name[:10])
kind=module.project_for(day)[-1]
rng=module.random.Random(module.seed_for(day))
xs,ys,_=module.evaluate(kind,rng,module.seed_for(day))

with (here/"data.csv").open(newline="") as file:
    rows=list(csv.DictReader(file))

assert len(rows)==len(xs)
for row,x,y in zip(rows,xs,ys):
    assert abs(float(row["input"])-x)<1e-6
    assert abs(float(row["output"])-y)<1e-6

print("PASS: all",len(rows),"data points reproduced")
