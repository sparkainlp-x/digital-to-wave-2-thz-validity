"""Protocol contract, seeds, reduced runs, determinism, validator and outputs."""

import copy
import csv

import pytest

from d2w_thz import benchmark as bm
from d2w_thz.validity import EQUATION_INVENTORY, engineering_validity_report


@pytest.fixture(scope="module")
def small():
    return bm.run_benchmark(frames_per_vector=5, master_seed=bm.TEST_SEED)


def test_seeds_are_fresh_and_distinct():
    assert bm.MASTER_SEED not in bm.PRIOR_SEEDS and bm.DEV_SEED not in bm.PRIOR_SEEDS
    assert len({bm.MASTER_SEED, bm.DEV_SEED, bm.TEST_SEED}) == 3
    for seed in (bm.DEV_SEED, 20261012, 20261011):
        with pytest.raises(ValueError):
            bm.run_benchmark(frames_per_vector=1, master_seed=seed)
    for bad in (0, -1, True, 2.5):
        with pytest.raises(ValueError):
            bm.run_benchmark(frames_per_vector=bad, master_seed=bm.TEST_SEED)


def test_locked_grid():
    cells = bm.protocol_cells()
    assert len(cells) == 9 + 5 + 7 + 6
    assert bm.FRAMES_PER_VECTOR == 2000 and bm.TOLERANCE == 0.25 and bm.MASTER_SEED == 20261013
    assert bm.ALPHA_PER_M == 22000.0
    assert [c["envelope_hz"] for c in cells if c["experiment"] == "E2_envelope_frequency"] == [5, 20, 40, 60, 100]


def test_small_run_validates_and_is_deterministic(small):
    bm.validate_result(small)
    again = bm.run_benchmark(frames_per_vector=5, master_seed=bm.TEST_SEED)
    assert again["rows"] == small["rows"] and again["paired"] == small["paired"]


def test_clean_cells_behave(small):
    pooled = {(r["experiment"], bm.cell_label(r), r["receiver"]): r for r in small["rows"]
              if r["vector_pattern"] == bm.POOLED}
    direct = [r for k, r in pooled.items() if k[0] == "E1_mapping" and k[1].startswith("single_tone_direct")
              and k[2] == "nominal"]
    assert len(direct) == 3 and all(r["frames_passing"] == 0 for r in direct)
    for mapping in ("two_tone_beat", "single_tone_biased"):
        clean = pooled[("E1_mapping", f"{mapping}|f_env=40Hz|z=0um|mismatch=0|sigma=0", "calibrated")]
        assert clean["frames_passing"] == clean["frames"]


def test_validator_detects_tampering(small):
    bad = copy.deepcopy(small)
    bad["rows"][0]["frames_passing"] += 1
    with pytest.raises(ValueError):
        bm.validate_result(bad)
    bad = copy.deepcopy(small)
    bad["paired"][0]["mcnemar_p"] = 0.123456
    with pytest.raises(ValueError):
        bm.validate_result(bad)
    bad = copy.deepcopy(small)
    bad["sign_destroyed_by_direct_rectification_all_vectors"] = False
    with pytest.raises(ValueError):
        bm.validate_result(bad)


def test_writes_outputs(small, tmp_path):
    paths = bm.write_outputs(small, engineering_validity_report(), tmp_path)
    for p in paths.values():
        assert p.is_file() and p.stat().st_size > 0
    with paths["inventory_csv"].open(encoding="utf-8") as handle:
        assert len(list(csv.DictReader(handle))) == len(EQUATION_INVENTORY)
