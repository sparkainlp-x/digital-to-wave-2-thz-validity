"""Checks on the committed full-run artifacts. Skipped in the protocol-lock commit, which has no results yet.

Written before the full run: the checks do not depend on what the results are.
"""

import csv
import hashlib
import json
import math

import pytest

from d2w_thz import benchmark as bm
from d2w_thz.validity import EQUATION_INVENTORY, INVENTORY_FIELDS, engineering_validity_report

ART = bm.ARTIFACTS
RESULT = ART / f"{bm.STEM}.json"
pytestmark = pytest.mark.skipif(not RESULT.is_file(), reason="no committed results (protocol-lock commit)")
RECHECK_CELLS = (8, 17)  # E1 two-tone sigma 0.45; E3 depth 20 um (fixed in the protocol lock)


@pytest.fixture(scope="module")
def result():
    return json.loads(RESULT.read_text(encoding="utf-8"))


def test_contract_and_provenance(result):
    c = result["contract"]
    assert c["master_seed"] == bm.MASTER_SEED and c["frames_per_vector"] == bm.FRAMES_PER_VECTOR
    assert c["git_tracked_tree_clean_at_run_start"] is True and c["git_commit"]
    assert c["module_sha256"] == bm.module_hashes()  # the code is unchanged since the run
    bm.validate_result(result)
    assert len({(r["experiment"], bm.cell_label(r)) for r in result["rows"]}) == len(bm.protocol_cells())


def test_two_cells_rerun_at_full_size_match_committed_csv():
    with (ART / f"{bm.STEM}.csv").open(encoding="utf-8") as handle:
        committed = list(csv.DictReader(handle))
    cells = bm.protocol_cells()
    for index in RECHECK_CELLS:
        rows, _ = bm.run_cell(cells[index], bm.fixed_patterns(), bm.FRAMES_PER_VECTOR, bm.MASTER_SEED, index)
        label = bm.cell_label(cells[index])
        mine = [{k: str(bm._fmt(r[k])) for k in bm.CSV_FIELDS} for r in rows]
        theirs = [r for r in committed if r["experiment"] == cells[index]["experiment"] and bm.cell_label(
            {k: (float(r[k]) if k != "mapping" else r[k]) for k in ("mapping", "envelope_hz", "depth_um",
                                                                    "tone_mismatch_frac", "noise_std")}) == label]
        assert mine == theirs, label


def _close(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b, strict=True))
    if isinstance(a, float):
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=0.0)
    return a == b


def test_validity_and_inventory_artifacts_match_code():
    committed = json.loads((ART / "engineering-validity.json").read_text(encoding="utf-8"))
    assert _close(committed, json.loads(json.dumps(engineering_validity_report(), sort_keys=True)))
    with (ART / "equation-inventory.csv").open(encoding="utf-8") as handle:
        assert list(csv.DictReader(handle)) == [{k: e[k] for k in INVENTORY_FIELDS} for e in EQUATION_INVENTORY]


def test_sha256sums():
    lines = (ART / "SHA256SUMS").read_text(encoding="utf-8").split("\n")
    entries = dict(reversed(line.split("  ", 1)) for line in lines if line)
    assert set(entries) == {p.name for p in ART.iterdir() if p.suffix in (".csv", ".json", ".png")}
    for name, digest in entries.items():
        assert hashlib.sha256((ART / name).read_bytes()).hexdigest() == digest, name
