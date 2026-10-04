"""The port reproduces the design it was ported from, bit for bit.

The channel was first written as module v9 on the local, unpublished branch ``part2-thz-channel`` of the Digital to
Wave Testbench and run there with master seed 20261012. Running two of its cells here with that seed (via
``run_cell``, which bypasses the fresh-seed guard of ``run_benchmark``) must give the same pooled counts. This checks
the port only; 20261012 is never used for this project's results.
"""

from d2w_thz import benchmark as bm

TESTBENCH_V9_SEED = 20261012
# (cell index, receiver) -> pooled frames passing out of 12,000 in the testbench-branch run.
EXPECTED = {
    (8, "nominal"): 2488, (8, "lpf_calibrated"): 10662, (8, "calibrated"): 10662,      # E1 two-tone, sigma 0.45
    (19, "nominal"): 0, (19, "lpf_calibrated"): 0, (19, "calibrated"): 830,             # E3 depth 50 um
}


def test_port_matches_testbench_branch_counts():
    cells = bm.protocol_cells()
    patterns = bm.fixed_patterns()
    for index in (8, 19):
        rows, _ = bm.run_cell(cells[index], patterns, 2000, TESTBENCH_V9_SEED, index)
        pooled = {r["receiver"]: r["frames_passing"] for r in rows if r["vector_pattern"] == bm.POOLED}
        for receiver, count in pooled.items():
            assert count == EXPECTED[(index, receiver)], (index, receiver)
