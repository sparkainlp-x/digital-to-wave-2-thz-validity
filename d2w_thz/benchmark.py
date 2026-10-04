"""Locked protocol: Part I encoding through the Part II THz/ELF channel, plus the engineering-validity report.

SYNTHETIC. No physical, biological or safety claim is made; Mun Seok Lee has not reviewed or endorsed this software.
The conditions below were fixed in reports/protocol-lock.md before the full run (``python -m d2w_thz.benchmark``).

Experiments (6 fixed testbench vectors, ``FRAMES_PER_VECTOR`` noisy frames per vector and cell, pass iff
max |error| <= 0.25 over the 32 values; for ``magnitude_sign_blind`` the target is |N|):
- E1: transmit mapping x noise SD {0, 0.25, 0.45} at a 40 Hz envelope, z = 0.
- E2: two-tone beat, envelope {5, 20, 40, 60, 100} Hz, SD 0.45 (100 Hz is the edge case at the membrane cut-off).
- E3: two-tone beat, depth in water at 0.99 THz {0, 5, 10, 20, 30, 50, 100} um (alpha = 220 /cm), SD 0.25.
- E4: two-tone beat, relative THz tone error {0, 1e-14, 2.5e-14, 5e-14, 1e-13, 2e-13} at 1 THz, 40 Hz, SD 0.45.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from . import thz_channel as ch  # noqa: E402
from ._vendor.testbench_v041 import (  # noqa: E402
    VECTOR_SEED,
    build_input_patterns,
    mcnemar_exact_p,
    theoretical_frame_pass_probability,
    wilson_interval,
)
from .references import ref  # noqa: E402
from .validity import EQUATION_INVENTORY, INVENTORY_FIELDS, engineering_validity_report  # noqa: E402

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent
ARTIFACTS = ROOT / "artifacts"
STEM = "thz-channel-benchmark"

MASTER_SEED = 20261013
DEV_SEED = 20261113
TEST_SEED = 6262
# Seeds already used by the Digital to Wave Testbench (v2-v8 master and development seeds) and by the unpublished,
# local-only testbench branch part2-thz-channel (20261012 master, 20261112 development) from which this design comes.
PRIOR_SEEDS = frozenset({20261003, 20261004, 20261005, 20261006, 20261007, 20261008, 20261009, 20261010, 20261011,
                         20261111, 20261012, 20261112})
FRAMES_PER_VECTOR = 2_000
TOLERANCE = 0.25
POOLED = "POOLED_ALL_VECTORS"
ALPHA_PER_M = ref("water_alpha_per_cm")["0.99"] * 100.0

E1_SIGMAS = (0.0, 0.25, 0.45)
E2_ENVELOPE_HZ = (5.0, 20.0, 40.0, 60.0, 100.0)
E2_SIGMA = 0.45
E3_DEPTHS_UM = (0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 100.0)
E3_SIGMA = 0.25
E4_TONE_MISMATCH_FRAC = (0.0, 1.0e-14, 2.5e-14, 5.0e-14, 1.0e-13, 2.0e-13)
E4_SIGMA = 0.45

CSV_FIELDS = (
    "experiment", "mapping", "envelope_hz", "depth_um", "tone_mismatch_frac", "beat_offset_cycles_per_symbol",
    "noise_std", "vector_pattern", "receiver", "frames", "frames_passing", "frame_pass_share", "wilson95_lower",
    "wilson95_upper", "mae", "theory_frame_pass_probability", "lpf_gain", "lpf_phase_deg", "depth_gain",
)
PAIRED_FIELDS = ("experiment", "cell", "receiver_a", "receiver_b", "a_pass_b_fail", "a_fail_b_pass", "mcnemar_p")
DIMENSION_FIELDS = ("equation", "page", "lhs", "rhs", "consistent", "note")


def protocol_cells() -> list[dict[str, Any]]:
    cells = []
    for m in ch.MAPPINGS:
        for s in E1_SIGMAS:
            cells.append({"experiment": "E1_mapping", "mapping": m, "envelope_hz": ch.REFERENCE_ENVELOPE_HZ,
                          "depth_um": 0.0, "tone_mismatch_frac": 0.0, "noise_std": s})
    for f in E2_ENVELOPE_HZ:
        cells.append({"experiment": "E2_envelope_frequency", "mapping": "two_tone_beat", "envelope_hz": f,
                      "depth_um": 0.0, "tone_mismatch_frac": 0.0, "noise_std": E2_SIGMA})
    for z in E3_DEPTHS_UM:
        cells.append({"experiment": "E3_depth_water_0p99THz", "mapping": "two_tone_beat",
                      "envelope_hz": ch.REFERENCE_ENVELOPE_HZ, "depth_um": z, "tone_mismatch_frac": 0.0,
                      "noise_std": E3_SIGMA})
    for e in E4_TONE_MISMATCH_FRAC:
        cells.append({"experiment": "E4_two_tone_mismatch", "mapping": "two_tone_beat",
                      "envelope_hz": ch.REFERENCE_ENVELOPE_HZ, "depth_um": 0.0, "tone_mismatch_frac": e,
                      "noise_std": E4_SIGMA})
    return cells


def receivers_for(mapping: str) -> tuple[str, ...]:
    if mapping == "single_tone_direct":
        return ("nominal", "magnitude_sign_blind")
    return ("nominal", "lpf_calibrated", "calibrated")


def cell_label(cell: dict[str, Any]) -> str:
    return (f"{cell['mapping']}|f_env={cell['envelope_hz']:g}Hz|z={cell['depth_um']:g}um|"
            f"mismatch={cell['tone_mismatch_frac']:g}|sigma={cell['noise_std']:g}")


def fixed_patterns() -> dict[str, np.ndarray]:
    return {k: np.asarray(v, dtype=float) for k, v in build_input_patterns(VECTOR_SEED).items()}


def run_cell(cell: dict[str, Any], patterns: dict[str, np.ndarray], frames_per_vector: int, seed: int,
             cell_index: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Simulate one cell. Noise for vector v comes from SeedSequence([seed, 9, cell_index, v])."""
    a = ch.lpf_coefficient(ch.MEMBRANE_CUTOFF_HZ, ch.sample_rate_hz(cell["envelope_hz"]))
    gain_lpf, phase_lpf = ch.lpf_response(a)
    g_depth = ch.depth_gain(cell["depth_um"] * 1e-6, ALPHA_PER_M)
    offset = ch.beat_offset_from_tone_mismatch(cell["tone_mismatch_frac"], envelope_hz=cell["envelope_hz"])
    sigma = cell["noise_std"]
    receivers = receivers_for(cell["mapping"])
    pass_flags: dict[str, list[np.ndarray]] = {r: [] for r in receivers}
    rows = []
    stats: dict[str, dict[str, Any]] = {r: {"passing": 0, "abs_err": 0.0, "theory": 0.0} for r in receivers}
    for v_index, (name, target_values) in enumerate(patterns.items()):
        clean = g_depth * ch.apply_lpf(ch.transmit(target_values, cell["mapping"], offset), a)
        rng = np.random.default_rng(np.random.SeedSequence([seed, 9, cell_index, v_index]))
        noisy = clean[None, :] + rng.normal(0.0, sigma, size=(frames_per_vector, ch.FRAME_SAMPLES))
        for r in receivers:
            if r == "nominal":
                est, clean_est, sd_scale = ch.decode_nominal(noisy), ch.decode_nominal(clean[None, :])[0], 1.0
            elif r == "lpf_calibrated":
                est = ch.decode_calibrated(noisy, gain_lpf, phase_lpf)
                clean_est, sd_scale = ch.decode_calibrated(clean[None, :], gain_lpf, phase_lpf)[0], gain_lpf
            elif r == "calibrated":
                g = gain_lpf * g_depth
                est = ch.decode_calibrated(noisy, g, phase_lpf)
                clean_est, sd_scale = ch.decode_calibrated(clean[None, :], g, phase_lpf)[0], g
            else:
                est, clean_est, sd_scale = ch.decode_magnitude(noisy), None, None
            target = np.abs(target_values) if r == "magnitude_sign_blind" else target_values
            err = np.abs(est - target[None, :])
            passed = err.max(axis=1) <= TOLERANCE
            pass_flags[r].append(passed)
            theory = (None if clean_est is None else
                      theoretical_frame_pass_probability(clean_est - target_values, sigma / sd_scale, TOLERANCE))
            k = int(passed.sum())
            lo, hi = wilson_interval(k, frames_per_vector)
            stats[r]["passing"] += k
            stats[r]["abs_err"] += float(err.mean())
            stats[r]["theory"] = None if theory is None else stats[r]["theory"] + theory
            rows.append(_row(cell, offset, name, r, frames_per_vector, k, lo, hi, float(err.mean()), theory,
                             gain_lpf, phase_lpf, g_depth))
    n_total = frames_per_vector * len(patterns)
    for r in receivers:
        k = int(stats[r]["passing"])
        lo, hi = wilson_interval(k, n_total)
        rows.append(_row(cell, offset, POOLED, r, n_total, k, lo, hi, stats[r]["abs_err"] / len(patterns),
                         None if stats[r]["theory"] is None else stats[r]["theory"] / len(patterns),
                         gain_lpf, phase_lpf, g_depth))
    paired = []
    flat = {r: np.concatenate(pass_flags[r]) for r in receivers}
    for r in (x for x in receivers if x != "nominal"):
        b = int(np.sum(flat[r] & ~flat["nominal"]))
        c = int(np.sum(~flat[r] & flat["nominal"]))
        paired.append({"experiment": cell["experiment"], "cell": cell_label(cell), "receiver_a": r,
                       "receiver_b": "nominal", "a_pass_b_fail": b, "a_fail_b_pass": c,
                       "mcnemar_p": mcnemar_exact_p(b, c)})
    return rows, paired


def _row(cell, offset, pattern, receiver, frames, k, lo, hi, mae, theory, gain, phase, g_depth) -> dict[str, Any]:
    return {
        "experiment": cell["experiment"], "mapping": cell["mapping"], "envelope_hz": cell["envelope_hz"],
        "depth_um": cell["depth_um"], "tone_mismatch_frac": cell["tone_mismatch_frac"],
        "beat_offset_cycles_per_symbol": offset, "noise_std": cell["noise_std"], "vector_pattern": pattern,
        "receiver": receiver, "frames": frames, "frames_passing": k, "frame_pass_share": k / frames,
        "wilson95_lower": lo, "wilson95_upper": hi, "mae": mae, "theory_frame_pass_probability": theory,
        "lpf_gain": gain, "lpf_phase_deg": math.degrees(phase), "depth_gain": g_depth,
    }


def module_hashes() -> dict[str, str]:
    files = sorted(p for p in PACKAGE.rglob("*") if p.suffix in (".py", ".json") and "__pycache__" not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def git_provenance() -> dict[str, Any]:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True,
                                timeout=10).stdout.strip()
        status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT,
                                capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return {"git_commit": None, "git_tracked_tree_clean_at_run_start": None}
    return {"git_commit": commit, "git_tracked_tree_clean_at_run_start": status == ""}


def run_benchmark(frames_per_vector: int = FRAMES_PER_VECTOR, master_seed: int = MASTER_SEED,
                  cells: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if isinstance(frames_per_vector, bool) or not isinstance(frames_per_vector, int) or frames_per_vector < 1:
        raise ValueError("frames_per_vector must be a positive integer")
    if int(master_seed) in PRIOR_SEEDS or int(master_seed) == DEV_SEED:
        raise ValueError("master_seed must be fresh (not a prior protocol seed or the development seed)")
    provenance = git_provenance()
    patterns = fixed_patterns()
    rows, paired = [], []
    for index, cell in enumerate(protocol_cells() if cells is None else cells):
        r, p = run_cell(cell, patterns, frames_per_vector, int(master_seed), index)
        rows.extend(r)
        paired.extend(p)
    return {
        "evidence_status": "SYNTHETIC. Dimensionless software model built from Part II's stated HWI mechanisms; no "
                           "physical, biological or safety claim is made; Mun Seok Lee has not reviewed or endorsed "
                           "this software.",
        "contract": {
            "frames_per_vector": frames_per_vector, "master_seed": int(master_seed),
            "development_seed_not_used_here": DEV_SEED, "vector_seed": VECTOR_SEED, "tolerance": TOLERANCE,
            "membrane_cutoff_hz": ch.MEMBRANE_CUTOFF_HZ, "reference_envelope_hz": ch.REFERENCE_ENVELOPE_HZ,
            "bias_beta": ch.BIAS_BETA, "alpha_per_m": ALPHA_PER_M,
            "module_sha256": module_hashes(), **provenance,
            "software_versions": {"python": platform.python_version(), "numpy": np.__version__,
                                  "matplotlib": matplotlib.__version__},
        },
        "sign_destroyed_by_direct_rectification_all_vectors": all(
            ch.sign_is_destroyed_by_direct_rectification(v) for v in patterns.values()),
        "rows": rows,
        "paired": paired,
    }


def validate_result(result: dict[str, Any]) -> None:
    """Raise ValueError on internal inconsistency."""
    for row in result["rows"]:
        if not 0 <= row["frames_passing"] <= row["frames"]:
            raise ValueError("pass count out of range")
        if not math.isclose(row["frame_pass_share"], row["frames_passing"] / row["frames"], abs_tol=1e-12):
            raise ValueError("share mismatch")
        lo, hi = wilson_interval(row["frames_passing"], row["frames"])
        if not (math.isclose(lo, row["wilson95_lower"], abs_tol=1e-12)
                and math.isclose(hi, row["wilson95_upper"], abs_tol=1e-12)):
            raise ValueError("Wilson interval mismatch")
    for p in (r for r in result["rows"] if r["vector_pattern"] == POOLED):
        parts = [r for r in result["rows"] if r["vector_pattern"] != POOLED and r["experiment"] == p["experiment"]
                 and cell_label(r) == cell_label(p) and r["receiver"] == p["receiver"]]
        if sum(r["frames_passing"] for r in parts) != p["frames_passing"]:
            raise ValueError("pooled count is not the sum of per-vector counts")
    for q in result["paired"]:
        if not math.isclose(q["mcnemar_p"], mcnemar_exact_p(q["a_pass_b_fail"], q["a_fail_b_pass"]), abs_tol=1e-15):
            raise ValueError("McNemar p mismatch")
    if not result["sign_destroyed_by_direct_rectification_all_vectors"]:
        raise ValueError("direct rectification must destroy the sign")


def _fmt(value: Any) -> Any:
    if isinstance(value, float):
        return f"{value:.10g}"
    return "" if value is None else value


def _write_csv(path: Path, fields: tuple[str, ...], rows: Any) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: _fmt(row[k]) for k in fields})


def write_outputs(result: dict[str, Any], validity: dict[str, Any], output_dir: Path = ARTIFACTS) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {"json": output_dir / f"{STEM}.json", "csv": output_dir / f"{STEM}.csv",
             "paired": output_dir / f"{STEM}-paired.csv", "png": output_dir / f"{STEM}.png",
             "validity_json": output_dir / "engineering-validity.json",
             "dimension_csv": output_dir / "dimension-checks.csv",
             "inventory_csv": output_dir / "equation-inventory.csv"}
    paths["json"].write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    paths["validity_json"].write_text(json.dumps(validity, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    _write_csv(paths["csv"], CSV_FIELDS, result["rows"])
    _write_csv(paths["paired"], PAIRED_FIELDS, result["paired"])
    _write_csv(paths["dimension_csv"], DIMENSION_FIELDS, validity["dimension_checks"])
    _write_csv(paths["inventory_csv"], INVENTORY_FIELDS, EQUATION_INVENTORY)
    _plot(result, paths["png"])
    return paths


def _pooled(result, experiment, receiver):
    return [r for r in result["rows"] if r["experiment"] == experiment and r["receiver"] == receiver
            and r["vector_pattern"] == POOLED]


def _plot(result: dict[str, Any], path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    ax = axes[0, 0]
    labels, values = [], []
    for row in [r for r in result["rows"] if r["experiment"] == "E1_mapping" and r["vector_pattern"] == POOLED
                and r["noise_std"] == 0.25]:
        labels.append(f"{row['mapping'].replace('single_tone_', 'st_').replace('two_tone_beat', 'beat')}\n"
                      f"{row['receiver'].replace('_calibrated', '_cal').replace('magnitude_sign_blind', '|N| only')}")
        values.append(100 * row["frame_pass_share"])
    ax.bar(range(len(values)), values, color="tab:blue")
    ax.set_xticks(range(len(values)), labels, fontsize=6, rotation=60)
    ax.set_ylabel("frames passing (%)")
    ax.set_title("E1 transmit mapping, sigma = 0.25 (|N| only: sign not decoded)", fontsize=9)
    ax = axes[0, 1]
    for receiver, style in (("nominal", "o-"), ("calibrated", "s-")):
        rows = _pooled(result, "E2_envelope_frequency", receiver)
        ax.plot([r["envelope_hz"] for r in rows], [100 * r["frame_pass_share"] for r in rows], style, label=receiver)
    ax.set_xlabel("envelope / beat frequency (Hz)")
    ax.set_ylabel("frames passing (%)")
    ax.set_title("E2 membrane low-pass (100 Hz), two-tone beat, sigma = 0.45", fontsize=9)
    ax.legend(fontsize=8)
    ax = axes[1, 0]
    for receiver, style in (("lpf_calibrated", "o-"), ("calibrated", "s-")):
        rows = _pooled(result, "E3_depth_water_0p99THz", receiver)
        ax.plot([r["depth_um"] for r in rows], [100 * r["frame_pass_share"] for r in rows], style, label=receiver)
    rows = _pooled(result, "E3_depth_water_0p99THz", "calibrated")
    ax.plot([r["depth_um"] for r in rows], [100 * r["theory_frame_pass_probability"] for r in rows], "k:",
            label="calibrated, closed form")
    ax.set_xlabel("depth in water at 0.99 THz (um), alpha = 220 /cm")
    ax.set_ylabel("frames passing (%)")
    ax.set_title("E3 Beer-Lambert depth, sigma = 0.25 at z = 0", fontsize=9)
    ax.legend(fontsize=8)
    ax = axes[1, 1]
    rows = _pooled(result, "E4_two_tone_mismatch", "calibrated")
    ax.semilogx([max(r["tone_mismatch_frac"], 3e-15) for r in rows], [100 * r["frame_pass_share"] for r in rows],
                "s-")
    ax.set_xlabel("relative THz tone-frequency error (0 plotted at 3e-15)")
    ax.set_ylabel("frames passing (%)")
    ax.set_title("E4 two-tone mismatch at 1 THz, 40 Hz beat, sigma = 0.45", fontsize=9)
    fig.suptitle("Part II THz/ELF channel: SYNTHETIC, no physical, biological or safety claim", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=120, facecolor="white", metadata={"Software": None})
    plt.close(fig)


def main() -> int:
    result = run_benchmark()
    validate_result(result)
    paths = write_outputs(result, engineering_validity_report())
    for row in result["rows"]:
        if row["vector_pattern"] == POOLED:
            print(f"{row['experiment']:<24} {cell_label(row):<64} {row['receiver']:<22} "
                  f"{row['frames_passing']:>5}/{row['frames']} theory={row['theory_frame_pass_probability']}")
    for path in paths.values():
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
