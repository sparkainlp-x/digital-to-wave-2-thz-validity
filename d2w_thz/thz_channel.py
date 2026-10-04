"""Part I encoding through a dimensionless channel built from Part II's THz/ELF human-wave-interface equations.

SYNTHETIC and dimensionless after an explicit normalisation. No physical, biological or safety claim is made: nothing
here models a real tissue, ion channel, brain, THz source or receiver. Mun Seok Lee has not reviewed or endorsed it.

Chain (the THz carrier itself is not sampled; its |E|^2 is averaged analytically over THz cycles, which is exact for
the 1e12 Hz vs <= 1e2 Hz separation):

  Part I segments -> transmit mapping -> square-law rectified envelope r(t) (P_LF = eps0 chi2 |E|^2, Part II p. 35)
  -> membrane first-order low-pass at 100 Hz (pp. 25, 27) -> Beer-Lambert depth gain exp(-alpha z) (p. 34; Delta V is
  linear in intensity, p. 36) -> additive white Gaussian noise (dimensionless, in units of the z = 0 unit-value
  amplitude) -> receiver.

Transmit mappings:
- ``single_tone_direct``: the Part I waveform drives the THz field amplitude, so |E|^2 = S^2. S(N)^2 = S(-N)^2, so the
  sign of every value is destroyed; only |N| survives (a sign-blind magnitude receiver is reported).
- ``single_tone_biased``: field 1 + beta*S with beta = 0.25 (always positive); |E|^2 = 1 + 2 beta S + beta^2 S^2,
  normalised by the known 2 beta. The DC and 2w terms are orthogonal to the w matched filter over full cycles.
- ``two_tone_beat``: two THz tones (amplitudes 1 and |N|, relative phase set per symbol; Part II pp. 45-47); the
  low-pass |E|^2 is (1 + N^2)/2 + |N| sin(w t + phi(N)), i.e. exactly S plus a DC term. A relative tone-frequency error
  shifts the beat frequency like a carrier-frequency offset.

Receivers: ``nominal`` (the vendored testbench ``decode_wave``: no low-pass or depth knowledge), ``lpf_calibrated``
(I/Q projection corrected for the known low-pass gain and phase at the carrier), ``calibrated`` (low-pass and the
known depth gain; an oracle reference that is never told a tone-frequency error) and ``magnitude_sign_blind``
(|N| from the symbol mean, ``single_tone_direct`` only).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from ._vendor.digital_to_wave import WaveConfig, decode_wave, encode_wave
from .validity import REFERENCE_THZ_HZ

CONFIG = WaveConfig()
VECTOR_LENGTH = 32
SAMPLES_PER_SYMBOL = CONFIG.samples_per_symbol
CYCLES_PER_SYMBOL = CONFIG.cycles_per_symbol
FRAME_SAMPLES = VECTOR_LENGTH * SAMPLES_PER_SYMBOL
OMEGA = 2.0 * math.pi * CYCLES_PER_SYMBOL / SAMPLES_PER_SYMBOL
BIAS_BETA = 0.25
MAPPINGS = ("single_tone_direct", "single_tone_biased", "two_tone_beat")

# Part II parameters (PAPER).
MEMBRANE_CUTOFF_HZ = 100.0          # p. 25: low-pass characteristics below 100 Hz
GATING_BAND_HZ = (5.0, 60.0)        # p. 27: gating / envelope at 5-60 Hz
REFERENCE_ENVELOPE_HZ = 40.0        # this project's choice inside the paper's band


def lpf_coefficient(cutoff_hz: float, sample_rate_hz: float) -> float:
    """Impulse-invariant first-order low-pass: y[n] = a y[n-1] + (1-a) x[n]."""
    if cutoff_hz <= 0 or sample_rate_hz <= 0:
        raise ValueError("cut-off and sample rate must be positive")
    return math.exp(-2.0 * math.pi * cutoff_hz / sample_rate_hz)


def sample_rate_hz(envelope_hz: float) -> float:
    """Sample rate that keeps the testbench's 64 samples per 4 envelope cycles."""
    return SAMPLES_PER_SYMBOL / CYCLES_PER_SYMBOL * envelope_hz


def lpf_response(a: float, omega: float = OMEGA) -> tuple[float, float]:
    """Gain and phase (rad) of the discrete low-pass at normalised angular frequency omega."""
    h = (1.0 - a) / (1.0 - a * complex(math.cos(omega), -math.sin(omega)))
    return abs(h), math.atan2(h.imag, h.real)


def apply_lpf(x: np.ndarray, a: float) -> np.ndarray:
    """Causal first-order low-pass along the last axis, zero initial state (silence before the frame)."""
    x = np.asarray(x, dtype=float)
    y = np.empty_like(x)
    state = np.zeros(x.shape[:-1])
    for n in range(x.shape[-1]):
        state = a * state + (1.0 - a) * x[..., n]
        y[..., n] = state
    return y


def depth_gain(depth_m: float, alpha_per_m: float) -> float:
    """Beer-Lambert intensity gain exp(-alpha z) (Part II p. 34)."""
    if depth_m < 0 or alpha_per_m < 0:
        raise ValueError("depth and alpha must be non-negative")
    return math.exp(-alpha_per_m * depth_m)


def transmit(values: Any, mapping: str, beat_offset_cycles_per_symbol: float = 0.0) -> np.ndarray:
    """Normalised rectified envelope r(t) for one frame (length 32*64) before the membrane low-pass."""
    vector = np.asarray(values, dtype=float)
    segments = encode_wave(vector, CONFIG)
    s = segments.reshape(-1)
    if mapping == "single_tone_direct":
        return s**2
    if mapping == "single_tone_biased":
        field = 1.0 + BIAS_BETA * s
        return field**2 / (2.0 * BIAS_BETA)
    if mapping == "two_tone_beat":
        n_global = np.arange(s.size, dtype=float)
        ramp = 2.0 * math.pi * beat_offset_cycles_per_symbol * n_global / SAMPLES_PER_SYMBOL
        local = np.tile(OMEGA * np.arange(SAMPLES_PER_SYMBOL, dtype=float), vector.size)
        phase = np.repeat(np.where(vector < 0.0, 5.0 * math.pi / 4.0, math.pi / 4.0), SAMPLES_PER_SYMBOL)
        amplitude = np.repeat(np.abs(vector) * CONFIG.amplitude_min, SAMPLES_PER_SYMBOL)
        return 0.5 * (1.0 + amplitude**2) + amplitude * np.sin(local + phase + ramp)
    raise ValueError(f"unknown mapping {mapping!r}")


def decode_calibrated(stream: np.ndarray, gain: float, phase: float) -> np.ndarray:
    """I/Q projection per symbol, rotated by the known phase and divided by the known gain."""
    frames = np.asarray(stream, dtype=float).reshape(-1, VECTOR_LENGTH, SAMPLES_PER_SYMBOL)
    theta = OMEGA * np.arange(SAMPLES_PER_SYMBOL, dtype=float) + math.pi / 4.0
    c = frames @ np.sin(theta)
    q = frames @ np.cos(theta)
    half = SAMPLES_PER_SYMBOL / 2.0
    return (c * math.cos(phase) + q * math.sin(phase)) / (half * gain * CONFIG.amplitude_min)


def decode_nominal(stream: np.ndarray) -> np.ndarray:
    """The vendored testbench matched-filter decoder, frame by frame."""
    frames = np.asarray(stream, dtype=float).reshape(-1, SAMPLES_PER_SYMBOL)
    return decode_wave(frames, CONFIG).reshape(-1, VECTOR_LENGTH)


def decode_magnitude(stream: np.ndarray) -> np.ndarray:
    """Sign-blind |N| from the symbol mean of S^2 (mean |N|^2 A^2 / 2), for single_tone_direct only."""
    frames = np.asarray(stream, dtype=float).reshape(-1, VECTOR_LENGTH, SAMPLES_PER_SYMBOL)
    return np.sqrt(np.maximum(0.0, 2.0 * frames.mean(axis=2))) / CONFIG.amplitude_min


def sign_is_destroyed_by_direct_rectification(values: Any) -> bool:
    """True if S(N)^2 equals S(-N)^2 up to floating-point rounding (exact in real arithmetic)."""
    v = np.asarray(values, dtype=float)
    return bool(np.allclose(transmit(v, "single_tone_direct"), transmit(-v, "single_tone_direct"), rtol=0, atol=1e-12))


def beat_offset_from_tone_mismatch(mismatch_frac: float, thz_hz: float = REFERENCE_THZ_HZ,
                                   envelope_hz: float = REFERENCE_ENVELOPE_HZ) -> float:
    """Relative THz tone-frequency error -> beat-frequency offset in cycles per symbol (4 cycles at f_env)."""
    return mismatch_frac * thz_hz / envelope_hz * CYCLES_PER_SYMBOL
