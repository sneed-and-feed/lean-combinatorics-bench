---
license: cc0-1.0
task_categories:
  - text-generation
  - question-answering
language:
  - en
tags:
  - lean4
  - mathlib
  - formal-mathematics
  - automated-theorem-proving
  - combinatorics
  - spectral-graph-theory
  - additive-combinatorics
  - discrete-geometry
  - benchmark
pretty_name: "Lean 4 Combinatorics, Spectral Graph Theory & Additive Number Theory Benchmark"
size_categories:
  - n<1K
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-00000-of-00001.parquet
  - config_name: tiers
    data_files:
      - split: tier1_discrete_geometry_extremal
        path: data/splits/tier1_discrete_geometry_extremal.jsonl
      - split: tier2_algebraic_spectral_graph
        path: data/splits/tier2_algebraic_spectral_graph.jsonl
      - split: tier3_additive_combinatorics_zeta
        path: data/splits/tier3_additive_combinatorics_zeta.jsonl
---

# Lean 4 Combinatorics, Spectral Graph Theory & Additive Number Theory Benchmark (`lean-combinatorics-bench`)

An open-source, sovereign **Lean 4 formal mathematics benchmark dataset** comprising **95 machine-checked formalizations** (**2,687 theorem & lemma declarations**, **41,502 non-empty lines of reference proof code**, and **23,978 tactic invocations**) curated across three theorem suites (`lean-theorems-1`, `lean-theorems-2`, `lean-theorems-3`) and pinned to `leanprover/lean4:v4.34.0-rc1` (Mathlib `v4.34.0-rc1`).

Every benchmark entry provides a paired `(challenge_statement, reference_solution)` specification along with fine-grained domain classification, MSC2020/arXiv metadata, Mathlib import graphs, and proof-golf complexity metrics. All **95 / 95** reference solutions are verified free of `sorry` and `admit` tokens.

---

## Corpus Summary & Key Metrics

| Metric | Value |
| :--- | :--- |
| **Total Benchmark Problems** | **95** |
| **Proved Theorem & Lemma Declarations** | **2,687** |
| **Total Challenge Specification LOC** | **9,452** |
| **Total Reference Solution LOC** | **41,502** |
| **Mean Proof Expansion Ratio (`Solution / Challenge`)** | **4.3908x** |
| **Total Tactic Invocations** | **23,978** |
| **Zero-Sorry Verified Reference Solutions** | **95 / 95 (100%)** |
| **Pinned Toolchain** | `leanprover/lean4:v4.34.0-rc1` |
| **License** | CC0-1.0 Public Domain |

---

## Mathematical Domain Distribution

| Mathematical Category | Problems | Declarations | Challenge LOC | Solution LOC | Expansion Ratio | Tactic Steps | Zero-Sorry Verified |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Discrete & Convex Geometry** | 24 | 624 | 2,178 | 10,336 | 4.75x | 5,816 | 100% (24/24) |
| **Extremal Graph Theory** | 20 | 488 | 1,146 | 10,770 | 9.4x | 7,470 | 100% (20/20) |
| **Additive Combinatorics** | 15 | 459 | 2,095 | 4,950 | 2.36x | 2,014 | 100% (15/15) |
| **Spectral Graph Theory** | 15 | 411 | 1,444 | 6,160 | 4.27x | 3,907 | 100% (15/15) |
| **Algebraic Topology & Monodromy** | 10 | 443 | 1,463 | 4,201 | 2.87x | 1,858 | 100% (10/10) |
| **Algebraic & Enumerative Combinatorics** | 9 | 237 | 722 | 4,016 | 5.56x | 2,594 | 100% (9/9) |
| **Arithmetic Dynamics & Number Theory** | 2 | 25 | 404 | 1,069 | 2.65x | 319 | 100% (2/2) |
| **Total / Overall** | **95** | **2,687** | **9,452** | **41,502** | **4.3908x** | **23,978** | **100% (95/95)** |

---

## Source & Tier Split Architecture

### 1. Source Repository Splits
- **`lean-theorems-1` (45 problems):** Classical discrete & convex geometry (Radon, Helly, Colorful Carathéodory, Tverberg, Sarkaria tensor trick, Art Gallery, Pick, Cauchy Arm, Sylvester–Gallai, Erdős–Szekeres, de Bruijn–Erdős, Desargues), topological combinatorics (1D/2D/3D/$n$D Sperner, Tucker's Lemma, Kneser–Lovász, Combinatorial Maps, Euler Polyhedron, Poincaré Dodecahedral Space $S^3/2I$ spectral & heat kernel modules), and extremal set/graph theory (Erdős–Ko–Rado, Bollobás Two-Families, Frankl–Wilson, Hall Marriage, König Matching, Ore/Dirac, Friendship Theorem, Schur & Rado Partition Regularity).
- **`lean-theorems-2` (25 problems):** Algebraic & enumerative combinatorics (Cayley's Prüfer-code tree bijection, Lindström–Gessel–Viennot determinant lemma, MacMahon's Master Theorem, RSK bijection, Stanley $\mathfrak{sl}_2$ poset unimodality, Fisher's inequality, Birkhoff–von Neumann), graph coloring & connectivity (Brooks' Theorem via Lovász ordering, Vizing's Edge-Coloring Theorem via Kempe fans, Menger's Vertex/Edge Duality, Whitney's $k$-Connectedness, Turán's Theorem), spectral graph & zeta theory (Ihara Zeta, Ihara–Bass, Hoffman–Singleton Moore graph classification, Matrix-Tree Theorem, Circulant Spectral Theory), and geometry of numbers (Blichfeldt, Jung, Van der Waerden, Ramanujan $\tau$ congruence).
- **`lean-theorems-3` (25 problems):** Spectral expanders (Alon–Boppana Nilli bound, Discrete Cheeger Inequality, Expander Mixing Lemma, Tanner Vertex Expansion), additive combinatorics & harmonic analysis (Kelley–Meka 2023 $r_3(N)$ bound, Roth's Theorem Fourier density increment, Ruzsa–Freiman & Plünnecke–Ruzsa sumset calculus, Cauchy–Davenport, Vosper's critical pairs, Chowla's theorem, Erdős–Ginzburg–Ziv, Gilmer union-closed entropy bound), discrete geometry & counterexamples (7D Keller Cube-Tiling Bridge, Jenrich 64D Borsuk counterexample, Busemann–Petty 4D/5D Zhang audit, Hedetniemi tensor counterexample, Engel Jacobian refutation, Lonely Runner $k=8$, Erdős–Gyárfás), and algebraic topology/monodromy (Brieskorn exotic 7-spheres, $SU(2)$ character varieties & Casson invariant, Orbifold Spectral Zeta, Picard–Fuchs mirror monodromy, Deligne Universal Monodromy Weight Filtration).

### 2. Curriculum Tier Splits (`data/splits/`)
- **`tier1_discrete_geometry_extremal.jsonl` (44 problems):** Discrete & Convex Geometry (24) + Extremal Graph Theory (20).
- **`tier2_algebraic_spectral_graph.jsonl` (24 problems):** Spectral Graph Theory (15) + Algebraic & Enumerative Combinatorics (9).
- **`tier3_additive_combinatorics_zeta.jsonl` (27 problems):** Additive Combinatorics (15) + Algebraic Topology & Monodromy (10) + Arithmetic Dynamics & Number Theory (2).

---

## Flagship Multi-File & High-Depth Formalizations (Top 15 by Proof LOC)

| Problem ID | Title | Domain | Split | Challenge LOC | Solution LOC | Ratio | Tactics |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `cayleys_formula` | Cayley's Tree Formula and Prüfer Sequence Bijection | Algebraic & Enumerative Combinatorics | `lean-theorems-2` | 55 | 1673 | 30.4182x | 1219 |
| `schurs_theorem` | Schur's Theorem in Additive Combinatorics and Group Theory | Additive Combinatorics | `lean-theorems-1` | 130 | 1515 | 11.6538x | 664 |
| `mengers_theorem` | Menger's Theorem and Whitney's Connectivity Duality | Extremal Graph Theory | `lean-theorems-2` | 112 | 1513 | 13.5089x | 982 |
| `whitney_two_connected` | Whitney's k-Connectedness Theorem via Internally Disjoint Menger Paths | Extremal Graph Theory | `lean-theorems-2` | 30 | 1439 | 47.9667x | 982 |
| `brooks_theorem` | Brooks' Theorem on Graph Colorings and Lovász Orderings | Extremal Graph Theory | `lean-theorems-2` | 78 | 1280 | 16.4103x | 1056 |
| `vizings_theorem` | Vizing's Theorem on Edge Colorings & König's Line Coloring Theorem | Extremal Graph Theory | `lean-theorems-2` | 62 | 1260 | 20.3226x | 1043 |
| `erdos_szekeres_convex` | The Happy Ending Theorem (Erdős–Szekeres Convex Polygon Theorem, 1935) | Discrete & Convex Geometry | `lean-theorems-1` | 32 | 1168 | 36.5x | 1104 |
| `friendship_theorem` | The Friendship Theorem on Graphs with Unique Common Neighbors | Spectral Graph Theory | `lean-theorems-1` | 17 | 1068 | 62.8235x | 832 |
| `tuckers_lemma` | Tucker's Lemma: Full Combinatorial & Topological Parity Suite in 1D and 2D | Algebraic Topology & Monodromy | `lean-theorems-1` | 220 | 1036 | 4.7091x | 528 |
| `poincare_adelic_standard_model` | Adelic Spectral Action and Fermion Quantum Number Representation over S^3/2I | Arithmetic Dynamics & Number Theory | `lean-theorems-1` | 338 | 990 | 2.929x | 297 |
| `desargues_theorem` | Desargues's Theorem and Synthetic Projective Equivalence | Discrete & Convex Geometry | `lean-theorems-1` | 135 | 966 | 7.1556x | 492 |
| `colorful_caratheodory` | Bárány's Colorful Carathéodory Theorem, Selection Lemmas, and Centerpoint Theorem | Discrete & Convex Geometry | `lean-theorems-1` | 83 | 918 | 11.0602x | 489 |
| `tverbergs_theorem` | Tverberg's Partition Theorem, 1D Theorem, and Colorful 1D Theorem | Discrete & Convex Geometry | `lean-theorems-1` | 40 | 917 | 22.925x | 651 |
| `erdos_ko_rado` | The Erdős–Ko–Rado Theorem and Hilton–Milner Extremizer | Extremal Graph Theory | `lean-theorems-1` | 33 | 893 | 27.0606x | 620 |
| `hoffman_singleton` | The Hoffman–Singleton Moore Graph Classification Theorem | Spectral Graph Theory | `lean-theorems-2` | 116 | 737 | 6.3534x | 501 |

---

## Repository Structure

```text
lean-combinatorics-bench/
├── README.md                                        # Dataset card, domain tables & documentation
├── codemeta.json                                    # CodeMeta 2.0 scientific software metadata
├── dataset_loading_script.py                        # HuggingFace datasets + standalone Python loader
├── scripts/
│   ├── build_benchmark.py                           # Deterministic extraction & metrics pipeline
│   └── build_docs_and_readme.py                     # Generator for docs/index.html and README.md
├── data/
│   ├── benchmark.jsonl                              # Complete 95-problem structured JSONL dataset
│   ├── benchmark_summary.csv                        # Tabular summary of all 95 problems & metrics
│   ├── benchmark_stats.json                         # Aggregate corpus statistics
│   ├── train-00000-of-00001.parquet                 # HuggingFace Parquet export
│   └── splits/
│       ├── tier1_discrete_geometry_extremal.jsonl   # Tier 1 split (44 problems)
│       ├── tier2_algebraic_spectral_graph.jsonl     # Tier 2 split (24 problems)
│       └── tier3_additive_combinatorics_zeta.jsonl  # Tier 3 split (27 problems)
├── eval/
│   ├── evaluate_submissions.py                      # Static soundness & single-threaded Lean 4 evaluator
│   └── latest_eval_report.json                      # Latest evaluation audit report (95/95 verified)
└── docs/
    └── index.html                                   # Standalone Interactive Benchmark Explorer
```

---

## Quickstart Usage

### 1. Loading the Benchmark in Python

```python
from dataset_loading_script import load_benchmark

# Load all 95 benchmark entries
problems = load_benchmark(split="all")
print(f"Loaded {len(problems)} problems")

# Filter by mathematical domain or tier split
spectral = load_benchmark(split="tier2", category="Spectral Graph Theory")
for p in spectral[:3]:
    print(p["problem_id"], "->", p["metrics"]["solution_loc"], "LOC")
```

Or with HuggingFace `datasets` / `pandas`:

```python
import pandas as pd

df = pd.read_parquet("data/train-00000-of-00001.parquet")
print(df[["problem_id", "category", "challenge_loc", "solution_loc", "tactic_count"]].head())
```

### 2. Running the Evaluation Harness

Audit all 95 reference solutions for syntactic integrity, forbidden axioms, declaration parity, and zero-sorry compliance:

```bash
python eval/evaluate_submissions.py --verify-reference
```

Evaluate a model's candidate solutions (`.jsonl` or directory of `<problem_id>.lean` files) with optional single-threaded `lake env lean` kernel verification and memory/timeout caps:

```bash
python eval/evaluate_submissions.py \
  --submissions path/to/model_predictions.jsonl \
  --run-lean \
  --timeout-sec 120 \
  --memory-mb 4096
```

### 3. Interactive Benchmark Explorer

Open `docs/index.html` directly in any browser (or serve via GitHub Pages) to explore all 95 problems with real-time search, domain/tier filtering, proof-golf expansion scatter plots, and side-by-side syntax-highlighted `Challenge.lean` vs. `Solution.lean` comparison.

---

## Citation

```bibtex
@misc{cohen2026leancombinatoricsbench,
  title        = {Lean 4 Combinatorics, Spectral Graph Theory \& Additive Number Theory Benchmark},
  author       = {Cohen, Noah},
  year         = {2026},
  howpublished = {\url{https://github.com/sneed-and-feed/lean-combinatorics-bench}},
  note         = {95 machine-checked formalizations in Lean 4 (v4.34.0-rc1 / Mathlib)}
}
```
