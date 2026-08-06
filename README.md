# MazeBench: A Comparative Study of Pathfinding Algorithms

An interactive maze-solving application with **real-time visualization** and an integrated **benchmarking framework** for comparing classical and bio-inspired pathfinding algorithms.

<div align="center">

**BFS • DFS • A* • Ant Colony Optimization (ACO)**

</div>

---

<div align="center">
  
## Demo

https://github.com/user-attachments/assets/62e38997-8fd3-4a8a-8e73-6a390c8cfa8c

</div>

## Features

- Interactive maze visualization using **Pygame**
- Implementations of **BFS, DFS, A*** and **ACO**
- Step-by-step algorithm animation
- Random maze generation with multiple exits
- Automated benchmarking on **100+ randomly generated mazes**
- Interactive analytics dashboard with Plotly
- Performance report generation
- Algorithm comparison based on:
  - Runtime
  - Nodes Expanded
  - Path Length
  - Search Efficiency
  - Success Rate

---

## Controls

| Key | Action |
|-----|--------|
| `1` | Run BFS (step-by-step) |
| `2` | Run DFS (step-by-step) |
| `3` | Run A* (step-by-step) |
| `4` | Run ACO (step-by-step) |
| `C` | Compare all algorithms |
| `N` | Generate new random maze |
| `W` | Toggle walls on/off |
| `R` | Reset maze |
| `Q` | Quit |

## Algorithms

| Algorithm | Optimal | Data Structure |
|-----------|:-------:|---------------|
| BFS | Optimal  | Queue |
| DFS | Not Gauranteed | Stack |
| A* | Optimal | Priority Queue |
| ACO | Heuristic | Ant Colony Optimization |

---

### Benchmark Dashboard

[Dashboard](https://navyasharma2744.github.io/MazeBench/)

---

## Benchmark Metrics

Each algorithm is evaluated on randomly generated mazes using:

- Runtime (ms)
- Nodes Expanded
- Path Length
- Search Efficiency
- Success Rate

Results are exported as:

- Interactive HTML Dashboard
- CSV Dataset
- Benchmark Summary
  
---

## Getting Started

```bash
git clone <repository-url>

cd MazeSolver

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

Run the visualizer

```bash
python main.py
```

Run benchmark

```bash
python benchmark_runner.py
```

Generate dashboard

```bash
python dashboard.py
```
---

## Project Structure

```
MazeBench/

├── algorithms.py
├── algorithms_visual.py
├── maze.py
├── visualizer.py
├── main.py

├── benchmark.py
├── benchmark_runner.py
├── metrics.py
├── dashboard.py

├── results/

└── README.md
```
---

## Tech Stack

- Python
- Pygame-ce
- Plotly
- Pandas
- Matplotlib
  
---

## Technical Blog

Read my blog post [here](https://dev.to/navya_sharma2744/i-turned-pathfinding-algorithms-into-an-interactive-game-p40)!

## Author

**Navya**


