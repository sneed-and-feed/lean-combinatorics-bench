#!/usr/bin/env python3
"""
HuggingFace `datasets`-compatible loading script and standalone loader API for
the Lean 4 Combinatorics, Spectral Graph Theory & Additive Number Theory Benchmark
(`lean-combinatorics-bench`).

Can be used either via HuggingFace `datasets` or imported directly as a zero-dependency
Python module:
    from dataset_loading_script import load_benchmark
    records = load_benchmark(split="all")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

BENCHMARK_ROOT = Path(__file__).resolve().parent
DATA_DIR = BENCHMARK_ROOT / "data"

SPLIT_FILES = {
    "all": DATA_DIR / "benchmark.jsonl",
    "train": DATA_DIR / "benchmark.jsonl",
    "tier1": DATA_DIR / "splits" / "tier1_discrete_geometry_extremal.jsonl",
    "tier2": DATA_DIR / "splits" / "tier2_algebraic_spectral_graph.jsonl",
    "tier3": DATA_DIR / "splits" / "tier3_additive_combinatorics_zeta.jsonl",
}


def load_benchmark(
    split: str = "all",
    category: Optional[str] = None,
    source_split: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Load benchmark records with optional split, category, or source repository filtering."""
    if split not in SPLIT_FILES:
        raise ValueError(f"Unknown split '{split}'. Valid splits: {list(SPLIT_FILES.keys())}")
    path = SPLIT_FILES[split]
    records: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if category and rec.get("category") != category:
                continue
            if source_split and rec.get("source_split") != source_split:
                continue
            records.append(rec)
    return records


def iter_benchmark(split: str = "all") -> Iterator[Dict[str, Any]]:
    """Stream benchmark records lazily from JSONL."""
    for rec in load_benchmark(split=split):
        yield rec


# Optional HuggingFace `datasets.GeneratorBasedBuilder` integration if `datasets` is installed
try:
    import datasets  # type: ignore

    _DESCRIPTION = (
        "Lean 4 Combinatorics, Spectral Graph Theory & Additive Number Theory Benchmark: "
        "95 machine-checked formalizations across extremal combinatorics, discrete geometry, "
        "spectral graph theory, additive number theory, and algebraic topology."
    )

    class LeanCombinatoricsBench(datasets.GeneratorBasedBuilder):  # type: ignore
        VERSION = datasets.Version("1.0.0")

        def _info(self) -> datasets.DatasetInfo:
            features = datasets.Features(
                {
                    "problem_id": datasets.Value("string"),
                    "title": datasets.Value("string"),
                    "source_split": datasets.Value("string"),
                    "source_type": datasets.Value("string"),
                    "source_path": datasets.Value("string"),
                    "category": datasets.Value("string"),
                    "tier_split": datasets.Value("string"),
                    "description": datasets.Value("string"),
                    "arxiv_classes": datasets.Sequence(datasets.Value("string")),
                    "msc2020": datasets.Sequence(datasets.Value("string")),
                    "lean_toolchain": datasets.Value("string"),
                    "permitted_axioms": datasets.Sequence(datasets.Value("string")),
                    "theorem_names": datasets.Sequence(datasets.Value("string")),
                    "imports": datasets.Sequence(datasets.Value("string")),
                    "challenge_statement": datasets.Value("string"),
                    "reference_solution": datasets.Value("string"),
                    "metrics": {
                        "challenge_loc": datasets.Value("int32"),
                        "solution_loc": datasets.Value("int32"),
                        "proof_expansion_ratio": datasets.Value("float64"),
                        "tactic_count": datasets.Value("int32"),
                        "zero_sorry_verified": datasets.Value("bool"),
                        "multi_file_modules": {
                            "count": datasets.Value("int32"),
                            "names": datasets.Sequence(datasets.Value("string")),
                        },
                    },
                }
            )
            return datasets.DatasetInfo(
                description=_DESCRIPTION,
                features=features,
                supervised_keys=("challenge_statement", "reference_solution"),
                license="CC0-1.0",
            )

        def _split_generators(self, dl_manager: Any) -> List[Any]:
            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={"filepath": str(SPLIT_FILES["train"])},
                ),
                datasets.SplitGenerator(
                    name="tier1_discrete_geometry_extremal",
                    gen_kwargs={"filepath": str(SPLIT_FILES["tier1"])},
                ),
                datasets.SplitGenerator(
                    name="tier2_algebraic_spectral_graph",
                    gen_kwargs={"filepath": str(SPLIT_FILES["tier2"])},
                ),
                datasets.SplitGenerator(
                    name="tier3_additive_combinatorics_zeta",
                    gen_kwargs={"filepath": str(SPLIT_FILES["tier3"])},
                ),
            ]

        def _generate_examples(self, filepath: str) -> Iterator[ Any ]:
            with open(filepath, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    if line.strip():
                        yield idx, json.loads(line)

except ImportError:
    pass


if __name__ == "__main__":
    all_recs = load_benchmark("all")
    print(f"Loaded {len(all_recs)} benchmark theorems from {SPLIT_FILES['all'].name}.")
    for tier in ("tier1", "tier2", "tier3"):
        print(f"  Split '{tier}': {len(load_benchmark(tier))} theorems")
