#!/usr/bin/env bash
# Regenerate every artifact from the locked protocol (about 20 s) and refresh artifacts/SHA256SUMS.
set -euo pipefail
cd "$(dirname "$0")/.."
python -m d2w_thz.benchmark
(cd artifacts && sha256sum -- *.csv *.json *.png > SHA256SUMS)
