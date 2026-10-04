"""Equation inventory and engineering-validity check of Part II's THz human-wave interface (HWI) equations.

SYNTHETIC analysis. This is an order-of-magnitude engineering check of the equations as printed, using standard
reference values (``references.REFERENCE_VALUES``). It is not a safety assessment or a peer review, and Mun Seok Lee has
not reviewed or endorsed it. Page numbers refer to the PDF pages of:

- Part I: Lee, M. S. (2026), "Digital to Wave: Paradigm Shift in Quantum Wave-Based Computing and Lab-Grown Diamond
  Memory", doi:10.5281/zenodo.21947036.
- Part II: Lee, M. S. (2026), "Digital to Wave: LGD In Situ Wave Memory-Human Wave Integrated Interface-Metaverse
  Hologram- Wave Affective AI", doi:10.5281/zenodo.21947108.

Equations are paraphrased in ASCII, not reproduced. Classes: (a) well-defined and simulatable; (b) dimensionally or
physically checkable against standard physics; (c) too vague to implement (undefined symbols or operators, no units,
or no measurable mapping).
"""

from __future__ import annotations

import math
from typing import Any

from .references import C_LIGHT, EPS0, K_B, REFERENCE_VALUES, ref

REFERENCE_THZ_HZ = 1.0e12  # this project's choice; Part II gives no single THz frequency

# --------------------------------------------------------------------------------------------------------------------
# Equation inventory
# --------------------------------------------------------------------------------------------------------------------
INVENTORY_FIELDS = ("id", "paper", "section", "pages", "equation", "classes", "used_here", "finding")


def _eq(id_, paper, section, pages, equation, classes, used_here, finding):
    return {"id": id_, "paper": paper, "section": section, "pages": pages, "equation": equation, "classes": classes,
            "used_here": used_here, "finding": finding}


EQUATION_INVENTORY: tuple[dict[str, str], ...] = (
    _eq("P1-12a", "I", "encoding", "12", "S(t) = |N| A_min sin(w t + phi), phi = pi/4 (N > 0), 5 pi/4 (N < 0)", "a,b",
        "channel input (vendored encode_wave)",
        "Well-defined. 5 pi/4 = pi + pi/4, so S = N A_min sin(w t + pi/4): signed amplitude on one fixed-phase "
        "carrier. N = 0 is not defined in the text; the testbench sends zero amplitude."),
    _eq("P1-12b", "I", "encoding", "12", "T_ijk tensor write; GHz / LGD spin-wave framing", "c", "",
        "No physical mapping or units."),
    _eq("P2-LGD-density", "II", "LGD memory", "3, 5, 11", "79.6 ZB in a 10 x 10 x 3 mm^3 LGD", "b", "validity",
        "3e-7 m^3 / (0.3567 nm)^3 = 6.6e21 diamond unit cells, i.e. about 96 bits per cell (about 12 per atom); "
        "no mechanism is given; implausible as stated."),
    _eq("P2-LGD-osc", "II", "LGD memory", "13", "damped driven oscillator for lattice modes", "b", "",
        "Standard form; no LGD parameters tied to data."),
    _eq("P2-LGD-phonon", "II", "LGD memory", "14", "phonon energy sum of hbar w (n + 1/2)", "b", "", "Standard."),
    _eq("P2-LGD-interf", "II", "LGD memory", "15", "interference intensity / energy density of superposed waves", "a",
        "", "Generic superposition; not specific to LGD."),
    _eq("P2-LGD-lattice", "II", "LGD memory", "15-16", "standing-wave lattice of nodes", "a", "", "Generic."),
    _eq("P2-LGD-phase", "II", "LGD memory", "16", "THz phase shift as integral of delta n over z", "a,b", "",
        "Standard optical path phase."),
    _eq("P2-LGD-omega", "II", "LGD memory", "17", "CVD imprint total Omega_Total", "c", "",
        "Composite symbols without definitions or units."),
    _eq("P2-LGD-sted", "II", "LGD memory", "18-19", "STED-THz locking / readout", "c", "",
        "Qualitative; no transfer function."),
    _eq("P2-HWI-band", "II", "HWI", "25, 27", "THz carrier gated at 5-60 Hz; neural band 0.5-100 Hz; membrane "
        "low-pass below 100 Hz", "a", "channel", "Used as the envelope band and a first-order 100 Hz low-pass."),
    _eq("P2-HWI-fresnel", "II", "HWI", "34", "T_sol = 4 n1 n2 / ((n1 + n2)^2 + kappa^2)", "a,b", "channel, validity",
        "Consistent; standard (lossless incident medium)."),
    _eq("P2-HWI-beer", "II", "HWI", "34", "I(z) = I0 exp(-alpha z), alpha = 2 w kappa / c, skin depth 1/alpha", "a,b",
        "channel, validity", "Consistent; standard."),
    _eq("P2-HWI-rect", "II", "HWI", "35", "P_LF = eps0 chi2 |E|^2", "a,b", "channel, validity",
        "Consistent; standard. Bulk liquid water is centrosymmetric, so chi2 = 0 in the dipole approximation."),
    _eq("P2-HWI-intensity", "II", "HWI", "35", "I = 1/2 n1 c eps0 |E|^2", "b", "validity",
        "Consistent; inside the tissue n2, not n1, applies."),
    _eq("P2-HWI-dV", "II", "HWI", "36", "dV = P_LF d / (eps0 eps_LF) = [2 chi2 T_sol exp(-alpha z) d / "
        "(n1 c eps0 eps_LF)] I", "a,b", "channel, validity", "Consistent; linear intensity-to-voltage coupling."),
    _eq("P2-HWI-Imin", "II", "HWI", "37", "I_peak,min >= dV_th / coupling (and an expanded form)", "b", "validity",
        "Consistent; the expanded form drops the kappa^2 of T_sol (about 4% for water at 1 THz)."),
    _eq("P2-HWI-std", "II", "HWI", "29", "'HWI Standard Equation' I_peak,min >= (1/D) [2 n2 c eps0 eps_LF / (chi2 d)] "
        "[((n1+n2)^2 + kappa^2) / (2 w kappa)] ln(I0/I_t) V_th", "b", "validity",
        "INCONSISTENT: the right side has units of intensity x time (J m^-2). ln(I0/I_t)/(2 w kappa) = z/c, so the "
        "exponential depth factor of p. 37 became linear; the Fresnel factor differs from p. 37; with 1/D the "
        "time-averaged intensity does not fall with duty cycle."),
    _eq("P2-HWI-thermal", "II", "HWI", "29, 38", "tau_th = rho C_p w^2 / (4 k)", "b", "validity",
        "Consistent; standard thermal-diffusion time."),
    _eq("P2-HWI-snr", "II", "HWI", "40", "SNR = q_eff dV / (k_B T)", "b", "validity",
        "Consistent. The paper's k_B T = 4.11e-21 J corresponds to about 298 K, not 310 K (4.28e-21 J)."),
    _eq("P2-QWM-fourier", "II", "QWM / BCI", "42-43", "memory 'compression' by Fourier transform", "c", "",
        "Generic FFT; no neural data model."),
    _eq("P2-QWM-copy", "II", "QWM / BCI", "43-45", "memory copy and erase operators", "c", "", "Undefined operators."),
    _eq("P2-QWM-beat", "II", "QWM / BCI", "45-47", "smartphone-brain link via two-tone THz difference frequency "
        "(0.5-50 Hz beat)", "a", "channel", "Only the beat is modelled, as a transmit mapping; nothing neural."),
    _eq("P2-QWM-stdp", "II", "QWM / BCI", "51", "STDP 'hub' equation", "c", "", "Symbols undefined."),
    _eq("P2-QWM-hippo", "II", "QWM / BCI", "54", "hippocampal tensor", "c", "", "No mapping."),
    _eq("P2-QWM-jholo", "II", "QWM / BCI", "55-57", "J_Holo / E_True", "c", "", "No units or measurement."),
    _eq("P2-HOLO-rot", "II", "hologram / CMB", "65", "Rodrigues rotation", "a", "", "Standard geometry; not specific."),
    _eq("P2-HOLO-pll", "II", "hologram / CMB", "73-74", "phase-locked loop", "a", "",
        "Standard PLL; no hologram-specific parameters."),
    _eq("P2-HOLO-rest", "II", "hologram / CMB", "64-77", "real-space hologram, CMB coupling", "c", "", ""),
    _eq("P2-WAI", "II", "wave affective AI", "86-94", "emotion-wave equations", "c", "",
        "No defined observables, units or data."),
)


# --------------------------------------------------------------------------------------------------------------------
# Dimensional analysis (exponents of m, kg, s, A, K)
# --------------------------------------------------------------------------------------------------------------------
class Dim(tuple):
    """SI dimension exponents (m, kg, s, A, K)."""

    def __new__(cls, m=0, kg=0, s=0, a=0, k=0):
        return super().__new__(cls, (m, kg, s, a, k))

    def __mul__(self, other):
        return Dim(*(x + y for x, y in zip(self, other, strict=True)))

    def __truediv__(self, other):
        return Dim(*(x - y for x, y in zip(self, other, strict=True)))

    def __pow__(self, p):
        return Dim(*(x * p for x in self))

    def label(self) -> str:
        names = ("m", "kg", "s", "A", "K")
        parts = [f"{n}^{e:g}" if e != 1 else n for n, e in zip(names, self, strict=True) if e != 0]
        return " ".join(parts) or "1"


ONE = Dim()
METRE = Dim(m=1)
SECOND = Dim(s=1)
VOLT = Dim(m=2, kg=1, s=-3, a=-1)
FARAD_PER_M = Dim(m=-3, kg=-1, s=4, a=2)
INTENSITY = Dim(kg=1, s=-3)                  # W m^-2
CHI2 = METRE / VOLT
VELOCITY = METRE / SECOND
JOULE = Dim(m=2, kg=1, s=-2)
COULOMB = Dim(s=1, a=1)
E_FIELD = VOLT / METRE


def equation_dimension_checks() -> list[dict[str, Any]]:
    """Dimensional check of each printed HWI equation (left side versus right side)."""
    rho, cp, kcond = Dim(m=-3, kg=1), Dim(m=2, s=-2, k=-1), Dim(m=1, kg=1, s=-3, k=-1)
    rows = []

    def add(name, page, lhs, rhs, note=""):
        rows.append({"equation": name, "page": page, "lhs": lhs.label(), "rhs": rhs.label(),
                     "consistent": lhs == rhs, "note": note})

    add("Fresnel normal-incidence transmissivity T_sol = 4 n1 n2 / ((n1+n2)^2 + kappa^2)", 34, ONE, ONE,
        "standard; correct form for a lossless incident medium")
    add("Beer-Lambert I(z) = I0 exp(-alpha z), alpha = 2 omega kappa / c", 34, METRE**-1, (SECOND**-1) / VELOCITY,
        "standard")
    add("Skin depth delta = 1/alpha = c / (2 omega kappa)", 34, METRE, VELOCITY / SECOND**-1,
        "standard (1/e intensity)")
    add("Rectification P_LF = eps0 chi2 |E|^2", 35, COULOMB / METRE**2, FARAD_PER_M * CHI2 * E_FIELD**2, "standard")
    add("Intensity I = 1/2 n1 c eps0 |E|^2", 35, INTENSITY, VELOCITY * FARAD_PER_M * E_FIELD**2,
        "standard; inside the target medium n2, not n1, applies")
    add("Induced potential Delta V = P_LF d / (eps0 eps_LF)", 36, VOLT, (COULOMB / METRE**2) * METRE / FARAD_PER_M,
        "consistent")
    add("Delta V = [2 chi2 T_sol exp(-alpha z) d / (n1 c eps0 eps_LF)] I_peak", 36, VOLT,
        CHI2 * METRE / (VELOCITY * FARAD_PER_M) * INTENSITY, "consistent")
    add("I_peak,min >= [n1 c eps0 eps_LF / (2 chi2 T_sol exp(-alpha z) d)] V_th", 37, INTENSITY,
        VELOCITY * FARAD_PER_M / (CHI2 * METRE) * VOLT, "consistent (inverse of p. 36)")
    add("I_peak,min >= [n1 c eps0 eps_LF (n1+n2)^2 / (8 n1 n2 chi2 d)] exp(2 omega kappa z / c) V_th", 37, INTENSITY,
        VELOCITY * FARAD_PER_M / (CHI2 * METRE) * VOLT,
        "consistent; drops the kappa^2 of T_sol (kappa ~ 0.5 for water at 1 THz: ~4% effect)")
    add("'HWI Standard Equation' I_peak,min >= (1/D) [2 n2 c eps0 eps_LF / (chi2 d)] [((n1+n2)^2 + kappa^2) / "
        "(2 omega kappa)] ln(I0/I_target) V_th", 29, INTENSITY,
        VELOCITY * FARAD_PER_M / (CHI2 * METRE) * SECOND * VOLT,
        "INCONSISTENT: the right side has units of intensity x time (J m^-2). ln(I0/I_t)/(2 omega kappa) = z/c, so "
        "the exponential depth factor of p. 37 became a linear one; the Fresnel factor also differs from p. 37")
    add("Thermal time tau_th = rho C_p w^2 / (4 k)", 29, SECOND, rho * cp * METRE**2 / kcond,
        "consistent; standard thermal-diffusion time scale")
    add("SNR = q_eff Delta V_LF / (k_B T)", 40, ONE, COULOMB * VOLT / JOULE, "consistent")
    return rows


# --------------------------------------------------------------------------------------------------------------------
# Part II HWI physics (PAPER equations evaluated with REF values)
# --------------------------------------------------------------------------------------------------------------------
def fresnel_transmittance(n1: float, n2: float, kappa: float) -> float:
    """Part II p. 34."""
    return 4.0 * n1 * n2 / ((n1 + n2) ** 2 + kappa**2)


def kappa_from_alpha(alpha_per_m: float, frequency_hz: float) -> float:
    """Invert alpha = 2 omega kappa / c (Part II p. 34)."""
    return alpha_per_m * C_LIGHT / (2.0 * 2.0 * math.pi * frequency_hz)


def coupling_volts_per_intensity(chi2: float, t_sol: float, alpha_per_m: float, z_m: float, d_m: float,
                                 n1: float, eps_lf: float) -> float:
    """Part II p. 36: Delta V / I_peak."""
    return 2.0 * chi2 * t_sol * math.exp(-alpha_per_m * z_m) * d_m / (n1 * C_LIGHT * EPS0 * eps_lf)


def log10_i_peak_min(v_th: float, chi2: float, t_sol: float, alpha_per_m: float, z_m: float, d_m: float,
                     n1: float, eps_lf: float) -> float:
    """Part II p. 37, evaluated in log10 space so deep z does not overflow."""
    base = n1 * C_LIGHT * EPS0 * eps_lf * v_th / (2.0 * chi2 * t_sol * d_m)
    return math.log10(base) + alpha_per_m * z_m / math.log(10.0)


def i_peak_min_p29_as_printed(v_th: float, chi2: float, n1: float, n2: float, kappa: float, omega: float,
                              d_m: float, eps_lf: float, attenuation_ratio: float, duty: float) -> float:
    """Part II p. 29 'HWI Standard Equation' exactly as printed (dimensionally inconsistent: the value is in J m^-2)."""
    return (1.0 / duty) * (2.0 * n2 * C_LIGHT * EPS0 * eps_lf / (chi2 * d_m)) * (
        ((n1 + n2) ** 2 + kappa**2) / (2.0 * omega * kappa)) * math.log(attenuation_ratio) * v_th


def thermal_relaxation_time(rho: float, cp: float, w_m: float, k: float) -> float:
    """Part II p. 29 / p. 38."""
    return rho * cp * w_m**2 / (4.0 * k)


def lgd_bits_per_unit_cell(bytes_claimed: float = 79.6e21, volume_m3: float = 10e-3 * 10e-3 * 3e-3,
                           lattice_m: float = 0.356_7e-9) -> dict[str, float]:
    """Part II pp. 3, 5, 11: implied storage density of the 79.6 ZB claim (diamond, 8 atoms per cubic cell)."""
    cells = volume_m3 / lattice_m**3
    bits = 8.0 * bytes_claimed
    return {"unit_cells": cells, "bits_per_unit_cell": bits / cells, "bits_per_atom": bits / (8.0 * cells)}


def engineering_validity_report() -> dict[str, Any]:
    """Dimension checks plus order-of-magnitude evaluation of the HWI equations with REF values."""
    f_thz = REFERENCE_THZ_HZ
    omega = 2.0 * math.pi * f_thz
    alpha_table = ref("water_alpha_per_cm")
    alpha = alpha_table["0.99"] * 100.0
    n1, n2 = 1.0, ref("water_n_1thz")
    kappa = kappa_from_alpha(alpha, f_thz)
    t_sol = fresnel_transmittance(n1, n2, kappa)
    chi2, d, eps_lf, v_th = (ref("chi2_upper_bound"), ref("membrane_thickness"), ref("membrane_eps_lf"),
                             ref("v_th_depolarisation"))
    rho, cp, kcond = ref("water_rho"), ref("water_cp"), ref("water_k")
    coupling0 = coupling_volts_per_intensity(chi2, t_sol, alpha, 0.0, d, n1, eps_lf)
    depths = {"surface_0um": 0.0, "one_penetration_depth": 1.0 / alpha, "100um": 1e-4, "1mm": 1e-3,
              "2mm_typical_skin_thickness": 2e-3, "10mm": 1e-2, "50mm_order_of_deep_brain_structures": 5e-2}
    icnirp = ref("icnirp_skin_limit_long")
    depth_rows = []
    for label, z in depths.items():
        log_i = log10_i_peak_min(v_th, chi2, t_sol, alpha, z, d, n1, eps_lf)
        log_e = 0.5 * (math.log10(2.0) + log_i - math.log10(C_LIGHT * EPS0 * n1))
        depth_rows.append({
            "depth_label": label, "depth_m": z, "log10_I_peak_min_W_per_m2": log_i,
            "log10_ratio_to_ICNIRP_1000_W_per_m2": log_i - math.log10(icnirp),
            "log10_incident_E_field_V_per_m": log_e,
            "log10_ratio_E_to_air_breakdown": log_e - math.log10(ref("air_breakdown_field")),
        })
    i0 = 10.0 ** depth_rows[0]["log10_I_peak_min_W_per_m2"]
    absorbed_w_per_m3 = alpha * t_sol * i0
    max_burst_for_half_kelvin = 0.5 * rho * cp / absorbed_w_per_m3
    kbt_310 = K_B * 310.0
    p29_value = i_peak_min_p29_as_printed(v_th, chi2, n1, n2, kappa, omega, d, eps_lf, math.e, 1.0)
    p37_value_at_one_depth = 10.0 ** log10_i_peak_min(v_th, chi2, t_sol, alpha, 1.0 / alpha, d, n1, eps_lf)
    return {
        "evidence_status": "SYNTHETIC order-of-magnitude engineering check of Part II's HWI equations with standard "
                           "reference values. Not a safety assessment; no physical validity of the HWI is claimed or "
                           "refuted beyond what the stated equations and references imply. Mun Seok Lee has not "
                           "reviewed or endorsed this analysis.",
        "assumptions": {"thz_frequency_hz": f_thz, "medium": "liquid water (skin is similar or higher)",
                        "alpha_per_m": alpha, "n1": n1, "n2": n2, "kappa": kappa, "T_sol": t_sol,
                        "chi2_m_per_V": chi2, "d_m": d, "eps_LF": eps_lf, "V_th_V": v_th},
        "dimension_checks": equation_dimension_checks(),
        "penetration_depth_m": {f"{k}THz": 1.0 / (v * 100.0) for k, v in alpha_table.items()},
        "coupling_V_per_W_m2_at_surface": coupling0,
        "required_intensity_by_depth": depth_rows,
        "heating_at_surface": {
            "absorbed_power_density_W_per_m3": absorbed_w_per_m3,
            "max_burst_s_for_delta_T_0p5K_no_diffusion": max_burst_for_half_kelvin,
            "thz_period_s": 1.0 / f_thz,
            "note": "T_burst < tau_th (p. 29, p. 38) limits diffusion, not the adiabatic rise within one burst. "
                    "Because p. 29 scales I_peak by 1/D, the time-averaged intensity D*I_peak does not fall with D.",
        },
        "thermal_relaxation_time_s": {f"w_{w * 1e6:g}um": thermal_relaxation_time(rho, cp, w, kcond)
                                      for w in (10e-6, 100e-6, 1e-3)},
        "kBT": {"paper_value_J": 4.11e-21, "k_B_times_310K_J": kbt_310, "k_B_times_298K_J": K_B * 298.0,
                "note": "the paper's 4.11e-21 J corresponds to ~298 K, not 310 K (~4% difference)"},
        "snr_p40_at_V_th": {"q_eff_C": ref("q_gating"), "value": ref("q_gating") * v_th / kbt_310,
                            "note": "dimensionless and plausible (~7) once Delta V = V_th is reached; it says "
                                    "nothing about whether Delta V can be reached"},
        "p29_vs_p37": {"p29_as_printed_at_ln_ratio_1_D_1_value_in_J_per_m2": p29_value,
                       "p37_at_one_penetration_depth_W_per_m2": p37_value_at_one_depth,
                       "note": "different units, so no numerical agreement is possible; p. 37 is the consistent form"},
        "lgd_density_claim": lgd_bits_per_unit_cell(),
        "references": {k: v["source"] for k, v in REFERENCE_VALUES.items()},
    }
