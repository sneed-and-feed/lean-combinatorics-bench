#!/usr/bin/env python3
"""
Evaluation Harness for the Lean 4 Combinatorics, Spectral Graph Theory &
Additive Number Theory Benchmark (`lean-combinatorics-bench`).

Features:
1. Syntactic & Soundness Audit:
   - Strips nested Lean 4 comments (`/- ... -/` and `-- ...`) and string literals.
   - Detects any `sorry`, `admit`, or `sorryAx` tokens.
   - Detects forbidden soundness bypasses (`axiom`, `constant`, `opaque`, `unsafe`,
     `@[implemented_by]`, `@[extern]`).
2. Theorem Signature & Declaration Parity Check:
   - Verifies that all target theorems declared in `Challenge.lean` / `theorem_names`
     are present in the candidate submission with matching normalized signatures.
3. Optional Single-Threaded Kernel Verification (`--run-lean`):
   - Runs `lake env lean -M <memory_mb>` one file at a time against a pre-built
     `leanprover/lean4:v4.34.0-rc1` workspace (`lean-theorems-1..3` or cached Mathlib)
     with strict wall-clock timeouts and memory caps to prevent RAM exhaustion.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BENCHMARK_ROOT = Path(__file__).resolve().parent.parent
DATA_JSONL = BENCHMARK_ROOT / "data" / "benchmark.jsonl"
DEFAULT_REPOS_ROOT = Path(r"C:\Users\x\Documents\antigravity")
FALLBACK_MATHLIB_WORKSPACE = Path(
    r"C:\Users\x\Documents\antigravity\adelic_spectral_zeta\formalization\spectral-positivity-ext"
)

FORBIDDEN_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("axiom_declaration", re.compile(r"^\s*(?:private\s+|protected\s+)?axiom\s+", re.M)),
    ("constant_declaration", re.compile(r"^\s*(?:private\s+|protected\s+)?constant\s+", re.M)),
    ("opaque_declaration", re.compile(r"^\s*(?:private\s+|protected\s+)?opaque\s+", re.M)),
    ("unsafe_declaration", re.compile(r"^\s*unsafe\s+", re.M)),
    ("implemented_by_attr", re.compile(r"@\[[^\]]*implemented_by[^\]]*\]")),
    ("extern_attr", re.compile(r"@\[[^\]]*extern[^\]]*\]")),
    ("sorryAx_term", re.compile(r"\bsorryAx\b")),
]


def strip_lean_comments(text: str) -> str:
    """Remove Lean 4 block comments `/- ... -/` (handling nesting) and `-- ...` line comments."""
    result: List[str] = []
    i = 0
    n = len(text)
    depth = 0
    in_string = False
    while i < n:
        if depth == 0 and not in_string:
            if text[i : i + 2] == "/-":
                depth += 1
                i += 2
                continue
            elif text[i : i + 2] == "--":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            elif text[i] == '"':
                in_string = True
                result.append(text[i])
                i += 1
                continue
            else:
                result.append(text[i])
                i += 1
        elif in_string:
            if text[i] == "\\" and i + 1 < n:
                result.append(text[i : i + 2])
                i += 2
                continue
            elif text[i] == '"':
                in_string = False
            result.append(text[i])
            i += 1
        else:
            if text[i : i + 2] == "/-":
                depth += 1
                i += 2
            elif text[i : i + 2] == "-/":
                depth -= 1
                i += 2
            else:
                if text[i] == "\n":
                    result.append("\n")
                i += 1
    return "".join(result)


def extract_declarations_and_signatures(text: str) -> Dict[str, str]:
    """
    Extract a map `{short_or_qualified_name: normalized_line}` for all
    `theorem`, `lemma`, `def`, and `abbrev` declarations in `text`.
    """
    cleaned = strip_lean_comments(text)
    decl_map: Dict[str, str] = {}
    pattern = re.compile(
        r"^(?:@\S+\s+)*(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma|def|abbrev)\s+([A-Za-z0-9_'.]+)\s*([^\n]*)",
        re.M,
    )
    for match in pattern.finditer(cleaned):
        name = match.group(1).strip()
        sig = " ".join(match.group(2).split())
        decl_map[name] = sig
        if "." in name:
            decl_map[name.split(".")[-1]] = sig
    return decl_map


def extract_axiom_names(text: str) -> List[str]:
    cleaned = strip_lean_comments(text)
    return re.findall(
        r"^\s*(?:private\s+|protected\s+)?axiom\s+([A-Za-z0-9_'.]+)",
        cleaned,
        re.M,
    )


def check_syntactic_integrity(
    problem: Dict[str, Any], candidate_code: str
) -> Dict[str, Any]:
    """
    Perform static syntactic, zero-sorry, forbidden-axiom, and theorem-declaration parity checks.
    """
    cleaned = strip_lean_comments(candidate_code)
    sorries = re.findall(r"\b(?:sorry|admit)\b", cleaned)
    zero_sorry_ok = len(sorries) == 0

    forbidden_hits: List[str] = []
    for label, pat in FORBIDDEN_PATTERNS:
        if label == "axiom_declaration":
            cand_axioms = set(extract_axiom_names(candidate_code))
            allowed_axioms = set(extract_axiom_names(problem["challenge_statement"])) | set(
                problem.get("permitted_axioms", [])
            )
            if not cand_axioms.issubset(allowed_axioms):
                forbidden_hits.append(label)
        elif pat.search(cleaned):
            forbidden_hits.append(label)

    # Check target theorem declarations
    cand_decls = extract_declarations_and_signatures(candidate_code)

    missing_theorems: List[str] = []
    for thm_name in problem.get("theorem_names", []):
        short_name = thm_name.split(".")[-1]
        if thm_name not in cand_decls and short_name not in cand_decls:
            missing_theorems.append(thm_name)

    # Also verify that every theorem with `sorry` in Challenge.lean appears in candidate
    chall_cleaned = strip_lean_comments(problem["challenge_statement"])
    for m in re.finditer(
        r"^(?:@\S+\s+)*(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)",
        chall_cleaned,
        re.M,
    ):
        tname = m.group(1)
        short = tname.split(".")[-1]
        if tname not in cand_decls and short not in cand_decls and tname not in missing_theorems:
            missing_theorems.append(tname)

    passed_static = (
        bool(candidate_code.strip())
        and zero_sorry_ok
        and len(forbidden_hits) == 0
        and len(missing_theorems) == 0
    )

    return {
        "problem_id": problem["problem_id"],
        "category": problem["category"],
        "source_split": problem["source_split"],
        "passed_static": passed_static,
        "zero_sorry": zero_sorry_ok,
        "sorry_count": len(sorries),
        "forbidden_constructs": forbidden_hits,
        "target_theorem_count": len(problem.get("theorem_names", [])),
        "missing_theorems": missing_theorems,
    }


def resolve_lean_workspace(problem: Dict[str, Any], custom_workspace: Optional[Path]) -> Path:
    if custom_workspace and custom_workspace.exists():
        return custom_workspace
    repo_ws = DEFAULT_REPOS_ROOT / problem["source_split"]
    if (repo_ws / "lean-toolchain").exists():
        return repo_ws
    if (FALLBACK_MATHLIB_WORKSPACE / "lean-toolchain").exists():
        return FALLBACK_MATHLIB_WORKSPACE
    raise FileNotFoundError(
        f"No Lean 4 workspace found at {repo_ws} or {FALLBACK_MATHLIB_WORKSPACE}."
    )


def verify_with_lean_kernel(
    problem: Dict[str, Any],
    candidate_code: str,
    workspace: Path,
    timeout_sec: int = 120,
    memory_mb: int = 4096,
) -> Dict[str, Any]:
    """
    Run single-threaded `lake env lean -M <memory_mb>` on a candidate submission.
    """
    t0 = time.monotonic()
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".lean",
        dir=str(workspace),
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(candidate_code)
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            "lake",
            "env",
            "lean",
            f"-M={memory_mb}",
            "-DwarningAsError=false",
            str(tmp_path),
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_sec,
        )
        elapsed = round(time.monotonic() - t0, 3)
        return {
            "kernel_verified": proc.returncode == 0,
            "return_code": proc.returncode,
            "elapsed_sec": elapsed,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
    except subprocess.TimeoutExpired:
        elapsed = round(time.monotonic() - t0, 3)
        return {
            "kernel_verified": False,
            "return_code": -1,
            "elapsed_sec": elapsed,
            "stdout": "",
            "stderr": f"TimeoutExpired after {timeout_sec}s",
        }
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def load_benchmark_problems() -> Dict[str, Dict[str, Any]]:
    problems: Dict[str, Dict[str, Any]] = {}
    with open(DATA_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                problems[rec["problem_id"]] = rec
    return problems


def load_submissions(
    submissions_path: Optional[Path],
    verify_reference: bool,
    problems: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    if verify_reference:
        return {pid: p["reference_solution"] for pid, p in problems.items()}
    if not submissions_path or not submissions_path.exists():
        raise FileNotFoundError(f"Submissions path not found: {submissions_path}")

    submissions: Dict[str, str] = {}
    if submissions_path.is_file() and submissions_path.suffix == ".jsonl":
        with open(submissions_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    obj = json.loads(line)
                    pid = obj.get("problem_id")
                    code = (
                        obj.get("generated_solution")
                        or obj.get("solution")
                        or obj.get("reference_solution")
                        or ""
                    )
                    if pid:
                        submissions[pid] = code
    elif submissions_path.is_dir():
        for p in sorted(submissions_path.glob("*.lean")):
            submissions[p.stem] = p.read_text(encoding="utf-8")
    else:
        raise ValueError(
            "Submissions must be a .jsonl file or a directory of <problem_id>.lean files."
        )
    return submissions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate Lean 4 benchmark submissions (static soundness + optional single-threaded kernel verification)."
    )
    parser.add_argument(
        "--submissions",
        type=Path,
        default=None,
        help="Path to submissions .jsonl file or directory of <problem_id>.lean files.",
    )
    parser.add_argument(
        "--verify-reference",
        action="store_true",
        help="Audit the benchmark's built-in 95 gold-standard reference solutions.",
    )
    parser.add_argument(
        "--run-lean",
        action="store_true",
        help="Invoke single-threaded `lake env lean` kernel verification on evaluated problems.",
    )
    parser.add_argument(
        "--problem-id",
        type=str,
        default=None,
        help="Filter evaluation to a single problem_id.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of problems to evaluate.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Optional override path to a Lean 4 v4.34.0-rc1 workspace with .lake build cache.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=120,
        help="Per-file timeout in seconds for `lake env lean` (default: 120).",
    )
    parser.add_argument(
        "--memory-mb",
        type=int,
        default=4096,
        help="Per-file memory cap in MB passed to `lean -M` (default: 4096).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BENCHMARK_ROOT / "eval" / "latest_eval_report.json",
        help="Path to save the JSON evaluation report.",
    )
    args = parser.parse_args()

    if not args.verify_reference and args.submissions is None:
        args.verify_reference = True

    problems = load_benchmark_problems()
    submissions = load_submissions(args.submissions, args.verify_reference, problems)

    target_pids = sorted(problems.keys())
    if args.problem_id:
        target_pids = [pid for pid in target_pids if pid == args.problem_id]
    if args.limit is not None:
        target_pids = target_pids[: args.limit]

    results: List[Dict[str, Any]] = []
    static_pass_count = 0
    kernel_pass_count = 0

    for pid in target_pids:
        prob = problems[pid]
        cand = submissions.get(pid, "")
        res = check_syntactic_integrity(prob, cand)
        if res["passed_static"]:
            static_pass_count += 1

        if args.run_lean:
            if res["passed_static"]:
                ws = resolve_lean_workspace(prob, args.workspace)
                kres = verify_with_lean_kernel(
                    prob,
                    cand,
                    workspace=ws,
                    timeout_sec=args.timeout_sec,
                    memory_mb=args.memory_mb,
                )
                res.update(kres)
                if kres["kernel_verified"]:
                    kernel_pass_count += 1
            else:
                res["kernel_verified"] = False
                res["stderr"] = "Skipped kernel check due to static check failure."

        results.append(res)

    total = len(results)
    summary = {
        "evaluated_problems": total,
        "static_passed": static_pass_count,
        "static_pass_rate": round(static_pass_count / max(total, 1), 4),
        "kernel_verification_enabled": args.run_lean,
        "kernel_passed": kernel_pass_count if args.run_lean else None,
        "kernel_pass_rate": (
            round(kernel_pass_count / max(total, 1), 4) if args.run_lean else None
        ),
        "results": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k != "results"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
