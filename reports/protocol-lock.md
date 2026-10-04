# Protocol lock: Part II THz/ELF channel benchmark and engineering-validity report (fixed before the full run)

**Evidence status:** this is a protocol only; no full-run results exist in this commit. All results will be
**SYNTHETIC**. **No physical, biological or safety claim is made.** Mun Seok Lee, author of the source preprints,
has not reviewed or endorsed this project. This is an exploratory software protocol, not a preregistration.

## Locked files

The modules in [`MODULES.sha256`](../MODULES.sha256) are fixed by this commit (also pinned in
`tests/test_hash_lock.py`):
- [`d2w_thz/thz_channel.py`](../d2w_thz/thz_channel.py)
- [`d2w_thz/benchmark.py`](../d2w_thz/benchmark.py)
- [`d2w_thz/validity.py`](../d2w_thz/validity.py)
- [`d2w_thz/references.py`](../d2w_thz/references.py)
- the vendored testbench code in [`d2w_thz/_vendor/`](../d2w_thz/_vendor/)

The full run is `python -m d2w_thz.benchmark` (or `tools/reproduce_all.sh`). It is executed afterwards from this lock
commit with a clean tracked tree. The results JSON records the commit, whether the tree was clean, and the SHA-256 of
every package file. `tests/test_committed_results.py` was written in this commit, before any result existed. It checks
the committed results without depending on their values:
- the contract and the module hashes
- the validator
- two full-size cells (indices 8 and 17) re-run and compared line by line with the committed CSV
- the validity and inventory artifacts against the code
- `SHA256SUMS`

## Publication plan and CI

CI (`.github/workflows/tests.yml`, Python 3.11–3.13) will run on this commit when it is pushed. The plan:
1. Push this lock commit **alone** to a new GitHub repository.
2. Wait for green CI on it.
3. Only then push the separate run commit, which adds the artifacts and the results text.
4. CI then regenerates every CSV and PNG byte for byte.

At the time of writing, the lock exists only locally; nothing has been pushed yet.

## Disclosure: this design was run before, with a different seed

This is a port, not a fresh design. The channel, receivers, grid and frame counts are identical to module v9 on the
local, unpublished branch `part2-thz-channel` of the Digital to Wave Testbench. That module was run there with master
seed 20261012 and development seed 20261112, so its results were known when this lock was written.

This project changes only the following, and nothing was tuned to those results:
- module names and structure
- the vendoring of the testbench code
- the seeds
- the separate validity, inventory and dimension artifacts

`tests/test_port_equivalence.py` re-runs two cells with seed 20261012 and confirms the port reproduces those counts
exactly. This project's results use the fresh master seed **20261013**, which no earlier run in either repository has
used. Before this lock, the only run here used the development seed **20261113**: one smoke run of all 27 cells at
100 frames per vector, to check the pipeline. Tests use seed 6262. The guard in `run_benchmark` refuses the
development seed and every prior seed.

## Sources

- **Part I, p. 12** (doi:10.5281/zenodo.21947036): `S(t) = |N|·A_min·sin(ωt + φ(N))`, with φ = π/4 for N > 0 and 5π/4
  for N < 0. Because 5π/4 = π + π/4, this is exactly `N·A_min·sin(ωt + π/4)`. The encoder and matched-filter decoder
  are vendored byte-identical from the Digital to Wave Testbench v0.4.1 (commit `f4b3934`, doi:10.5281/zenodo.23134616);
  see `d2w_thz/_vendor/PROVENANCE.json`.
- **Part II** (doi:10.5281/zenodo.21947108), page numbers of the PDF:
  - 5–60 Hz gating and a membrane low-pass below 100 Hz (pp. 25, 27)
  - rectification `P_LF = ε0·χ2·|E|²` (p. 35)
  - Fresnel and Beer–Lambert (p. 34)
  - `ΔV` linear in intensity (p. 36)
  - minimum intensity (p. 37)
  - the "HWI Standard Equation" (p. 29)
  - thermal time (pp. 29, 38)
  - SNR (p. 40)
  - two-tone THz difference-frequency beat (pp. 45–47)
- **Standard reference values** with sources are in `d2w_thz/references.py`.

## Chain

Part I frame (32 values × 64 samples, 4 carrier cycles per symbol), then one of three transmit mappings:
- **single_tone_direct:** `|E|² = S²`, so the sign is destroyed.
- **single_tone_biased:** field `1 + 0.25·S`, normalised by the known 0.5.
- **two_tone_beat:** low-pass `|E|² = (1+N²)/2 + |N|·sin(ωt + φ(N))`, with a relative THz tone error acting as a
  beat-frequency offset.

Then a first-order impulse-invariant low-pass with `f_c` = 100 Hz, at sample rate 16 × the envelope frequency and zero
initial state. Then the depth gain `exp(−α z)` with α = 220 cm⁻¹ (water at 0.99 THz; Xu et al. 2006). Then additive
white Gaussian noise of SD σ, in units of the unit-value amplitude at z = 0. The THz carrier is not sampled.

## Receivers

- **nominal:** the vendored `decode_wave`.
- **lpf_calibrated:** I/Q projection corrected by the known low-pass gain and phase.
- **calibrated:** additionally knows the depth gain. It is an oracle and is never told the tone error.
- **magnitude_sign_blind:** |N| from the symbol mean, single_tone_direct only.

A frame passes iff max |error| ≤ 0.25 over its 32 values (against |N| for magnitude_sign_blind).

## Grid

Six fixed vectors (testbench `build_input_patterns(20261004)`), 2,000 frames per vector and cell, master seed 20261013,
noise via `SeedSequence([seed, 9, cell_index, vector_index])`.

| experiment | mapping | varied | fixed |
|---|---|---|---|
| E1 | all three | σ ∈ {0, 0.25, 0.45} | f_env 40 Hz, z = 0 |
| E2 | two_tone_beat | f_env ∈ {5, 20, 40, 60, 100} Hz | σ 0.45, z = 0 |
| E3 | two_tone_beat | z ∈ {0, 5, 10, 20, 30, 50, 100} µm | σ 0.25, 40 Hz |
| E4 | two_tone_beat | relative tone error ∈ {0, 1e-14, 2.5e-14, 5e-14, 1e-13, 2e-13} at 1 THz | σ 0.45, 40 Hz, z = 0 |

## Reporting

For every vector and the pooled panel, the run reports:
- pass counts with Wilson 95% intervals
- the closed-form frame pass probability (exact clean decoder bias, noise SD σ/gain, testbench v5 formula)
- exact McNemar tests of each receiver against nominal

It also reports the engineering-validity report (dimension checks; required intensity by depth against the ICNIRP
limit and air breakdown; heating; thermal times; k_B·T; SNR; the LGD density claim) and the equation inventory.
Where a closed-form prediction falls outside its Wilson interval, this will be reported as observed, not explained
away.

## Pre-stated expectations (reported, not success criteria)

1. single_tone_direct passes 0 frames with the nominal decoder at every σ.
2. Without noise, two_tone_beat and single_tone_biased pass every frame with the calibrated receiver at 40 Hz.
3. Pooled closed-form predictions match observed shares within Monte Carlo error.
4. Only the p. 29 equation fails the dimension check.
