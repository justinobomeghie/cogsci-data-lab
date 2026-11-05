#!/usr/bin/env python3
"""The Curiosity Lab: reproducible computational mini-projects."""
import csv
import datetime as dt
import hashlib
import html
import json
import math
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "projects"

# Every family is a distinct computational question.
# The library rotates through all 18 before repeating.
FAMILIES = [
    ("cognitive-science", "memory-decay",
     "Can We Predict What You Will Forget?",
     "How does retention change as time passes?",
     "An exponential forgetting model illustrates memory decay.",
     "Hours since learning", "Recall probability", "memory"),
    ("data-science", "clustering",
     "Can Algorithms Discover Hidden Groups?",
     "Can unsupervised learning recover structure in noisy data?",
     "K-means minimizes within-cluster squared distances.",
     "Data point index", "Distance to assigned centroid", "cluster"),
    ("computer-science", "search-algorithms",
     "How Fast Can an Algorithm Find a Path?",
     "How does breadth-first search scale on grid mazes?",
     "Breadth-first search finds shortest paths in unweighted graphs.",
     "Grid width", "Nodes explored", "search"),
    ("cognitive-science", "decision-noise",
     "Why Do We Sometimes Choose the Worse Option?",
     "How does decision noise change choice probabilities?",
     "A softmax model describes stochastic choices.",
     "Choice temperature", "Probability of better choice", "softmax"),
    ("data-science", "outlier-detection",
     "When Is a Data Point Actually Strange?",
     "How does the outlier threshold change flagged observations?",
     "Z-score screening depends on distributional assumptions.",
     "Z-score threshold", "Flagged observations", "outliers"),
    ("computer-science", "sorting-race",
     "Which Sorting Algorithm Wins?",
     "How do comparison counts scale with input size?",
     "Insertion sort has quadratic worst-case comparison growth.",
     "Array length", "Comparisons", "sorting"),
    ("cognitive-science", "learning-curves",
     "Why Does Practice Help Less Over Time?",
     "What happens to skill improvement over repeated practice?",
     "Saturating learning curves model diminishing gains.",
     "Practice session", "Predicted performance", "learning"),
    ("data-science", "sampling-bias",
     "Can a Sample Tell the Wrong Story?",
     "How does sampling bias distort estimated population averages?",
     "Nonrepresentative samples can yield biased estimates.",
     "Selection bias strength", "Estimated population mean", "sampling"),
    ("computer-science", "hash-collisions",
     "Why Do Hash Tables Sometimes Slow Down?",
     "How does table occupancy affect collision frequency?",
     "Collisions become more frequent as a table fills.",
     "Items inserted", "Total collisions", "hash"),
    ("cognitive-science", "signal-detection",
     "Can You Separate Signal from Noise?",
     "How does perceptual sensitivity affect detection accuracy?",
     "Signal detection theory distinguishes sensitivity and criterion.",
     "Sensitivity d-prime", "Expected accuracy", "signal"),
    ("data-science", "bootstrap",
     "How Certain Is an Average?",
     "How does sample size affect bootstrap uncertainty?",
     "Resampling approximates the variability of a statistic.",
     "Sample size", "Bootstrap 95% interval width", "bootstrap"),
    ("computer-science", "graph-connectivity",
     "When Does a Network Become Connected?",
     "How does adding edges change graph connectivity?",
     "Random graph connectivity exhibits a transition as edges accumulate.",
     "Edges added", "Largest component size", "graph"),
    ("cognitive-science", "working-memory",
     "How Much Can Working Memory Hold?",
     "How does item load affect modeled recall accuracy?",
     "Capacity-limited models predict declining accuracy under load.",
     "Items to remember", "Recall probability", "working"),
    ("data-science", "overfitting",
     "Can a Model Memorize Instead of Learn?",
     "How does polynomial complexity affect held-out error?",
     "High model complexity can fit noise rather than generalizable structure.",
     "Polynomial degree", "Test mean squared error", "overfit"),
    ("computer-science", "compression",
     "How Much Can Repetition Shrink a Message?",
     "How does run-length encoding behave as repetition increases?",
     "Compression efficiency depends on data structure.",
     "Average run length", "Encoded/original size ratio", "compress"),
    ("cognitive-science", "reaction-time",
     "Why Do More Choices Slow Us Down?",
     "How does the number of alternatives affect reaction time?",
     "The Hick-Hyman relationship links choice count and response latency.",
     "Number of choices", "Predicted reaction time (ms)", "reaction"),
    ("data-science", "correlation",
     "Does Correlation Mean Prediction?",
     "How does noise weaken an observable relationship?",
     "Correlation measures linear association, not causality.",
     "Noise standard deviation", "Pearson correlation", "correlation"),
    ("computer-science", "random-walks",
     "How Far Does a Random Walker Travel?",
     "How does displacement grow with random-walk length?",
     "Independent random steps yield diffusive scaling.",
     "Number of steps", "Mean distance from origin", "walk"),
]

def seed_for(day):
    return int(hashlib.sha256(day.isoformat().encode()).hexdigest()[:12], 16)

def mean(values):
    return statistics.mean(values)

def std(values):
    return statistics.pstdev(values)

def corr(a, b):
    am, bm = mean(a), mean(b)
    top = sum((x-am)*(y-bm) for x,y in zip(a,b))
    bottom = math.sqrt(
        sum((x-am)**2 for x in a) *
        sum((y-bm)**2 for y in b)
    )
    return top / bottom if bottom else 0.0

def solve_linear(matrix, vector):
    n = len(vector)
    a = [list(matrix[i]) + [vector[i]] for i in range(n)]
    for k in range(n):
        pivot = max(range(k,n), key=lambda i: abs(a[i][k]))
        a[k], a[pivot] = a[pivot], a[k]
        if abs(a[k][k]) < 1e-12:
            return None
        div = a[k][k]
        a[k] = [v/div for v in a[k]]
        for i in range(n):
            if i != k:
                factor = a[i][k]
                a[i] = [u-factor*v for u,v in zip(a[i],a[k])]
    return [a[i][-1] for i in range(n)]

def polyfit(xs, ys, degree):
    # Ridge-stabilized least squares using scaled input coordinates.
    scale = max(abs(x) for x in xs) or 1
    z = [x/scale for x in xs]
    matrix = [
        [sum(t**(i+j) for t in z) +
         (1e-7 if i == j else 0)
         for j in range(degree+1)]
        for i in range(degree+1)
    ]
    vector = [sum(y*t**i for t,y in zip(z,ys))
              for i in range(degree+1)]
    return solve_linear(matrix,vector),scale

def evaluate(kind, rng, variant):
    xs, ys = [], []
    details = []
    if kind == "memory":
        decay = rng.uniform(.035,.10)
        xs = list(range(0,49,2))
        ys = [math.exp(-decay*x) for x in xs]
        details.append(f"Decay constant: {decay:.4f} per hour.")
    elif kind == "cluster":
        centers = [(-3,-2),(3,2),(-2,4)]
        points = [(cx+rng.gauss(0,.8),cy+rng.gauss(0,.8))
                  for cx,cy in centers for _ in range(35)]
        centroids = [points[i] for i in (0,35,70)]
        for _ in range(25):
            groups = [[] for _ in centroids]
            for point in points:
                idx = min(range(3),
                    key=lambda j: sum((point[d]-centroids[j][d])**2
                                      for d in range(2)))
                groups[idx].append(point)
            new = [
                (mean([p[0] for p in group]),
                 mean([p[1] for p in group]))
                if group else centroids[i]
                for i,group in enumerate(groups)
            ]
            if new == centroids:
                break
            centroids = new
        xs = list(range(len(points)))
        ys = [math.sqrt(min(sum((p[d]-c[d])**2 for d in range(2))
                  for c in centroids)) for p in points]
        details.append("Implemented k-means with three clusters.")
    elif kind == "search":
        from collections import deque
        for n in range(6,31,2):
            blocked = {(x,y) for x in range(n) for y in range(n)
                       if rng.random()<.17 and
                       (x,y) not in ((0,0),(n-1,n-1))}
            q = deque([(0,0)])
            visited = {(0,0)}
            while q:
                x,y = q.popleft()
                if (x,y)==(n-1,n-1):
                    break
                for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0<=p[0]<n and 0<=p[1]<n and \
                       p not in blocked and p not in visited:
                        visited.add(p)
                        q.append(p)
            xs.append(n)
            ys.append(len(visited))
        details.append("Implemented BFS on randomly obstructed grids.")
    elif kind == "softmax":
        xs = [i/10 for i in range(1,41)]
        ys = [1/(1+math.exp(-1.5/x)) for x in xs]
    elif kind == "outliers":
        data = [rng.gauss(0,1) for _ in range(250)]
        data += [rng.choice([-1,1])*rng.uniform(4,7)
                 for _ in range(12)]
        m,s = mean(data),std(data)
        xs = [i/10 for i in range(10,41)]
        ys = [sum(abs(v-m)/s>x for v in data) for x in xs]
        details.append("Generated 250 baseline points and 12 injected outliers.")
    elif kind == "sorting":
        for n in range(10,151,10):
            values = [rng.random() for _ in range(n)]
            comparisons = 0
            for i in range(1,n):
                key = values[i]
                j = i-1
                while j>=0:
                    comparisons += 1
                    if values[j]<=key:
                        break
                    values[j+1]=values[j]
                    j-=1
                values[j+1]=key
            xs.append(n)
            ys.append(comparisons)
        details.append("Counted comparisons in actual insertion-sort runs.")
    elif kind == "learning":
        rate = rng.uniform(.06,.18)
        xs = list(range(1,41))
        ys = [.3+.65*(1-math.exp(-rate*x)) for x in xs]
    elif kind == "sampling":
        population = [rng.gauss(50,12) for _ in range(5000)]
        for strength in range(11):
            factor = strength/10
            weights = [
                max(.01,1+factor*(v-50)/12)
                for v in population
            ]
            sample = rng.choices(population,weights=weights,k=250)
            xs.append(round(factor,2))
            ys.append(mean(sample))
        details.append(f"True synthetic population mean: {mean(population):.2f}.")
    elif kind == "hash":
        slots = [False]*257
        collisions = 0
        for i in range(1,231):
            key = rng.randrange(10000000)
            index = key%257
            while slots[index]:
                collisions+=1
                index=(index+1)%257
            slots[index]=True
            if i%10==0:
                xs.append(i)
                ys.append(collisions)
        details.append("Implemented linear probing in a 257-slot table.")
    elif kind == "signal":
        xs = [i/10 for i in range(0,41)]
        ys = [.5*(1+math.erf(x/(2*math.sqrt(2)))) for x in xs]
        details.append("Equal-variance Gaussian detection model, unbiased criterion.")
    elif kind == "bootstrap":
        for n in range(15,151,15):
            sample = [rng.gauss(10,3) for _ in range(n)]
            estimates = sorted(
                mean(rng.choices(sample,k=n))
                for _ in range(300)
            )
            xs.append(n)
            ys.append(estimates[292]-estimates[7])
        details.append("300 bootstrap resamples per sample size.")
    elif kind == "graph":
        n = 60
        parent = list(range(n))
        size = [1]*n
        def find(x):
            while parent[x]!=x:
                parent[x]=parent[parent[x]]
                x=parent[x]
            return x
        edges = [(i,j) for i in range(n) for j in range(i+1,n)]
        rng.shuffle(edges)
        largest = 1
        for k,(a,b) in enumerate(edges[:180],1):
            a,b=find(a),find(b)
            if a!=b:
                if size[a]<size[b]:
                    a,b=b,a
                parent[b]=a
                size[a]+=size[b]
                largest=max(largest,size[a])
            if k%5==0:
                xs.append(k)
                ys.append(largest)
        details.append("Implemented union-find on a 60-node random graph.")
    elif kind == "working":
        midpoint = rng.uniform(4,7)
        xs = list(range(1,17))
        ys = [.3+.68/(1+math.exp(.9*(x-midpoint))) for x in xs]
    elif kind == "overfit":
        train_x = [i/12 for i in range(-12,13)]
        test_x = [(i+.5)/12 for i in range(-12,12)]
        truth = lambda x: .6*x*x-.3*x+.2
        train_y = [truth(x)+rng.gauss(0,.12) for x in train_x]
        for degree in range(1,13):
            coefficients,scale = polyfit(train_x,train_y,degree)
            if coefficients is None:
                continue
            prediction = [
                sum(c*(x/scale)**i for i,c in enumerate(coefficients))
                for x in test_x
            ]
            error = mean([(a-truth(x))**2
                          for a,x in zip(prediction,test_x)])
            xs.append(degree)
            ys.append(error)
        details.append("Tested polynomial fits against the known generating function.")
    elif kind == "compress":
        for run_length in range(1,26):
            source = "".join(
                rng.choice("ABCD")*run_length
                for _ in range(60)
            )
            # RLE format: one character followed by decimal count and semicolon.
            encoded = []
            i = 0
            while i<len(source):
                j=i+1
                while j<len(source) and source[j]==source[i]:
                    j+=1
                encoded.append(f"{source[i]}{j-i};")
                i=j
            xs.append(run_length)
            ys.append(len("".join(encoded))/len(source))
        details.append("Measured actual run-length encoded string lengths.")
    elif kind == "reaction":
        slope = rng.uniform(85,165)
        xs = list(range(1,33))
        ys = [220+slope*math.log2(x) for x in xs]
    elif kind == "correlation":
        for noise in [i/10 for i in range(0,31,2)]:
            x = [rng.gauss(0,1) for _ in range(300)]
            y = [v+rng.gauss(0,noise) for v in x]
            xs.append(noise)
            ys.append(corr(x,y))
        details.append("Computed Pearson correlations from generated paired observations.")
    elif kind == "walk":
        for steps in range(10,501,20):
            distances = []
            for _ in range(120):
                x=y=0
                for _ in range(steps):
                    direction=rng.randrange(4)
                    x += (direction==0)-(direction==1)
                    y += (direction==2)-(direction==3)
                distances.append(math.hypot(x,y))
            xs.append(steps)
            ys.append(mean(distances))
        details.append("Simulated 120 independent 2D random walks per step count.")
    else:
        raise ValueError(kind)
    assert len(xs)==len(ys) and len(xs)>1
    assert all(math.isfinite(float(y)) for y in ys)
    return xs,ys,details

def chart(xs,ys,title,xlabel,ylabel):
    width,height=1000,560
    left,right,top,bottom=115,55,95,95
    pw=width-left-right
    ph=height-top-bottom
    xmin,xmax=min(xs),max(xs)
    ymin,ymax=min(ys),max(ys)
    padding=max((ymax-ymin)*.12,.03)
    ymin-=padding
    ymax+=padding
    px=lambda x:left+(x-xmin)/max(xmax-xmin,1e-9)*pw
    py=lambda y:top+(ymax-y)/max(ymax-ymin,1e-9)*ph
    esc=html.escape
    parts=[
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<defs><linearGradient id="bg" x2="1" y2="1">'
        '<stop stop-color="#0b1022"/>'
        '<stop offset="1" stop-color="#142d42"/>'
        '</linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="22" fill="url(#bg)"/>',
        f'<text x="50" y="45" fill="#67e8f9" font-family="Arial" font-size="15" font-weight="bold">THE CURIOSITY LAB / COMPUTATIONAL STUDY</text>',
        f'<text x="50" y="76" fill="#ffffff" font-family="Arial" font-size="25" font-weight="bold">{esc(title)}</text>',
    ]
    for i in range(6):
        value=ymin+(ymax-ymin)*i/5
        y=py(value)
        parts.extend([
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#334155"/>',
            f'<text x="{left-15}" y="{y+5:.1f}" text-anchor="end" fill="#cbd5e1" font-size="14" font-family="Arial">{value:.2f}</text>'
        ])
    points=" ".join(f"{px(x):.1f},{py(y):.1f}" for x,y in zip(xs,ys))
    parts.append(f'<polyline points="{points}" fill="none" stroke="#22d3ee" stroke-width="4" stroke-linejoin="round"/>')
    for x,y in zip(xs,ys):
        parts.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="3.5" fill="#fbbf24"/>')
    parts.extend([
        f'<text x="{width/2}" y="{height-25}" text-anchor="middle" fill="#f8fafc" font-size="18" font-family="Arial">{esc(xlabel)}</text>',
        f'<text transform="translate(30,{height/2}) rotate(-90)" text-anchor="middle" fill="#f8fafc" font-size="18" font-family="Arial">{esc(ylabel)}</text>',
        f'<text x="{left}" y="{height-68}" fill="#cbd5e1" font-size="13">{xmin:g}</text>',
        f'<text x="{width-right}" y="{height-68}" text-anchor="end" fill="#cbd5e1" font-size="13">{xmax:g}</text>',
        '</svg>'
    ])
    return "\n".join(parts)

def project_for(day):
    # Calendar-driven round robin with a fixed offset.
    index=(day.toordinal()-dt.date(2026,1,1).toordinal())%len(FAMILIES)
    return FAMILIES[index]

def build(day):
    family=project_for(day)
    category,slug,title,question,theory,xlabel,ylabel,kind=family
    directory=PROJECTS / f"{day.isoformat()}-{slug}"
    if directory.exists():
        print("Already exists:",directory)
        return False

    seed=seed_for(day)
    rng=random.Random(seed)
    xs,ys,details=evaluate(kind,rng,seed)
    directory.mkdir(parents=True)

    with (directory/"data.csv").open("w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["input","output"])
        for x,y in zip(xs,ys):
            writer.writerow([f"{x:.8f}",f"{y:.8f}"])

    (directory/"visualization.svg").write_text(
        chart(xs,ys,title,xlabel,ylabel),encoding="utf-8"
    )

    slope=(ys[-1]-ys[0])/(xs[-1]-xs[0])
    trend="increased" if ys[-1]>ys[0] else (
        "decreased" if ys[-1]<ys[0] else "stayed constant"
    )

    notes="\n".join("- "+item for item in details) or \
          "- Evaluated the stated mathematical model."

    report=f"""# {title}

![Project visualization](visualization.svg)

**Field:** {category.replace("-", " ").title()}  
**Date:** {day.isoformat()}  
**Type:** Reproducible computational demonstration

## The big question

> {question}

## Why this is interesting

{theory}

The experiment explores how a mathematical or algorithmic assumption
shapes the results. It is intended to inspire deeper investigation,
not to claim a new scientific discovery.

## What I built

- A working Python model or algorithm
- A deterministic computational experiment
- A CSV dataset containing {len(xs)} evaluated observations
- A custom SVG visualization
- A reproducibility check and automated tests

## Method

{notes}

The experiment uses random seed `{seed}`.

All observations are synthetic or algorithmically generated.
No human participant data were collected.

## Results

| Metric | Value |
|---|---:|
| Observations | {len(xs)} |
| First output | {ys[0]:.5f} |
| Last output | {ys[-1]:.5f} |
| Mean output | {mean(ys):.5f} |
| Output range | {max(ys)-min(ys):.5f} |
| Endpoint slope | {slope:.5f} |

Across the evaluated range, the output **{trend}**.

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
"""
    (directory/"README.md").write_text(report,encoding="utf-8")

    # Copy the self-contained computational implementation into the project.
    source=Path(__file__).read_text(encoding="utf-8")
    (directory/"model.py").write_text(source,encoding="utf-8")

    reproduce='''#!/usr/bin/env python3
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
'''
    (directory/"reproduce.py").write_text(
        reproduce,encoding="utf-8"
    )

    tests=directory/"tests"
    tests.mkdir()
    (tests/"test_reproducibility.py").write_text(
        '''import subprocess
import sys
import unittest
from pathlib import Path

class ProjectTests(unittest.TestCase):
    def test_reproduction(self):
        project=Path(__file__).resolve().parents[1]
        result=subprocess.run(
            [sys.executable,str(project/"reproduce.py")],
            capture_output=True,text=True
        )
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("PASS:",result.stdout)

    def test_chart_exists(self):
        project=Path(__file__).resolve().parents[1]
        chart=(project/"visualization.svg").read_text()
        self.assertIn("<svg",chart)
        self.assertIn("</svg>",chart)

if __name__=="__main__":
    unittest.main()
''',encoding="utf-8")

    # Validate the generated project before allowing it to be committed.
    import subprocess
    result=subprocess.run(
        [sys.executable,"-m","unittest","discover",
         "-s",str(tests),"-v"],
        capture_output=True,text=True
    )
    if result.returncode:
        raise RuntimeError(result.stdout+"\n"+result.stderr)

    print("Created and tested:",directory.name)
    return True

def homepage():
    entries=[]
    for folder in sorted(PROJECTS.glob("20??-??-??-*"),reverse=True):
        if (folder/"README.md").exists():
            lines=(folder/"README.md").read_text().splitlines()
            title=lines[0].removeprefix("# ").strip()
            entries.append((folder.name,title))
    categories={
        "cognitive-science":"🧠 Cognitive Science",
        "data-science":"📊 Data Science",
        "computer-science":"💻 Computer Science"
    }
    lines=[
        "# 🔬 The Curiosity Lab",
        "",
        "### Minds. Data. Algorithms. One question at a time.",
        "",
        "A collection of computational explorations across",
        "**cognitive science, data science, and computer science**.",
        "",
        "Each mini-project includes reproducible Python, a data",
        "visualization, a research question, tests, and limitations.",
        "",
        "> **Research integrity:** These are automated computational",
        "> demonstrations, not peer-reviewed discoveries or",
        "> experiments involving real human participants.",
        "",
        "## Explore the lab",
        "",
        f"**{len(entries)} projects** across three disciplines.",
        ""
    ]
    for category,label in categories.items():
        lines.extend(["### "+label,""])
        matching=[
            (name,title) for name,title in entries
            if any(name.endswith("-"+f[1]) for f in FAMILIES
                   if f[0]==category)
        ]
        for name,title in matching[:25]:
            lines.append(f"- [{title}](projects/{name}/README.md) "
                         f"— `{name[:10]}`")
        if not matching:
            lines.append("Projects coming soon.")
        lines.append("")
    lines.extend([
        "## How to reproduce a project",
        "",
        "```bash",
        "cd projects/YYYY-MM-DD-project-name",
        "python3 reproduce.py",
        "python3 -m unittest discover -s tests -v",
        "```",
        "",
        "## Design principles",
        "",
        "- Curiosity before hype",
        "- Runnable code before claims",
        "- Clear limitations before overconfidence",
        "- Beautiful, accessible visualizations",
        "- Transparent automation and data provenance",
        "",
        "## About",
        "",
        "Projects are generated using a curated set of 18",
        "computational project families. A new dated experiment",
        "uses its own deterministic parameters or simulations.",
        "The same research theme may return after a full rotation.",
        "",
        "Automation helps maintain a daily practice; substantive",
        "research contributions require human review and extension.",
        ""
    ])
    (ROOT/"README.md").write_text("\n".join(lines),encoding="utf-8")

def main():
    day=dt.date.today()
    if len(sys.argv)==3 and sys.argv[1]=="--date":
        day=dt.date.fromisoformat(sys.argv[2])
    PROJECTS.mkdir(parents=True,exist_ok=True)
    build(day)
    homepage()

if __name__=="__main__":
    main()
