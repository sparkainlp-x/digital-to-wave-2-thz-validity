# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - not yet released (set the date at release)

### Results (SYNTHETIC; no physical, biological or safety claim)
- Full run with master seed 20261013 from lock commit `6ff37d6` (clean tree). The artifacts are `artifacts/thz-channel-benchmark{.json,.csv,-paired.csv,.png}`, `engineering-validity.json`, `dimension-checks.csv` and `equation-inventory.csv`, plus `SHA256SUMS`.
- [`reports/equation-inventory-and-validity.md`](reports/equation-inventory-and-validity.md): Part II equation inventory with pages and classes, plausibility numbers and sources. The README now has a results summary.

### Added
- Protocol lock ([`reports/protocol-lock.md`](reports/protocol-lock.md)) for the Part II THz/ELF channel benchmark and engineering-validity report: fresh master seed 20261013, 27 cells, 2,000 frames per vector.
- `d2w_thz` package:
  - `validity.py`: equation inventory with pages and classes, dimension checks, HWI equations, validity report.
  - `references.py`: cited reference values.
  - `thz_channel.py`: the channel model.
  - `benchmark.py`: the protocol.
  - `_vendor/`: testbench v0.4.1 code, verbatim, with `PROVENANCE.json`.
- Tests, CI (Python 3.11–3.13, including verification of the vendored code against the testbench tag), `tools/reproduce_all.sh` and `tools/verify_vendor.py`.
