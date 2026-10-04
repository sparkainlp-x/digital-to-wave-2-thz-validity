# Digital to Wave 2 THz Validity

**An engineering-validity study of the THz human-wave interface (HWI) equations in Mun Seok Lee's *Digital to Wave* Part II preprint.** It has three parts:
- an equation inventory with page numbers;
- dimensional checks and standard-reference plausibility numbers;
- a seeded, protocol-locked synthetic channel benchmark that carries the Part I signed-amplitude sine encoding through Part II's THz/ELF mechanisms.

[![tests](https://github.com/sparkainlp-x/digital-to-wave-2-thz-validity/actions/workflows/tests.yml/badge.svg)](https://github.com/sparkainlp-x/digital-to-wave-2-thz-validity/actions/workflows/tests.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![Python 3.11–3.13](https://img.shields.io/badge/python-3.11%E2%80%933.13-blue.svg)](.github/workflows/tests.yml)
[![Status: research prototype](https://img.shields.io/badge/status-research%20prototype-orange.svg)](#scope-what-it-is-not)

Evidence tags: **SYNTHETIC** means produced by code in this repository; rerun it yourself. **TARGET** means planned, not done. **UNRUN** means not executed.

## Scope: what it is not

**No physical, biological or safety claim is made.**

- **Not a model of tissue, neurons, ion channels, the brain, a brain–computer interface or THz hardware.** The channel benchmark is dimensionless after an explicit normalisation. It borrows only the functional form of Part II's mechanisms: square-law rectification, a 100 Hz low-pass, Beer–Lambert depth loss and two-tone beating.
- **Not a safety assessment.** The validity numbers are order-of-magnitude evaluations of the printed equations with cited reference values. They show what the equations themselves imply. They are not exposure calculations for any device.
- **Not a review or endorsement by the source author.** Mun Seok Lee is credited as the author of the source equations only. He has not reviewed or endorsed this software.
- **Not a preregistration.** Conditions were fixed in a [protocol lock](reports/protocol-lock.md) before the full run. The lock commit is meant to be pushed and pass CI before the results. The design was ported from an earlier local run with another seed, which the lock discloses.

## Sources and attribution

> Lee, Mun Seok (2026). *Digital to Wave: LGD In Situ Wave Memory-Human Wave Integrated Interface-Metaverse Hologram- Wave Affective AI.* Preprint (Part II; patent pending), Zenodo. https://doi.org/10.5281/zenodo.21947108 (all versions: [10.5281/zenodo.21947107](https://doi.org/10.5281/zenodo.21947107)). CC BY 4.0.

> Lee, Mun Seok (2026). *Digital to Wave: Paradigm Shift in Quantum Wave-Based Computing and Lab-Grown Diamond Memory.* Preprint (Part I), Zenodo. https://doi.org/10.5281/zenodo.21947036 (all versions: [10.5281/zenodo.21464222](https://doi.org/10.5281/zenodo.21464222)). CC BY 4.0.

Page numbers refer to the PDF pages. Equations are paraphrased; no text or figures from the preprints are redistributed.

The Part I encoder, the matched-filter decoder and the statistics helpers are **vendored verbatim** from the [Digital to Wave Testbench](https://github.com/sparkainlp-x/digital-to-wave-testbench) v0.4.1 (commit `f4b3934`, doi:[10.5281/zenodo.23134616](https://doi.org/10.5281/zenodo.23134616)). See [`d2w_thz/_vendor/PROVENANCE.json`](d2w_thz/_vendor/PROVENANCE.json), which records the file, commit and SHA-256 of every vendored file and definition.

## Layout

| path | content |
|---|---|
| [`d2w_thz/validity.py`](d2w_thz/validity.py) | Equation inventory (page and class a/b/c), SI dimension checks, Part II HWI equations, engineering-validity report |
| [`d2w_thz/references.py`](d2w_thz/references.py) | Physical constants and standard reference values, each with its source |
| [`d2w_thz/thz_channel.py`](d2w_thz/thz_channel.py) | Transmit mappings, membrane low-pass, depth gain, receivers |
| [`d2w_thz/benchmark.py`](d2w_thz/benchmark.py) | Locked protocol (seeds, grid), statistics, validator, artifacts, plot |
| [`d2w_thz/_vendor/`](d2w_thz/_vendor/) | Verbatim testbench v0.4.1 code and its provenance |
| [`reports/protocol-lock.md`](reports/protocol-lock.md) | Protocol fixed before the full run |
| [`tests/`](tests/) | Vendor provenance, hash lock, channel exactness, validity, protocol, port equivalence, committed-result checks |
| [`tools/`](tools/) | `reproduce_all.sh` and `verify_vendor.py` (checks the vendored code against a testbench checkout) |
| `artifacts/` | Generated JSON/CSV/PNG with `SHA256SUMS` (added by the run commit) |

## Why vendored rather than a Git dependency

The testbench is a flat set of top-level modules. It is not on PyPI, and it pins the same NumPy/Matplotlib versions. Vendoring was chosen over a Git dependency for three reasons:
- **Zenodo is self-contained.** The Zenodo archive of a release contains everything needed to run it. A Git dependency would fetch code from GitHub at install time, and that code is not part of the archive.
- **No network for the core code.** CI and users do not need the network to install the core code.
- **Verifiable.** The provenance is mechanically checked. `tests/test_vendor_provenance.py` checks the recorded hashes offline. CI also checks out the testbench at tag `v0.4.1` and runs `tools/verify_vendor.py` against it.

## Install and usage

```bash
python -m pip install -e ".[test]" ruff
python -m pytest              # tests
ruff check .                  # lint
sha256sum -c MODULES.sha256   # locked modules unchanged
python -m d2w_thz.benchmark   # full protocol (about 20 s), writes artifacts/
tools/reproduce_all.sh        # same, and refreshes artifacts/SHA256SUMS
```

## Results

Pending. The results are added by the run commit, after CI is green on the protocol-lock commit.

## Limitations

- The channel is dimensionless. Noise is IID Gaussian in units of the unit-value amplitude at z = 0. The THz carrier is not sampled; its |E|² is averaged analytically.
- The membrane is an idealised first-order low-pass with a zero initial state. At 5 Hz (fs = 80 Hz) it is close to all-pass.
- The `calibrated` receiver is an oracle: it knows the low-pass and depth gains. No carrier, gain or timing recovery is attempted.
- The validity numbers use an extreme χ⁽²⁾ upper bound (ZnTe level). Bulk liquid water has χ⁽²⁾ = 0 in the dipole approximation, so real tissue is expected to be far weaker.
- Water at 0.99 THz stands in for skin; in vivo skin is of the same order or higher. One frequency (1 THz) is evaluated in detail.
- The fixed six-vector panel and the tolerance (0.25) are testbench choices.

## Citation

See [CITATION.cff](CITATION.cff). Please also cite the Part II preprint (source of the equations), the Part I preprint (source of the encoding) and the testbench.

## License

This software is available under the GNU Affero General Public License v3.0 only (AGPL-3.0-only); see [LICENSE](LICENSE).

Organizations that want to use it in proprietary products or services without AGPL obligations can contact the author about a commercial license via https://sparkainlpx.xyz. See [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md).
