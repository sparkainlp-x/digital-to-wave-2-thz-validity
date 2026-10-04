"""Physical constants and standard reference values (REF) with their sources.

Values marked approx are read from published spectra. The values are chosen to favour Part II where a range exists
(see the notes); they are inputs to an order-of-magnitude check, not measurements made by this project.
"""

from __future__ import annotations

from typing import Any

C_LIGHT = 299_792_458.0          # m s^-1 (exact, SI)
EPS0 = 8.8541878128e-12          # F m^-1 (CODATA 2018)
K_B = 1.380649e-23               # J K^-1 (exact, SI)
E_CHARGE = 1.602176634e-19       # C (exact, SI)

REFERENCE_VALUES: dict[str, dict[str, Any]] = {
    "water_alpha_per_cm": {
        "value": {"0.30": 123.0, "0.60": 167.0, "0.99": 220.0, "1.98": 347.0},
        "unit": "cm^-1 (intensity absorption), key = frequency in THz",
        "source": "Xu, Plaxco & Allen, J. Chem. Phys. 124, 036101 (2006), Table I "
                  "(https://www.itst.ucsb.edu/~sjallen/Pubs/PubJChemPhys.pdf)",
    },
    "water_n_1thz": {"value": 2.1, "unit": "1", "source": "approx.; Kindt & Schmuttenmaer, J. Phys. Chem. 100, "
                     "10373 (1996), doi:10.1021/jp960141g; Thrane et al., Chem. Phys. Lett. 240, 330 (1995)"},
    "skin_note": {"value": None, "unit": "", "source": "In vivo skin is water-dominated at THz and of the same "
                  "order or higher (Pickwell et al., Phys. Med. Biol. 49, 1595 (2004), "
                  "doi:10.1088/0031-9155/49/9/001)"},
    "water_rho": {"value": 997.0, "unit": "kg m^-3", "source": "standard tables (CRC Handbook)"},
    "water_cp": {"value": 4180.0, "unit": "J kg^-1 K^-1", "source": "standard tables (CRC Handbook)"},
    "water_k": {"value": 0.6, "unit": "W m^-1 K^-1", "source": "standard tables (CRC Handbook)"},
    "membrane_thickness": {"value": 5.0e-9, "unit": "m", "source": "textbook lipid bilayer ~5 nm"},
    "membrane_eps_lf": {"value": 2.0, "unit": "1", "source": "lipid hydrocarbon core ~2 (low value favours the paper)"},
    "v_th_depolarisation": {"value": 0.015, "unit": "V", "source": "rest about -70 mV to threshold about -55 mV "
                            "(Kandel et al., Principles of Neural Science, 6th ed., 2021; cited by Part II)"},
    "chi2_upper_bound": {"value": 2.0 * 68.5e-12, "unit": "m V^-1", "source": "ZnTe d14 ~ 68.5 pm/V (chi2 = 2 d), "
                         "one of the strongest THz optical-rectification crystals; a deliberately extreme upper "
                         "bound. Bulk liquid water is centrosymmetric, so its bulk chi2 vanishes in the electric-"
                         "dipole approximation (Boyd, Nonlinear Optics, 3rd ed., 2008, sec. 1.5)"},
    "q_gating": {"value": 13.0 * E_CHARGE, "unit": "C", "source": "Shaker K+ channel ~13 e0: Aggarwal & "
                 "MacKinnon, Neuron 16, 1169 (1996), doi:10.1016/s0896-6273(00)80143-9; Schoppa et al., Science "
                 "255, 1712 (1992)"},
    "icnirp_skin_limit_long": {"value": 1000.0, "unit": "W m^-2", "source": "ICNIRP 2013 laser guidelines "
                               "(Health Phys. 105, 271), >1400 nm to 1 mm, >10 s: 10/A_s W m^-2 for 0.01-0.1 m^2 "
                               "(1000 W m^-2 at 0.01 m^2), 100 W m^-2 above 0.1 m^2"},
    "air_breakdown_field": {"value": 3.0e6, "unit": "V m^-1", "source": "standard dielectric strength of dry air"},
}


def ref(name: str) -> Any:
    """Return the value of a reference entry."""
    return REFERENCE_VALUES[name]["value"]
