"""Verbatim extracts from the Digital to Wave Testbench at tag v0.4.1 (vendored; do not edit).

Source: https://github.com/sparkainlp-x/digital-to-wave-testbench, tag v0.4.1, commit f4b39343e7dac983a06238795bc2b7f42c5f94b5
(Zenodo version DOI 10.5281/zenodo.23134616; concept DOI 10.5281/zenodo.23122876). AGPL-3.0-only,
Copyright (C) 2026 Jean-François Brisson / Spark AI NLP (same author and licence as this project).

Each top-level definition below is copied character for character from the named file; the SHA-256 of each
definition's source text and of each whole source file is recorded in PROVENANCE.json, checked by
tests/test_vendor_provenance.py and re-derived from a testbench checkout by tools/verify_vendor.py.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

# --- robustness_benchmark_v2.py, lines 30-30 (v0.4.1) ---
VECTOR_SEED = 20261004


# --- robustness_benchmark_v2.py, lines 35-35 (v0.4.1) ---
WILSON_Z_95 = 1.959963984540054


# --- robustness_benchmark_v2.py, lines 45-65 (v0.4.1) ---
def build_input_patterns(vector_seed: int = VECTOR_SEED) -> dict[str, np.ndarray]:
    """Return six fixed 32-value test vectors spanning distinct value patterns."""
    mixed_half = np.asarray(
        [-2.0, -1.75, -1.5, -1.0, -0.75, -0.25, -0.125, -1.25,
          2.0, 1.75, 1.5, 1.0, 0.75, 0.25, 0.125, 1.25], dtype=float
    )
    sparse = np.zeros(32, dtype=float)
    sparse[[0, 4, 15, 22, 31]] = [-2.0, 1.0, -0.25, 2.0, -1.5]
    boundary_half = np.asarray(
        [-2.0, -1.999, -1.5, -1.0, -0.25, -0.001, 0.0, 0.001,
          0.25, 1.0, 1.5, 1.999, 2.0, 0.0, -2.0, 2.0], dtype=float
    )
    rng = np.random.default_rng(vector_seed)
    patterns = {
        "mixed_signs": np.tile(mixed_half, 2),
        "sparse_and_zeros": sparse,
        "boundary_values": np.tile(boundary_half, 2),
    }
    for index in range(1, 4):
        patterns[f"randomized_{index}"] = rng.uniform(-2.0, 2.0, size=32)
    return patterns


# --- robustness_benchmark_v2.py, lines 68-81 (v0.4.1) ---
def wilson_interval(successes: int, trials: int, z: float = WILSON_Z_95) -> tuple[float, float]:
    """Return a two-sided Wilson score interval for a binomial proportion."""
    if isinstance(successes, bool) or not isinstance(successes, (int, np.integer)):
        raise ValueError("successes must be an integer")
    if isinstance(trials, bool) or not isinstance(trials, (int, np.integer)):
        raise ValueError("trials must be an integer")
    if trials < 1 or successes < 0 or successes > trials or not math.isfinite(z) or z <= 0:
        raise ValueError("invalid Wilson interval arguments")
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = (p + z2 / (2.0 * trials)) / denominator
    radius = z * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials * trials)) / denominator
    return max(0.0, center - radius), min(1.0, center + radius)


# --- robustness_benchmark_v5_timing.py, lines 37-37 (v0.4.1) ---
TOLERANCE = 0.25


# --- robustness_benchmark_v5_timing.py, lines 72-79 (v0.4.1) ---
def _finite_nonnegative(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite and non-negative") from exc
    if not math.isfinite(result) or result < 0.0:
        raise ValueError(f"{label} must be finite and non-negative")
    return result


# --- robustness_benchmark_v5_timing.py, lines 145-168 (v0.4.1) ---
def theoretical_frame_pass_probability(
    component_bias: Any,
    noise_std: float,
    tolerance: float = TOLERANCE,
    template_energy: float = 32.0,
) -> float:
    """Compute a frame probability for independent Gaussian projection errors."""
    bias = np.asarray(component_bias, dtype=float)
    sigma = _finite_nonnegative(noise_std, "noise_std")
    tau = _finite_nonnegative(tolerance, "tolerance")
    energy = _finite_nonnegative(template_energy, "template_energy")
    if bias.ndim != 1 or bias.size < 1 or not np.all(np.isfinite(bias)):
        raise ValueError("component_bias must be a non-empty finite vector")
    if energy <= 0.0:
        raise ValueError("template_energy must be positive")
    if sigma == 0.0:
        return float(np.all(np.abs(bias) <= tau))
    component_sd = sigma / math.sqrt(energy)
    probabilities = []
    for mean in bias:
        upper = 0.5 * (1.0 + math.erf((tau - float(mean)) / (math.sqrt(2.0) * component_sd)))
        lower = 0.5 * (1.0 + math.erf((-tau - float(mean)) / (math.sqrt(2.0) * component_sd)))
        probabilities.append(max(0.0, min(1.0, upper - lower)))
    return float(np.prod(probabilities))


# --- robustness_benchmark_v6_timing_recovery.py, lines 171-180 (v0.4.1) ---
def mcnemar_exact_p(a_pass_b_fail: int, a_fail_b_pass: int) -> float:
    """Exact two-sided McNemar (binomial) p-value from the two discordant counts."""
    b, c = int(a_pass_b_fail), int(a_fail_b_pass)
    if b < 0 or c < 0:
        raise ValueError("discordant counts must be non-negative")
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1))
    return min(1.0, 2 * tail / 2**n)
