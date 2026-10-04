"""Channel exactness: Part I identity, sign destruction, low-pass response, calibrated inversion, tone mismatch."""

import math

import numpy as np
import pytest

from d2w_thz import thz_channel as ch
from d2w_thz._vendor.digital_to_wave import decode_wave, encode_wave
from d2w_thz.benchmark import fixed_patterns

PATTERNS = fixed_patterns()
MIXED = PATTERNS["mixed_signs"]


def test_part1_equation_is_a_signed_amplitude_sine():
    # phi = 5*pi/4 is pi + pi/4, so S(N) = N * A_min * sin(w n + pi/4) for every N.
    n = np.arange(64)
    expected = np.outer(MIXED, np.sin(2 * np.pi * 4 / 64 * n + np.pi / 4))
    assert np.allclose(encode_wave(MIXED), expected, atol=1e-12)


def test_direct_rectification_destroys_sign():
    for vector in PATTERNS.values():
        assert ch.sign_is_destroyed_by_direct_rectification(vector)


def test_beat_and_biased_mappings_recover_values_without_lowpass():
    for mapping in ("two_tone_beat", "single_tone_biased"):
        r = ch.transmit(MIXED, mapping)
        assert np.allclose(decode_wave(r.reshape(32, 64)), MIXED, atol=1e-12)


def test_unknown_mapping_rejected():
    with pytest.raises(ValueError):
        ch.transmit(MIXED, "nope")


def test_magnitude_receiver_recovers_abs_values_on_clean_direct_stream():
    r = ch.transmit(MIXED, "single_tone_direct")
    assert np.allclose(ch.decode_magnitude(r[None, :])[0], np.abs(MIXED), atol=1e-12)


def test_lowpass_response_matches_steady_state_sine():
    a = ch.lpf_coefficient(100.0, 640.0)
    gain, phase = ch.lpf_response(a)
    n = np.arange(4000)
    y = ch.apply_lpf(np.sin(ch.OMEGA * n), a)
    tail = slice(2000, None)
    assert np.allclose(y[tail], gain * np.sin(ch.OMEGA * n[tail] + phase), atol=1e-9)
    with pytest.raises(ValueError):
        ch.lpf_coefficient(0.0, 640.0)


def test_calibrated_receiver_inverts_known_gain_and_phase():
    a = ch.lpf_coefficient(100.0, ch.sample_rate_hz(40.0))
    gain, phase = ch.lpf_response(a)
    clean = ch.apply_lpf(ch.transmit(MIXED, "two_tone_beat"), a)
    est = ch.decode_calibrated(clean[None, :], gain, phase)[0]
    assert np.max(np.abs(est - MIXED)) < 0.05  # residual is the low-pass start-up and symbol-edge transient


def test_depth_gain_is_beer_lambert():
    assert math.isclose(ch.depth_gain(1 / 22000.0, 22000.0), math.exp(-1))
    with pytest.raises(ValueError):
        ch.depth_gain(-1.0, 1.0)


def test_beat_offset_mapping():
    assert math.isclose(ch.beat_offset_from_tone_mismatch(2.5e-14), 0.0025, rel_tol=1e-12)
