"""Locked protocol modules and vendored code: pinned here and in MODULES.sha256 (fixed in the protocol-lock commit)."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKED = {
    "d2w_thz/__init__.py": "1691c8747c76365b0a48a7ce3c02a269c9b3c016faec4b22c51867969cfd196b",
    "d2w_thz/_vendor/PROVENANCE.json": "2a9a7e73e776c906f2a46b4ae6798f02a22ba529bf13dc1964fbdface502d6b5",
    "d2w_thz/_vendor/__init__.py": "a33cb126e6ca1cd0d0d715234cecdae2002d16b20603dcb322db27fe0c82be8d",
    "d2w_thz/_vendor/digital_to_wave.py": "866cab09ae3b64387de9fc9909288dac37f9f81e7e2f6603b2e786674d46ac18",
    "d2w_thz/_vendor/testbench_v041.py": "9826c1fd4f7fbce513e0173e0e859a8b696081073e87e78a119901a46bbfef60",
    "d2w_thz/benchmark.py": "5765362b36025b27febf7a684b5d9db379403987e4f680d7bfc011ec94c05e52",
    "d2w_thz/references.py": "b6733fd7716dc7fad51b2e989555973740a64005a0fac7d7dd1f6f20f3466e03",
    "d2w_thz/thz_channel.py": "691b9cbec6a4e9f6b1812151fdb169f14f61c8164d9f27bc85b4397f0c422b6a",
    "d2w_thz/validity.py": "1eec4b089e52921217f6dde154488001380d5edb072f19890d1e32d736484294",
}


def test_modules_sha256_file_matches_pins():
    lines = (ROOT / "MODULES.sha256").read_text(encoding="utf-8").splitlines()
    assert dict(reversed(line.split("  ", 1)) for line in lines) == LOCKED


def test_locked_files_unchanged():
    for name, digest in LOCKED.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def test_every_package_file_is_locked():
    files = {p.relative_to(ROOT).as_posix() for p in (ROOT / "d2w_thz").rglob("*")
             if p.suffix in (".py", ".json") and "__pycache__" not in p.parts}
    assert files == set(LOCKED)
