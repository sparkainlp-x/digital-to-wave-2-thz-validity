"""The vendored testbench code is byte-identical / verbatim to what PROVENANCE.json records (tag v0.4.1)."""

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("verify_vendor", ROOT / "tools" / "verify_vendor.py")
verify_vendor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_vendor)
PROV = json.loads((ROOT / "d2w_thz" / "_vendor" / "PROVENANCE.json").read_text(encoding="utf-8"))


def test_provenance_metadata():
    assert PROV["tag"] == "v0.4.1"
    assert PROV["commit"] == "f4b39343e7dac983a06238795bc2b7f42c5f94b5"
    assert PROV["zenodo_version_doi"] == "10.5281/zenodo.23134616"
    assert PROV["zenodo_concept_doi"] == "10.5281/zenodo.23122876"


def test_whole_file_copy_matches_recorded_hash():
    for item in PROV["whole_files"]:
        data = (ROOT / item["vendored_as"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == item["sha256"]
        assert PROV["source_file_sha256"][item["source_file"]] == item["sha256"]


def test_extracted_definitions_match_recorded_hashes():
    segments = verify_vendor.top_level_segments(
        (ROOT / "d2w_thz" / "_vendor" / "testbench_v041.py").read_text(encoding="utf-8"))
    names = [item["name"] for item in PROV["extracted_definitions"]]
    assert names == ["VECTOR_SEED", "WILSON_Z_95", "build_input_patterns", "wilson_interval", "TOLERANCE",
                     "_finite_nonnegative", "theoretical_frame_pass_probability", "mcnemar_exact_p"]
    for item in PROV["extracted_definitions"]:
        assert hashlib.sha256(segments[item["name"]].encode("utf-8")).hexdigest() == item["sha256"], item["name"]
    # Nothing else is defined in the vendored module.
    assert set(segments) == set(names)


def test_vendored_behaviour_spot_checks():
    from d2w_thz._vendor.digital_to_wave import decode_wave, encode_wave
    from d2w_thz._vendor.testbench_v041 import mcnemar_exact_p, theoretical_frame_pass_probability, wilson_interval

    values = [-2.0, -0.5, 0.0, 1.25]
    assert max(abs(a - b) for a, b in zip(decode_wave(encode_wave(values)), values, strict=True)) < 1e-12
    lo, hi = wilson_interval(5, 10)
    assert 0.23 < lo < 0.24 and 0.76 < hi < 0.77
    assert mcnemar_exact_p(0, 0) == 1.0
    assert abs(theoretical_frame_pass_probability([0.0] * 32, 0.45) - 0.9478) < 1e-3
