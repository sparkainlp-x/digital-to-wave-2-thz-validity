# Contributing to Digital to Wave 2 THz Validity

Thank you for helping! Please read the [Code of Conduct](CODE_OF_CONDUCT.md) first. Report security issues privately as described in [SECURITY.md](SECURITY.md), not as public issues.

## Ground rules

- **Synthetic data only.** Never commit private, proprietary or personal data, correspondence or drafts. The `private/` folder is git-ignored for local notes.
- **No physical, biological or safety claims.** The channel benchmark is a dimensionless software model, and the validity analysis is an order-of-magnitude check of printed equations against cited reference values. Do not present either as evidence about tissue, neurons, brain-computer interfaces, THz hardware or exposure safety. Label evidence as SYNTHETIC, TARGET or UNRUN.
- **Locked modules stay unchanged.** The modules listed in [`MODULES.sha256`](MODULES.sha256) were fixed before the full run. New experiments go in new modules with their own protocol lock (committed, pushed and green in CI before the full run), a fresh master seed and their own tests.
- **Vendored code is verbatim.** `d2w_thz/_vendor/` is copied from the Digital to Wave Testbench v0.4.1 and checked by `tests/test_vendor_provenance.py` and `tools/verify_vendor.py`. Do not edit it; update it only by re-vendoring from a tagged testbench release and updating `PROVENANCE.json`.
- **Real measured numbers only.** Any number in the README must come from a command in this repository that anyone can rerun. Every reference value must cite its source in `d2w_thz/references.py`. Report losses and null results as honestly as wins.
- **License.** The project is AGPL-3.0-only (see [LICENSE](LICENSE) and [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)). By contributing, you agree that your contribution is licensed under the same terms.

## Development setup

```bash
python -m pip install -e ".[test]"
python -m pip install ruff
```

## Before you open a pull request

1. **Tests:** `python -m pytest` must pass (CI runs Python 3.11–3.13).
2. **Lint:** `ruff check .` must be clean.
3. **Locks and artifacts:** `sha256sum -c MODULES.sha256` must pass. If you regenerate artifacts with `tools/reproduce_all.sh`, the committed CSV/PNG files must stay byte-identical unless the change is intentional and explained.
4. **Docs:** update the README and `CHANGELOG.md` (under *Unreleased*) for any user-visible change.
