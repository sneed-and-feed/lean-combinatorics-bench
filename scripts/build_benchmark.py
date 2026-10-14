#!/usr/bin/env python3
"""
Deterministic Extraction & Analysis Pipeline for the Lean 4 Combinatorics,
Spectral Graph Theory & Additive Number Theory Benchmark Dataset.

Scans read-only theorem repositories (`lean-theorems-1`, `lean-theorems-2`, `lean-theorems-3`)
and extracts all 95 formalized theorem entries (both from `palomar/<slug>/` and standalone
`Formalization/` multi-file theorem modules), computing LOC, proof expansion ratios,
tactic counts, Mathlib import graphs, and zero-sorry verification audits.
"""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

BASE_REPOS_DIR = Path(r"C:\Users\x\Documents\antigravity")
BENCHMARK_ROOT = Path(r"C:\Users\x\Documents\antigravity\lean-combinatorics-bench")
REPOS = ["lean-theorems-1", "lean-theorems-2", "lean-theorems-3"]

# Map from palomar slug (in repo 1 / 2 / 3) to Formalization PascalCase module name & optional subdir
SLUG_TO_FORMALIZATION: Dict[Tuple[str, str], Tuple[Optional[str], Optional[str]]] = {
    # lean-theorems-1 (36)
    ("lean-theorems-1", "art_gallery_theorem"): ("ArtGalleryTheorem", None),
    ("lean-theorems-1", "becks_theorem"): ("BecksTheorem", None),
    ("lean-theorems-1", "bollobas_two_families"): ("BollobasTwoFamilies", None),
    ("lean-theorems-1", "bondy_induced_subsets"): ("BondyInducedSubsets", None),
    ("lean-theorems-1", "cauchy_arm_lemma"): ("CauchyArmLemma", None),
    ("lean-theorems-1", "colorful_caratheodory"): ("ColorfulCaratheodory", "ColorfulCaratheodory"),
    ("lean-theorems-1", "colorful_helly"): ("ColorfulHelly", None),
    ("lean-theorems-1", "crossing_lemma"): ("CrossingLemma", None),
    ("lean-theorems-1", "de_bruijn_erdos"): ("DeBruijnErdos", None),
    ("lean-theorems-1", "desargues_theorem"): ("DesarguesVector", None),
    ("lean-theorems-1", "descartes_rule_of_signs"): ("DescartesSigns", None),
    ("lean-theorems-1", "dilworth_mirsky"): ("DilworthTheorem", None),
    ("lean-theorems-1", "elekes_sum_product"): ("ElekesSumProduct", None),
    ("lean-theorems-1", "erdos_ko_rado"): ("ErdosKoRado", None),
    ("lean-theorems-1", "erdos_szekeres_convex"): ("ErdosSzekeresConvex", "ErdosSzekeresConvex"),
    ("lean-theorems-1", "erdos_unit_distances"): ("ErdosUnitDistances", None),
    ("lean-theorems-1", "euler_polyhedron"): ("EulerPolyhedron", "CombinatorialMap"),
    ("lean-theorems-1", "frankl_wilson"): ("FranklWilson", None),
    ("lean-theorems-1", "friendship_theorem"): ("FriendshipTheorem", "FriendshipTheorem"),
    ("lean-theorems-1", "friendship_windmill"): ("FriendshipWindmill", None),
    ("lean-theorems-1", "graham_pollak"): ("GrahamPollak", None),
    ("lean-theorems-1", "hall_marriage"): ("HallMarriage", None),
    ("lean-theorems-1", "kneser_lovasz"): ("KneserLovasz", None),
    ("lean-theorems-1", "konig_matching"): ("KonigMatching", "KonigMatching"),
    ("lean-theorems-1", "ore_dirac_hamiltonian"): ("OreHamiltonian", None),
    ("lean-theorems-1", "picks_theorem"): ("PicksTheorem", None),
    ("lean-theorems-1", "radon_helly"): ("RadonHelly", None),
    ("lean-theorems-1", "schurs_theorem"): ("SchursTheorem", "SchursTheorem"),
    ("lean-theorems-1", "sperner_3d"): ("Sperner3D", None),
    ("lean-theorems-1", "sperner_nd"): ("SpernerND", None),
    ("lean-theorems-1", "sperners_lemma"): ("SpernersLemma", None),
    ("lean-theorems-1", "sylvester_gallai"): ("SylvesterGallai", None),
    ("lean-theorems-1", "szemeredi_trotter"): ("SzemerediTrotter", None),
    ("lean-theorems-1", "tuckers_lemma"): ("TuckersLemma", "TuckersLemma"),
    ("lean-theorems-1", "tutte_one_factor"): ("TutteOneFactor", None),
    ("lean-theorems-1", "tverbergs_theorem"): ("TverbergsTheorem", "TverbergsTheorem"),
    # lean-theorems-2 (24)
    ("lean-theorems-2", "birkhoff_von_neumann"): ("BirkhoffVonNeumann", None),
    ("lean-theorems-2", "blichfeldts_theorem"): ("BlichfeldtsTheorem", None),
    ("lean-theorems-2", "brooks_theorem"): ("BrooksTheorem", "BrooksTheorem"),
    ("lean-theorems-2", "cayleys_formula"): ("CayleysFormula", "CayleysFormula"),
    ("lean-theorems-2", "circulant_spectral_theory"): ("CirculantSpectralTheory", None),
    ("lean-theorems-2", "cyclic_shift"): ("CyclicShift", None),
    ("lean-theorems-2", "fishers_inequality"): ("FishersInequality", None),
    ("lean-theorems-2", "gessel_viennot"): ("GesselViennot", None),
    ("lean-theorems-2", "hoffman_singleton"): ("HoffmanSingleton", None),
    ("lean-theorems-2", "ihara_bass"): ("IharaBass", None),
    ("lean-theorems-2", "ihara_zeta"): ("IharaZeta", None),
    ("lean-theorems-2", "jungs_theorem"): ("JungsTheorem", None),
    ("lean-theorems-2", "konig_matching"): ("KonigMatching", None),
    ("lean-theorems-2", "macmahons_master_theorem"): ("MacMahonsMasterTheorem", None),
    ("lean-theorems-2", "matrix_tree_theorem"): ("MatrixTreeTheorem", None),
    ("lean-theorems-2", "mengers_theorem"): ("MengersTheorem", "MengersTheorem"),
    ("lean-theorems-2", "prefix_sparsity"): ("PrefixSparsity", None),
    ("lean-theorems-2", "ramanujan_tau"): ("RamanujanTau", None),
    ("lean-theorems-2", "rsk_bijection"): ("RSKBijection", None),
    ("lean-theorems-2", "sperner_antichain"): ("SpernerAntichain", None),
    ("lean-theorems-2", "stanley_sl2"): ("StanleySL2", None),
    ("lean-theorems-2", "turans_theorem"): ("TuransTheorem", None),
    ("lean-theorems-2", "van_der_waerden"): ("VanDerWaerden", None),
    ("lean-theorems-2", "vizings_theorem"): ("VizingsTheorem", "VizingsTheorem"),
    # lean-theorems-3 (22)
    ("lean-theorems-3", "alon_boppana"): ("AlonBoppana", "AlonBoppana"),
    ("lean-theorems-3", "brieskorn_manifolds"): ("BrieskornManifolds", None),
    ("lean-theorems-3", "brieskorn_su2_character_variety"): ("BrieskornSU2CharacterVariety", None),
    ("lean-theorems-3", "busemann_petty_zhang_audit"): (None, None),
    ("lean-theorems-3", "cauchy_davenport"): ("CauchyDavenport", "CauchyDavenport"),
    ("lean-theorems-3", "discrete_cheeger"): ("DiscreteCheeger", None),
    ("lean-theorems-3", "engel_jacobian_refutation"): (None, None),
    ("lean-theorems-3", "erdos_gyarfas"): ("ErdosGyarfas", None),
    ("lean-theorems-3", "expander_mixing"): ("ExpanderMixing", None),
    ("lean-theorems-3", "gilmer_union_closed"): ("GilmerUnionClosed", None),
    ("lean-theorems-3", "hedetniemi_counterexample"): (None, None),
    ("lean-theorems-3", "jenrich_borsuk_64"): ("JenrichBorsuk64", None),
    ("lean-theorems-3", "keller_cube_tiling_bridge"): ("KellerCubeTilingBridge", None),
    ("lean-theorems-3", "kelley_meka"): ("KelleyMeka", None),
    ("lean-theorems-3", "lonely_runner_8"): ("LonelyRunner8", None),
    ("lean-theorems-3", "orbifold_spectral_zeta"): ("OrbifoldSpectralZeta", None),
    ("lean-theorems-3", "picard_fuchs_mirror_monodromy"): ("PicardFuchsMirrorMonodromy", None),
    ("lean-theorems-3", "roths_theorem"): ("RothsTheorem", "RothsTheorem"),
    ("lean-theorems-3", "ruzsa_freiman"): ("RuzsaFreiman", "RuzsaFreiman"),
    ("lean-theorems-3", "szemeredi_regularity"): ("SzemerediRegularity", "SzemerediRegularity"),
    ("lean-theorems-3", "tanner_expansion"): ("TannerExpansion", None),
    ("lean-theorems-3", "universal_monodromy_weight_filtration"): ("UniversalMonodromyWeightFiltration", None),
}

# 13 standalone / sub-package theorem formalization modules in Formalization/
STANDALONE_FORMALIZATION_MODULES: List[Dict[str, Any]] = [
    {
        "problem_id": "poincare_binary_icosahedral",
        "title": "Binary Icosahedral Group 2I in H^x and Hurwitz Quaternion Units",
        "source_split": "lean-theorems-1",
        "category": "Algebraic Topology & Monodromy",
        "rel_path": "Formalization/PoincareDodecahedron/UniverseAdelic/BinaryIcosahedral.lean",
        "supporting_dir": None,
        "arxiv": ["math.GT", "math.GR", "math.RT"],
        "msc2020": ["20G20", "57M60", "11R52"],
        "description": (
            "Formalization of the binary icosahedral group 2I of order 120 inside the unit quaternions, "
            "golden ratio identities, 24 Hurwitz quaternion units, and 96 icosahedral elements."
        ),
    },
    {
        "problem_id": "poincare_spectral_decomposition",
        "title": "Ikeda Spectral Multiplicity Decomposition of the Poincare Dodecahedral Space S^3/2I",
        "source_split": "lean-theorems-1",
        "category": "Spectral Graph Theory",
        "rel_path": "Formalization/PoincareDodecahedron/UniverseAdelic/SpectralDecomposition.lean",
        "supporting_dir": None,
        "arxiv": ["math.SP", "math.DG", "math.GT"],
        "msc2020": ["58J50", "53C20", "20C15"],
        "description": (
            "Formalizes Ikeda's (1995) spectral multiplicity formula on the Poincare dodecahedral homology "
            "3-sphere S^3/2I, proving vanishing of low harmonic modes and multiplicity 6 at k = 12."
        ),
    },
    {
        "problem_id": "poincare_heat_kernel_asymptotics",
        "title": "Weyl Heat Kernel Asymptotics and Seeley-DeWitt Coefficients on S^3/2I",
        "source_split": "lean-theorems-1",
        "category": "Spectral Graph Theory",
        "rel_path": "Formalization/PoincareDodecahedron/UniverseAdelic/HeatKernelAsymptotics.lean",
        "supporting_dir": None,
        "arxiv": ["math.SP", "math.DG", "math-ph"],
        "msc2020": ["58J35", "58J50", "53C21"],
        "description": (
            "Formalizes the volume Vol(S^3/2I) = pi^2/60, scalar curvature R = 6, and Seeley-DeWitt "
            "heat kernel asymptotic coefficients a_0, a_1, a_2 on the Poincare dodecahedral space."
        ),
    },
    {
        "problem_id": "poincare_adelic_standard_model",
        "title": "Adelic Spectral Action and Fermion Quantum Number Representation over S^3/2I",
        "source_split": "lean-theorems-1",
        "category": "Algebraic Topology & Monodromy",
        "rel_path": "Formalization/PoincareDodecahedron/UniverseAdelic/StandardModel.lean",
        "supporting_dir": "PoincareDodecahedron/UniverseAdelic",
        "arxiv": ["math-ph", "math.QA", "hep-th"],
        "msc2020": ["58B34", "81V22", "20C35"],
        "description": (
            "Formalizes the finite noncommutative geometry Hilbert space H_F = C^96 (3 generations x 32 "
            "fermionic degrees of freedom), hypercharge tracelessness, and anomaly cancellation identities."
        ),
    },
    {
        "problem_id": "combinatorial_map_genus_obstructions",
        "title": "Tutte Combinatorial Map Rotation Systems and Topological Genus Obstructions",
        "source_split": "lean-theorems-1",
        "category": "Discrete & Convex Geometry",
        "rel_path": "Formalization/CombinatorialMap/Obstructions.lean",
        "supporting_dir": "CombinatorialMap",
        "arxiv": ["math.CO", "math.GT"],
        "msc2020": ["05C10", "57M15", "52B05"],
        "description": (
            "Formalizes permutation-triple combinatorial maps (sigma, alpha, phi) with sigma * alpha * phi = 1, "
            "Euler characteristic parity, face handshaking bounds, and non-planarity of K_5 and K_{3,3}."
        ),
    },
    {
        "problem_id": "rado_partition_regularity",
        "title": "Rado's Single-Equation Partition Regularity Theorem and Columns Condition",
        "source_split": "lean-theorems-1",
        "category": "Additive Combinatorics",
        "rel_path": "Formalization/SchursTheorem/Rado.lean",
        "supporting_dir": None,
        "arxiv": ["math.CO", "math.NT"],
        "msc2020": ["05D10", "11B75"],
        "description": (
            "Formalizes Rado's (1933) partition regularity theorem for linear Diophantine equations "
            "sum c_i x_i = 0, proving equivalence with the nonempty subset zero-sum condition."
        ),
    },
    {
        "problem_id": "quantitative_schurs_theorem",
        "title": "Quantitative Schur Multiplicity Theorem and Monochromatic Triple Lower Bounds",
        "source_split": "lean-theorems-1",
        "category": "Additive Combinatorics",
        "rel_path": "Formalization/SchursTheorem/Quantitative.lean",
        "supporting_dir": None,
        "arxiv": ["math.CO", "math.NT"],
        "msc2020": ["05D10", "11B75", "05C55"],
        "description": (
            "Formalizes quantitative lower bounds and monotonicity laws for monochromatic Schur triples "
            "(x + y = z) across finite intervals and group colorings."
        ),
    },
    {
        "problem_id": "first_selection_centerpoint",
        "title": "Rado's Centerpoint Theorem and Barany's First Selection Lemma in 1D",
        "source_split": "lean-theorems-1",
        "category": "Discrete & Convex Geometry",
        "rel_path": "Formalization/ColorfulCaratheodory/Selection.lean",
        "supporting_dir": None,
        "arxiv": ["math.MG", "math.CO"],
        "msc2020": ["52A35", "52C10", "05D15"],
        "description": (
            "Formalizes Rado's centerpoint theorem, Barany's first selection lemma, and the colorful "
            "selection lemma for point configurations via order-statistic median partitions."
        ),
    },
    {
        "problem_id": "sarkaria_colorful_tverberg",
        "title": "Sarkaria's Tensor Trick and Barany's Colorful Tverberg Bridge",
        "source_split": "lean-theorems-1",
        "category": "Discrete & Convex Geometry",
        "rel_path": "Formalization/TverbergsTheorem/Sarkaria.lean",
        "supporting_dir": None,
        "arxiv": ["math.MG", "math.CO"],
        "msc2020": ["52A35", "52A20", "52C10"],
        "description": (
            "Formalizes Sarkaria's (1992) tensor product lifting trick reducing Tverberg's theorem "
            "to Colorful Caratheodory zero-sum configurations in tensor space."
        ),
    },
    {
        "problem_id": "whitney_two_connected",
        "title": "Whitney's k-Connectedness Theorem via Internally Disjoint Menger Paths",
        "source_split": "lean-theorems-2",
        "category": "Extremal Graph Theory",
        "rel_path": "Formalization/MengersTheorem/Whitney.lean",
        "supporting_dir": "MengersTheorem",
        "arxiv": ["math.CO"],
        "msc2020": ["05C40", "05C38"],
        "description": (
            "Formalizes Whitney's (1932) theorem proving that a finite graph is k-vertex-connected "
            "if and only if every pair of distinct non-adjacent vertices is joined by k internally disjoint paths."
        ),
    },
    {
        "problem_id": "vospers_critical_pair_theorem",
        "title": "Vosper's Theorem on Critical Sumset Pairs in Z/pZ",
        "source_split": "lean-theorems-3",
        "category": "Additive Combinatorics",
        "rel_path": "Formalization/CauchyDavenport/Vosper.lean",
        "supporting_dir": None,
        "arxiv": ["math.NT", "math.CO"],
        "msc2020": ["11P70", "11B13", "20K01"],
        "description": (
            "Formalizes Vosper's (1956) inverse Cauchy-Davenport theorem characterizing critical pairs "
            "|A + B| = |A| + |B| - 1 in prime cyclic groups via arithmetic progressions."
        ),
    },
    {
        "problem_id": "chowlas_sumset_theorem",
        "title": "Chowla's Composite Modulus Sumset Theorem in Z/nZ",
        "source_split": "lean-theorems-3",
        "category": "Additive Combinatorics",
        "rel_path": "Formalization/CauchyDavenport/Chowla.lean",
        "supporting_dir": None,
        "arxiv": ["math.NT", "math.CO"],
        "msc2020": ["11P70", "11B13", "20K01"],
        "description": (
            "Formalizes I. Chowla's (1935) composite generalization of the Cauchy-Davenport theorem "
            "for subsets of Z/nZ where elements of B \\ {0} are coprime to n."
        ),
    },
    {
        "problem_id": "erdos_ginzburg_ziv_theorem",
        "title": "The Erdos-Ginzburg-Ziv Zero-Sum Theorem via Iterated Cauchy-Davenport",
        "source_split": "lean-theorems-3",
        "category": "Additive Combinatorics",
        "rel_path": "Formalization/CauchyDavenport/ErdosGinzburgZiv.lean",
        "supporting_dir": None,
        "arxiv": ["math.NT", "math.CO"],
        "msc2020": ["11B75", "11P70", "05D10"],
        "description": (
            "Formalizes the Erdos-Ginzburg-Ziv (1961) zero-sum theorem proving that any 2n - 1 elements "
            "in Z/nZ contain an n-element subsequence summing to zero modulo n."
        ),
    },
]

# Deterministic fine-grained domain classification for all 95 theorems
CATEGORY_MAP: Dict[str, str] = {
    # 1. Spectral Graph Theory (15)
    "alon_boppana": "Spectral Graph Theory",
    "discrete_cheeger": "Spectral Graph Theory",
    "expander_mixing": "Spectral Graph Theory",
    "tanner_expansion": "Spectral Graph Theory",
    "hoffman_singleton": "Spectral Graph Theory",
    "ihara_bass": "Spectral Graph Theory",
    "ihara_zeta": "Spectral Graph Theory",
    "circulant_spectral_theory": "Spectral Graph Theory",
    "cyclic_shift": "Spectral Graph Theory",
    "matrix_tree_theorem": "Spectral Graph Theory",
    "graham_pollak": "Spectral Graph Theory",
    "friendship_theorem": "Spectral Graph Theory",
    "orbifold_spectral_zeta": "Spectral Graph Theory",
    "poincare_spectral_decomposition": "Spectral Graph Theory",
    "poincare_heat_kernel_asymptotics": "Spectral Graph Theory",

    # 2. Additive Combinatorics (15)
    "roths_theorem": "Additive Combinatorics",
    "kelley_meka": "Additive Combinatorics",
    "ruzsa_freiman": "Additive Combinatorics",
    "cauchy_davenport": "Additive Combinatorics",
    "elekes_sum_product": "Additive Combinatorics",
    "van_der_waerden": "Additive Combinatorics",
    "schurs_theorem": "Additive Combinatorics",
    "rado_partition_regularity": "Additive Combinatorics",
    "quantitative_schurs_theorem": "Additive Combinatorics",
    "vospers_critical_pair_theorem": "Additive Combinatorics",
    "chowlas_sumset_theorem": "Additive Combinatorics",
    "erdos_ginzburg_ziv_theorem": "Additive Combinatorics",
    "gilmer_union_closed": "Additive Combinatorics",
    "frankl_wilson": "Additive Combinatorics",
    "lonely_runner_8": "Additive Combinatorics",

    # 3. Extremal Graph Theory (20)
    "szemeredi_regularity": "Extremal Graph Theory",
    "turans_theorem": "Extremal Graph Theory",
    "brooks_theorem": "Extremal Graph Theory",
    "vizings_theorem": "Extremal Graph Theory",
    "mengers_theorem": "Extremal Graph Theory",
    "whitney_two_connected": "Extremal Graph Theory",
    "hall_marriage": "Extremal Graph Theory",
    "konig_matching": "Extremal Graph Theory",
    "konig_matching_augmenting": "Extremal Graph Theory",
    "tutte_one_factor": "Extremal Graph Theory",
    "ore_dirac_hamiltonian": "Extremal Graph Theory",
    "friendship_windmill": "Extremal Graph Theory",
    "erdos_gyarfas": "Extremal Graph Theory",
    "hedetniemi_counterexample": "Extremal Graph Theory",
    "crossing_lemma": "Extremal Graph Theory",
    "erdos_ko_rado": "Extremal Graph Theory",
    "bollobas_two_families": "Extremal Graph Theory",
    "bondy_induced_subsets": "Extremal Graph Theory",
    "sperner_antichain": "Extremal Graph Theory",
    "dilworth_mirsky": "Extremal Graph Theory",

    # 4. Discrete & Convex Geometry (24)
    "art_gallery_theorem": "Discrete & Convex Geometry",
    "becks_theorem": "Discrete & Convex Geometry",
    "cauchy_arm_lemma": "Discrete & Convex Geometry",
    "colorful_caratheodory": "Discrete & Convex Geometry",
    "first_selection_centerpoint": "Discrete & Convex Geometry",
    "colorful_helly": "Discrete & Convex Geometry",
    "radon_helly": "Discrete & Convex Geometry",
    "tverbergs_theorem": "Discrete & Convex Geometry",
    "sarkaria_colorful_tverberg": "Discrete & Convex Geometry",
    "de_bruijn_erdos": "Discrete & Convex Geometry",
    "desargues_theorem": "Discrete & Convex Geometry",
    "erdos_szekeres_convex": "Discrete & Convex Geometry",
    "erdos_unit_distances": "Discrete & Convex Geometry",
    "szemeredi_trotter": "Discrete & Convex Geometry",
    "sylvester_gallai": "Discrete & Convex Geometry",
    "picks_theorem": "Discrete & Convex Geometry",
    "euler_polyhedron": "Discrete & Convex Geometry",
    "combinatorial_map_genus_obstructions": "Discrete & Convex Geometry",
    "birkhoff_von_neumann": "Discrete & Convex Geometry",
    "blichfeldts_theorem": "Discrete & Convex Geometry",
    "jungs_theorem": "Discrete & Convex Geometry",
    "busemann_petty_zhang_audit": "Discrete & Convex Geometry",
    "jenrich_borsuk_64": "Discrete & Convex Geometry",
    "keller_cube_tiling_bridge": "Discrete & Convex Geometry",

    # 5. Algebraic & Enumerative Combinatorics (9)
    "cayleys_formula": "Algebraic & Enumerative Combinatorics",
    "gessel_viennot": "Algebraic & Enumerative Combinatorics",
    "macmahons_master_theorem": "Algebraic & Enumerative Combinatorics",
    "rsk_bijection": "Algebraic & Enumerative Combinatorics",
    "stanley_sl2": "Algebraic & Enumerative Combinatorics",
    "fishers_inequality": "Algebraic & Enumerative Combinatorics",
    "prefix_sparsity": "Algebraic & Enumerative Combinatorics",
    "descartes_rule_of_signs": "Algebraic & Enumerative Combinatorics",
    "engel_jacobian_refutation": "Algebraic & Enumerative Combinatorics",

    # 6. Arithmetic Dynamics & Number Theory (2)
    "ramanujan_tau": "Arithmetic Dynamics & Number Theory",
    "poincare_adelic_standard_model": "Arithmetic Dynamics & Number Theory",

    # 7. Algebraic Topology & Monodromy (10)
    "sperners_lemma": "Algebraic Topology & Monodromy",
    "sperner_3d": "Algebraic Topology & Monodromy",
    "sperner_nd": "Algebraic Topology & Monodromy",
    "tuckers_lemma": "Algebraic Topology & Monodromy",
    "kneser_lovasz": "Algebraic Topology & Monodromy",
    "brieskorn_manifolds": "Algebraic Topology & Monodromy",
    "brieskorn_su2_character_variety": "Algebraic Topology & Monodromy",
    "picard_fuchs_mirror_monodromy": "Algebraic Topology & Monodromy",
    "universal_monodromy_weight_filtration": "Algebraic Topology & Monodromy",
    "poincare_binary_icosahedral": "Algebraic Topology & Monodromy",
}

TIER_SPLIT_MAP: Dict[str, str] = {
    "Discrete & Convex Geometry": "tier1_discrete_geometry_extremal",
    "Extremal Graph Theory": "tier1_discrete_geometry_extremal",
    "Spectral Graph Theory": "tier2_algebraic_spectral_graph",
    "Algebraic & Enumerative Combinatorics": "tier2_algebraic_spectral_graph",
    "Additive Combinatorics": "tier3_additive_combinatorics_zeta",
    "Arithmetic Dynamics & Number Theory": "tier3_additive_combinatorics_zeta",
    "Algebraic Topology & Monodromy": "tier3_additive_combinatorics_zeta",
}

TACTIC_KEYWORDS = [
    "rw", "simp", "exact", "apply", "intro", "intros", "have", "rcases", "obtain",
    "cases", "induction", "linarith", "nlinarith", "omega", "ring", "ring_nf",
    "norm_num", "positivity", "decide", "aesop", "tauto", "congr", "ext",
    "funext", "push_neg", "contrapose", "by_contra", "by_cases", "split_ifs",
    "refine", "use", "existsi", "constructor", "left", "right", "symm", "trans",
    "calc", "unfold", "dsimp", "change", "suffices", " specialize", "clear",
    "revert", "subst", "assumption", " contradiction", "exfalso", " native_decide",
    "abel", "group", "field_simp", "norm_cast", "push_cast", "exact_mod_cast",
    "gcongr", "mono", "erw", "nth_rw", "conv",
]

TACTIC_REGEX = re.compile(
    r"\b(?:" + "|".join(t.strip() for t in TACTIC_KEYWORDS) + r")\b"
)


def strip_lean_comments(text: str) -> str:
    """Remove Lean 4 block comments `/- ... -/` (with nesting) and `-- ...` line comments."""
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


def count_non_empty_loc(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def count_tactics(text: str) -> int:
    cleaned = strip_lean_comments(text)
    return len(TACTIC_REGEX.findall(cleaned))


def check_zero_sorry(text: str) -> bool:
    cleaned = strip_lean_comments(text)
    return len(re.findall(r"\b(?:sorry|admit)\b", cleaned)) == 0


def extract_imports(text: str) -> List[str]:
    imports: List[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("import "):
            mod = s[len("import ") :].strip()
            if mod and mod not in imports:
                imports.append(mod)
    return imports


def extract_theorem_names(text: str) -> List[str]:
    cleaned = strip_lean_comments(text)
    names = re.findall(
        r"^(?:@\S+\s+)*(?:private\s+|protected\s+|noncomputable\s+)*(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)",
        cleaned,
        flags=re.MULTILINE,
    )
    seen = []
    for nm in names:
        if nm not in seen:
            seen.append(nm)
    return seen


def synthesize_challenge_from_formalization(solution_text: str) -> str:
    """
    Deterministically transforms a Formalization/*.lean module into a Challenge.lean
    specification by preserving all imports, docstrings, definitions, structures, and
    theorem/lemma type signatures while replacing theorem/lemma proof bodies with `:= by sorry`.
    """
    lines = solution_text.splitlines()
    out_lines: List[str] = []
    i = 0
    n = len(lines)

    top_level_starters = (
        "theorem ",
        "lemma ",
        "private theorem ",
        "private lemma ",
        "protected theorem ",
        "protected lemma ",
        "def ",
        "noncomputable def ",
        "private def ",
        "abbrev ",
        "structure ",
        "class ",
        "inductive ",
        "instance ",
        "noncomputable instance ",
        "axiom ",
        "variable ",
        "variables ",
        "open ",
        "namespace ",
        "section ",
        "end ",
        "omit ",
        "@",
        "/-",
        "--",
    )

    thm_starters = (
        "theorem ",
        "lemma ",
        "private theorem ",
        "private lemma ",
        "protected theorem ",
        "protected lemma ",
    )

    while i < n:
        line = lines[i]
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        if indent == 0 and any(stripped.startswith(ts) for ts in thm_starters):
            # Collect signature lines until top-level `:=`
            sig_lines = [line]
            i += 1
            while i < n and ":=" not in sig_lines[-1]:
                sig_lines.append(lines[i])
                i += 1
            # Truncate the last signature line at `:=`
            last = sig_lines[-1]
            idx = last.find(":=")
            if idx != -1:
                sig_lines[-1] = last[:idx].rstrip() + " := by\n  sorry"
            out_lines.extend(sig_lines)

            # Skip proof body lines until next top-level starter or EOF
            while i < n:
                nxt = lines[i]
                nxt_s = nxt.lstrip()
                nxt_indent = len(nxt) - len(nxt_s)
                if nxt_s == "":
                    # Check if next non-empty line is top-level
                    j = i + 1
                    while j < n and lines[j].strip() == "":
                        j += 1
                    if j >= n:
                        i = j
                        break
                    peek = lines[j]
                    peek_s = peek.lstrip()
                    peek_indent = len(peek) - len(peek_s)
                    if peek_indent == 0 and any(peek_s.startswith(st) for st in top_level_starters):
                        out_lines.append("")
                        i = j
                        break
                    i += 1
                elif nxt_indent == 0 and any(nxt_s.startswith(st) for st in top_level_starters):
                    break
                else:
                    i += 1
        else:
            out_lines.append(line)
            i += 1

    return "\n".join(out_lines) + "\n"


def assemble_reference_solution(
    repo_dir: Path,
    pal_sol_path: Optional[Path],
    form_mod: Optional[str],
    form_subdir: Optional[str],
) -> Tuple[str, List[str]]:
    """
    Returns (full_reference_solution_code, supporting_module_names).
    Resolves `import Formalization.<Mod>` wrappers to the actual gold-standard
    Lean 4 proof code in `Formalization/<Mod>.lean` plus any supporting multi-file
    modules in `Formalization/<Subdir>/*.lean`.
    If `palomar/<slug>/Solution.lean` is already a standalone self-contained file
    (does not import `Formalization.*`), uses `palomar/<slug>/Solution.lean` as the
    primary reference solution while recording `multi_files` metadata.
    """
    sections: List[str] = []
    multi_files: List[str] = []

    form_dir = repo_dir / "Formalization"

    # Collect multi-file subdirectory modules metadata if present
    subdir_contents: List[Tuple[str, str]] = []
    if form_subdir:
        subdir_path = form_dir / form_subdir
        if subdir_path.exists() and subdir_path.is_dir():
            for p in sorted(subdir_path.rglob("*.lean")):
                rel_name = p.relative_to(form_dir).as_posix()
                multi_files.append(rel_name)
                subdir_contents.append((rel_name, p.read_text(encoding="utf-8").strip()))

    pal_sol_content = ""
    if pal_sol_path and pal_sol_path.exists():
        pal_sol_content = pal_sol_path.read_text(encoding="utf-8").strip()

    imports_formalization = "import Formalization." in pal_sol_content

    if imports_formalization:
        for rel_name, content in subdir_contents:
            sections.append(
                f"-- ============================================================================\n-- Supporting Module: Formalization/{rel_name}\n-- ============================================================================\n{content}"
            )
        # Resolve all top-level Formalization.<Mod> imports in pal_sol_content
        imported_mods = re.findall(r"^import\s+Formalization\.([A-Za-z0-9_]+)\s*$", pal_sol_content, re.M)
        if form_mod and form_mod not in imported_mods:
            imported_mods.insert(0, form_mod)
        for mod_name in imported_mods:
            f_path = form_dir / f"{mod_name}.lean"
            if f_path.exists():
                sections.append(
                    f"-- ============================================================================\n-- Main Module: Formalization/{mod_name}.lean\n-- ============================================================================\n{f_path.read_text(encoding='utf-8').strip()}"
                )
        if len(pal_sol_content.splitlines()) > 3:
            sections.append(
                f"-- ============================================================================\n-- Palomar Export Bridge: Solution.lean\n-- ============================================================================\n{pal_sol_content}"
            )
    elif pal_sol_content:
        sections.append(pal_sol_content)
    elif form_mod:
        f_path = form_dir / f"{form_mod}.lean"
        if f_path.exists():
            sections.append(f_path.read_text(encoding="utf-8").strip())

    return "\n\n".join(sections) + "\n", multi_files


def load_formalization_yaml(fy_path: Path) -> Dict[str, Any]:
    if not fy_path.exists():
        return {}
    raw = fy_path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    # Resilient regex fallback for minor indentation quirks
    name_m = re.search(r'^\s*name:\s*["\']?(.*?)["\']?\s*$', raw, flags=re.M)
    arxiv_m = re.search(r'^\s*arxiv:\s*\[(.*?)\]', raw, flags=re.M)
    msc_m = re.search(r'^\s*msc2020:\s*\[(.*?)\]', raw, flags=re.M)
    desc_m = re.search(r'^\s*description:\s*>-\s*\n((?:^\s{4,}.*\n)+)', raw, flags=re.M)
    desc = " ".join(line.strip() for line in desc_m.group(1).splitlines()) if desc_m else ""
    arxiv = [x.strip().strip("\"'") for x in arxiv_m.group(1).split(",") if x.strip()] if arxiv_m else []
    msc = [x.strip().strip("\"'") for x in msc_m.group(1).split(",") if x.strip()] if msc_m else []
    return {
        "project": {
            "name": name_m.group(1) if name_m else "",
            "description": desc,
        },
        "classification": {
            "arxiv": arxiv,
            "msc2020": msc,
        },
    }


def parse_palomar_entry(repo: str, slug: str) -> Dict[str, Any]:
    repo_dir = BASE_REPOS_DIR / repo
    pal_dir = repo_dir / "palomar" / slug

    # Disambiguate konig_matching in lean-theorems-2 vs lean-theorems-1
    problem_id = "konig_matching_augmenting" if (repo == "lean-theorems-2" and slug == "konig_matching") else slug

    fy_path = pal_dir / "formalization.yaml"
    comp_path = pal_dir / "comparator.json"
    ch_path = pal_dir / "Challenge.lean"
    sol_path = pal_dir / "Solution.lean"

    meta = load_formalization_yaml(fy_path)
    comp = json.loads(comp_path.read_text(encoding="utf-8")) if comp_path.exists() else {}

    title = meta.get("project", {}).get("name", slug.replace("_", " ").title())
    if problem_id == "konig_matching_augmenting":
        title = "König's Bipartite Matching Theorem (Monolithic Augmenting-Walk Formalization)"

    description = meta.get("project", {}).get("description", "").strip()
    arxiv = meta.get("classification", {}).get("arxiv", [])
    msc2020 = [str(x) for x in meta.get("classification", {}).get("msc2020", [])]

    challenge_code = ch_path.read_text(encoding="utf-8")
    form_mod, form_subdir = SLUG_TO_FORMALIZATION.get((repo, slug), (None, None))
    reference_solution, multi_files = assemble_reference_solution(repo_dir, sol_path, form_mod, form_subdir)

    comp_thms = comp.get("theorem_names", [])
    extracted_thms = extract_theorem_names(reference_solution)
    theorem_names = list(dict.fromkeys(comp_thms + extracted_thms))

    all_imports = extract_imports(challenge_code + "\n" + reference_solution)
    mathlib_imports = [imp for imp in all_imports if imp.startswith("Mathlib")]

    ch_loc = count_non_empty_loc(challenge_code)
    sol_loc = count_non_empty_loc(reference_solution)
    ratio = round(sol_loc / max(ch_loc, 1), 4)
    tactic_cnt = count_tactics(reference_solution)
    zero_sorry = check_zero_sorry(reference_solution)

    category = CATEGORY_MAP[problem_id]
    tier_split = TIER_SPLIT_MAP[category]

    base_axioms = comp.get("permitted_axioms", ["propext", "Quot.sound", "Classical.choice"])
    src_axioms = re.findall(
        r"^\s*(?:private\s+|protected\s+)?axiom\s+([A-Za-z0-9_'.]+)",
        strip_lean_comments(reference_solution),
        re.M,
    )
    permitted_axioms = list(dict.fromkeys(base_axioms + src_axioms))

    return {
        "problem_id": problem_id,
        "title": title,
        "source_split": repo,
        "source_type": "palomar_package",
        "source_path": f"{repo}/palomar/{slug}",
        "category": category,
        "tier_split": tier_split,
        "description": description,
        "arxiv_classes": arxiv,
        "msc2020": msc2020,
        "lean_toolchain": "leanprover/lean4:v4.34.0-rc1",
        "permitted_axioms": permitted_axioms,
        "theorem_names": theorem_names,
        "imports": mathlib_imports if mathlib_imports else all_imports,
        "challenge_statement": challenge_code,
        "reference_solution": reference_solution,
        "metrics": {
            "challenge_loc": ch_loc,
            "solution_loc": sol_loc,
            "proof_expansion_ratio": ratio,
            "tactic_count": tactic_cnt,
            "zero_sorry_verified": zero_sorry,
            "multi_file_modules": {
                "count": len(multi_files),
                "names": multi_files,
            },
        },
    }


def parse_standalone_formalization_entry(spec: Dict[str, Any]) -> Dict[str, Any]:
    repo = spec["source_split"]
    repo_dir = BASE_REPOS_DIR / repo
    mod_path = repo_dir / spec["rel_path"]
    raw_sol = mod_path.read_text(encoding="utf-8")

    # Assemble supporting files if supporting_dir is specified
    multi_files: List[str] = []
    sections: List[str] = []
    if spec.get("supporting_dir"):
        sdir = repo_dir / "Formalization" / spec["supporting_dir"]
        if sdir.exists():
            for p in sorted(sdir.rglob("*.lean")):
                if p.resolve() == mod_path.resolve():
                    continue
                rel_name = p.relative_to(repo_dir / "Formalization").as_posix()
                multi_files.append(rel_name)
                sections.append(
                    f"-- ============================================================================\n-- Supporting Module: Formalization/{rel_name}\n-- ============================================================================\n{p.read_text(encoding='utf-8').strip()}"
                )
    sections.append(
        f"-- ============================================================================\n-- Main Module: {spec['rel_path']}\n-- ============================================================================\n{raw_sol.strip()}"
    )
    reference_solution = "\n\n".join(sections) + "\n"
    challenge_code = synthesize_challenge_from_formalization(raw_sol)

    theorem_names = extract_theorem_names(raw_sol)
    all_imports = extract_imports(reference_solution)
    mathlib_imports = [imp for imp in all_imports if imp.startswith("Mathlib")]

    ch_loc = count_non_empty_loc(challenge_code)
    sol_loc = count_non_empty_loc(reference_solution)
    ratio = round(sol_loc / max(ch_loc, 1), 4)
    tactic_cnt = count_tactics(reference_solution)
    zero_sorry = check_zero_sorry(reference_solution)

    category = CATEGORY_MAP[spec["problem_id"]]
    tier_split = TIER_SPLIT_MAP[category]

    base_axioms = ["propext", "Quot.sound", "Classical.choice"]
    src_axioms = re.findall(
        r"^\s*(?:private\s+|protected\s+)?axiom\s+([A-Za-z0-9_'.]+)",
        strip_lean_comments(reference_solution),
        re.M,
    )
    permitted_axioms = list(dict.fromkeys(base_axioms + src_axioms))

    return {
        "problem_id": spec["problem_id"],
        "title": spec["title"],
        "source_split": repo,
        "source_type": "formalization_module",
        "source_path": f"{repo}/{spec['rel_path']}",
        "category": category,
        "tier_split": tier_split,
        "description": spec["description"],
        "arxiv_classes": spec["arxiv"],
        "msc2020": spec["msc2020"],
        "lean_toolchain": "leanprover/lean4:v4.34.0-rc1",
        "permitted_axioms": permitted_axioms,
        "theorem_names": theorem_names,
        "imports": mathlib_imports if mathlib_imports else all_imports,
        "challenge_statement": challenge_code,
        "reference_solution": reference_solution,
        "metrics": {
            "challenge_loc": ch_loc,
            "solution_loc": sol_loc,
            "proof_expansion_ratio": ratio,
            "tactic_count": tactic_cnt,
            "zero_sorry_verified": zero_sorry,
            "multi_file_modules": {
                "count": len(multi_files),
                "names": multi_files,
            },
        },
    }


def build_all() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    # 1. Extract all 82 Palomar packages across lean-theorems-1, lean-theorems-2, lean-theorems-3
    for repo in REPOS:
        pal_root = BASE_REPOS_DIR / repo / "palomar"
        for slug in sorted(os.listdir(pal_root)):
            if (pal_root / slug).is_dir():
                rec = parse_palomar_entry(repo, slug)
                records.append(rec)

    # 2. Extract the 13 standalone Formalization theorem modules
    for spec in STANDALONE_FORMALIZATION_MODULES:
        rec = parse_standalone_formalization_entry(spec)
        records.append(rec)

    # Sort deterministically by source_split then problem_id
    records.sort(key=lambda r: (r["source_split"], r["problem_id"]))

    # Write data/benchmark.jsonl
    data_dir = BENCHMARK_ROOT / "data"
    splits_dir = data_dir / "splits"
    data_dir.mkdir(parents=True, exist_ok=True)
    splits_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = data_dir / "benchmark.jsonl"
    with open(jsonl_path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write tier splits
    for tier_name in sorted(set(TIER_SPLIT_MAP.values())):
        tier_path = splits_dir / f"{tier_name}.jsonl"
        tier_recs = [r for r in records if r["tier_split"] == tier_name]
        with open(tier_path, "w", encoding="utf-8", newline="\n") as f:
            for r in tier_recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write data/benchmark_summary.csv
    csv_path = data_dir / "benchmark_summary.csv"
    fieldnames = [
        "problem_id",
        "title",
        "source_split",
        "source_type",
        "category",
        "tier_split",
        "theorem_count",
        "primary_theorem",
        "import_count",
        "challenge_loc",
        "solution_loc",
        "proof_expansion_ratio",
        "tactic_count",
        "multi_file_count",
        "zero_sorry_verified",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            m = r["metrics"]
            writer.writerow(
                {
                    "problem_id": r["problem_id"],
                    "title": r["title"],
                    "source_split": r["source_split"],
                    "source_type": r["source_type"],
                    "category": r["category"],
                    "tier_split": r["tier_split"],
                    "theorem_count": len(r["theorem_names"]),
                    "primary_theorem": r["theorem_names"][0] if r["theorem_names"] else "",
                    "import_count": len(r["imports"]),
                    "challenge_loc": m["challenge_loc"],
                    "solution_loc": m["solution_loc"],
                    "proof_expansion_ratio": m["proof_expansion_ratio"],
                    "tactic_count": m["tactic_count"],
                    "multi_file_count": m["multi_file_modules"]["count"],
                    "zero_sorry_verified": m["zero_sorry_verified"],
                }
            )

    # Also write summary stats JSON for README & Interactive Explorer
    stats = compute_summary_stats(records)
    (data_dir / "benchmark_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Export HuggingFace-compatible Parquet file if pandas + pyarrow/fastparquet are available
    try:
        import pandas as pd

        flat_rows = []
        for r in records:
            m = r["metrics"]
            flat_rows.append(
                {
                    "problem_id": r["problem_id"],
                    "title": r["title"],
                    "source_split": r["source_split"],
                    "source_type": r["source_type"],
                    "source_path": r["source_path"],
                    "category": r["category"],
                    "tier_split": r["tier_split"],
                    "description": r["description"],
                    "arxiv_classes": r["arxiv_classes"],
                    "msc2020": r["msc2020"],
                    "lean_toolchain": r["lean_toolchain"],
                    "permitted_axioms": r["permitted_axioms"],
                    "theorem_names": r["theorem_names"],
                    "imports": r["imports"],
                    "challenge_statement": r["challenge_statement"],
                    "reference_solution": r["reference_solution"],
                    "challenge_loc": m["challenge_loc"],
                    "solution_loc": m["solution_loc"],
                    "proof_expansion_ratio": m["proof_expansion_ratio"],
                    "tactic_count": m["tactic_count"],
                    "zero_sorry_verified": m["zero_sorry_verified"],
                    "multi_file_count": m["multi_file_modules"]["count"],
                    "multi_file_names": m["multi_file_modules"]["names"],
                }
            )
        df = pd.DataFrame(flat_rows)
        df.to_parquet(data_dir / "train-00000-of-00001.parquet", index=False)
    except Exception as exc:
        print(f"[INFO] Parquet export skipped ({exc}); JSONL and CSV exports complete.")

    return records


def compute_summary_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_cat: Dict[str, int] = {}
    by_repo: Dict[str, int] = {}
    by_tier: Dict[str, int] = {}
    total_ch_loc = 0
    total_sol_loc = 0
    total_tactics = 0
    total_thms = 0
    zero_sorry_all = True

    for r in records:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
        by_repo[r["source_split"]] = by_repo.get(r["source_split"], 0) + 1
        by_tier[r["tier_split"]] = by_tier.get(r["tier_split"], 0) + 1
        m = r["metrics"]
        total_ch_loc += m["challenge_loc"]
        total_sol_loc += m["solution_loc"]
        total_tactics += m["tactic_count"]
        total_thms += len(r["theorem_names"])
        if not m["zero_sorry_verified"]:
            zero_sorry_all = False

    return {
        "total_problems": len(records),
        "total_theorem_declarations": total_thms,
        "total_challenge_loc": total_ch_loc,
        "total_solution_loc": total_sol_loc,
        "overall_expansion_ratio": round(total_sol_loc / max(total_ch_loc, 1), 4),
        "total_tactic_invocations": total_tactics,
        "zero_sorry_verified_count": sum(1 for r in records if r["metrics"]["zero_sorry_verified"]),
        "zero_sorry_all": zero_sorry_all,
        "by_source_split": by_repo,
        "by_category": dict(sorted(by_cat.items(), key=lambda kv: (-kv[1], kv[0]))),
        "by_tier_split": by_tier,
    }


if __name__ == "__main__":
    recs = build_all()
    stats = compute_summary_stats(recs)
    print(json.dumps(stats, indent=2))
