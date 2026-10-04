#!/usr/bin/env python3
"""Verify the vendored testbench code against a checkout of the Digital to Wave Testbench at tag v0.4.1.

Usage: python tools/verify_vendor.py PATH_TO_TESTBENCH_CHECKOUT

Checks, using d2w_thz/_vendor/PROVENANCE.json: the checkout's commit (if it is a Git checkout), the SHA-256 of every
upstream source file, the byte-identical whole-file copy, and that every extracted definition is character for
character the same in the upstream file and in the vendored module.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVENANCE = ROOT / "d2w_thz" / "_vendor" / "PROVENANCE.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def top_level_segments(source: str) -> dict[str, str]:
    """Map each top-level def/class/assignment name to its exact source text."""
    out = {}
    for node in ast.parse(source).body:
        name = getattr(node, "name", None)
        if name is None and isinstance(node, ast.Assign | ast.AnnAssign):
            target = node.targets[0] if isinstance(node, ast.Assign) else node.target
            name = getattr(target, "id", None)
        if name is not None:
            out[name] = ast.get_source_segment(source, node)
    return out


def verify(upstream: Path) -> list[str]:
    prov = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    errors = []
    if (upstream / ".git").exists():
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=upstream, capture_output=True, text=True,
                              check=True).stdout.strip()
        if head != prov["commit"]:
            errors.append(f"upstream HEAD {head} != recorded commit {prov['commit']}")
    for name, digest in prov["source_file_sha256"].items():
        if sha256_bytes((upstream / name).read_bytes()) != digest:
            errors.append(f"upstream {name}: SHA-256 differs from PROVENANCE.json")
    for item in prov["whole_files"]:
        up = sha256_bytes((upstream / item["source_file"]).read_bytes())
        local = sha256_bytes((ROOT / item["vendored_as"]).read_bytes())
        if not up == local == item["sha256"]:
            errors.append(f"{item['vendored_as']}: not byte-identical to upstream {item['source_file']}")
    vendored_cache: dict[str, dict[str, str]] = {}
    for item in prov["extracted_definitions"]:
        up_segments = top_level_segments((upstream / item["source_file"]).read_text(encoding="utf-8"))
        path = item["vendored_in"]
        if path not in vendored_cache:
            vendored_cache[path] = top_level_segments((ROOT / path).read_text(encoding="utf-8"))
        up_text = up_segments.get(item["name"])
        local_text = vendored_cache[path].get(item["name"])
        if up_text is None or local_text is None or up_text != local_text:
            errors.append(f"{item['name']}: vendored text differs from upstream {item['source_file']}")
        elif sha256_bytes(up_text.encode("utf-8")) != item["sha256"]:
            errors.append(f"{item['name']}: SHA-256 differs from PROVENANCE.json")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    errors = verify(Path(argv[1]))
    for e in errors:
        print(f"FAIL: {e}")
    if not errors:
        print("vendored code matches the testbench checkout")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
