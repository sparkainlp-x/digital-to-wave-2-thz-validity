"""Equation inventory, dimensional checks and standard-reference magnitudes."""

import math

from d2w_thz import validity as v
from d2w_thz.references import REFERENCE_VALUES


def test_inventory_is_well_formed():
    ids = [e["id"] for e in v.EQUATION_INVENTORY]
    assert len(ids) == len(set(ids))
    for e in v.EQUATION_INVENTORY:
        assert set(e) == set(v.INVENTORY_FIELDS)
        assert e["paper"] in ("I", "II") and e["pages"]
        assert set(e["classes"].split(",")) <= {"a", "b", "c"}
        if e["classes"] == "c":
            assert e["used_here"] == ""
    used = {e["id"] for e in v.EQUATION_INVENTORY if "channel" in e["used_here"]}
    assert {"P1-12a", "P2-HWI-band", "P2-HWI-rect", "P2-HWI-beer", "P2-QWM-beat"} <= used


def test_dimension_checks_flag_only_p29():
    rows = v.equation_dimension_checks()
    bad = [r for r in rows if not r["consistent"]]
    assert [r["page"] for r in bad] == [29]
    assert bad[0]["rhs"] == "kg s^-2"  # intensity x time = J m^-2
    assert all(r["consistent"] for r in rows if r["page"] in (34, 35, 36, 37, 40))


def test_dim_algebra():
    assert v.VOLT * v.COULOMB == v.JOULE
    assert (v.METRE**2).label() == "m^2" and v.ONE.label() == "1"


def test_p36_and_p37_are_exact_inverses():
    c = v.coupling_volts_per_intensity(1e-12, 0.8, 1e4, 1e-5, 5e-9, 1.0, 2.0)
    assert math.isclose(10 ** v.log10_i_peak_min(0.015, 1e-12, 0.8, 1e4, 1e-5, 5e-9, 1.0, 2.0) * c, 0.015,
                        rel_tol=1e-9)


def test_engineering_values():
    rep = v.engineering_validity_report()
    assert math.isclose(rep["penetration_depth_m"]["0.99THz"], 1 / 22000.0)
    assert 0.8 < rep["assumptions"]["T_sol"] < 0.9
    surface = rep["required_intensity_by_depth"][0]
    assert surface["log10_I_peak_min_W_per_m2"] > 13  # even with a ZnTe-level chi2 upper bound
    assert rep["heating_at_surface"]["max_burst_s_for_delta_T_0p5K_no_diffusion"] < 1e-11
    assert math.isclose(rep["kBT"]["k_B_times_298K_J"], 4.114e-21, rel_tol=1e-3)
    assert 90 < rep["lgd_density_claim"]["bits_per_unit_cell"] < 100
    assert set(rep["references"]) == set(REFERENCE_VALUES)


def test_report_is_deterministic():
    assert v.engineering_validity_report() == v.engineering_validity_report()
