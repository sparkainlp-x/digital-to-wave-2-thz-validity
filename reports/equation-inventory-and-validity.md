# Part II equation inventory and engineering-validity check of the HWI equations

**Evidence status: SYNTHETIC analysis.** This is an order-of-magnitude engineering check of the equations as printed,
using standard reference values. It is not a safety assessment and not a peer review. **No physical, biological or
safety claim is made.** Mun Seok Lee has not reviewed or endorsed this analysis.

The inventory is data in [`d2w_thz/validity.py`](../d2w_thz/validity.py) (`EQUATION_INVENTORY`), exported to
[`artifacts/equation-inventory.csv`](../artifacts/equation-inventory.csv). The numbers come from
`engineering_validity_report()` and are stored in
[`artifacts/engineering-validity.json`](../artifacts/engineering-validity.json) and
[`artifacts/dimension-checks.csv`](../artifacts/dimension-checks.csv). They do not depend on any random seed.

**Source.** Lee, M. S. (2026), *Digital to Wave: LGD In Situ Wave Memory-Human Wave Integrated Interface-Metaverse
Hologram- Wave Affective AI*, Zenodo, doi:10.5281/zenodo.21947108 (CC BY 4.0). Page numbers refer to that PDF. Equations are
paraphrased, not reproduced.

**Classes.**
- **(a)** well-defined and simulatable.
- **(b)** dimensionally or physically checkable against standard physics.
- **(c)** too vague to implement: undefined symbols or operators, no units, or no measurable mapping.

## 1. Part I equation used as the channel input (Part I, doi:10.5281/zenodo.21947036, p. 12)

| equation | class | finding |
|---|---|---|
| `S(t) = \|N\|·A_min·sin(ωt + φ)`, with φ = π/4 (N > 0) and 5π/4 (N < 0) | a, b | Well-defined. Because 5π/4 = π + π/4, it is exactly `N·A_min·sin(ωt + π/4)`: signed amplitude (2-PAM-like) on one fixed-phase carrier. N = 0 is not defined in the text; the testbench sends zero amplitude. Vendored byte-identical from the testbench v0.4.1 (`d2w_thz/_vendor/digital_to_wave.py`). |
| T_ijk tensor write and the GHz/LGD spin-wave framing (same section) | c | No physical mapping or units; not modelled. |

## 2. Part II inventory

### LGD in-situ wave memory (pp. 3–19)

| page | equation or model | class | note |
|---|---|---|---|
| 3, 5, 11 | 79.6 ZB in a 10×10×3 mm³ LGD | b | 3×10⁻⁷ m³ ÷ (0.3567 nm)³ ≈ 6.6×10²¹ unit cells, so ≈ 96 bits per cell (≈ 12 bits per carbon atom). No mechanism for this is given; physically implausible as stated. |
| 13 | damped driven oscillator for lattice modes | b | Standard form. Generic; no LGD parameters are tied to data. |
| 14 | phonon energy sum `Σ ħω(n + ½)` | b | Standard. |
| 15 | interference intensity / energy density of superposed waves | a | Generic superposition; simulatable but not specific to LGD. |
| 15–16 | standing-wave lattice of nodes | a | Generic. |
| 16 | THz phase-shift integral `∫ Δn dz` | a, b | Standard optical path phase. |
| 17 | CVD imprint total Ω_Total | c | Composite symbols without definitions or units. |
| 18–19 | STED–THz locking / readout | c | Qualitative; no transfer function. |

### Human Wave Interface (pp. 20–40): the part modelled here

| page | equation | class | dimension check | note |
|---|---|---|---|---|
| 25, 27 | THz carrier gated or modulated at 5–60 Hz; neural response band 0.5–100 Hz; low-pass below 100 Hz | a | — | Used as the envelope band and a first-order 100 Hz low-pass. |
| 34 | Fresnel `T = 4n₁n₂/((n₁+n₂)² + κ²)` | a, b | consistent | Standard (lossless incident medium). |
| 34 | Beer–Lambert `I(z) = I₀e^(−αz)`, `α = 2ωκ/c`, skin depth 1/α | a, b | consistent | Standard. |
| 35 | `P_LF = ε₀χ⁽²⁾\|E\|²` (optical rectification) | a, b | consistent | Standard. Bulk liquid water is centrosymmetric, so χ⁽²⁾ = 0 in the dipole approximation. |
| 35 | `I = ½n₁cε₀\|E\|²` | b | consistent | Inside the tissue n₂, not n₁, applies. |
| 36 | `ΔV = P_LF·d/(ε₀ε_LF)` and `ΔV = [2χ⁽²⁾T e^(−αz) d/(n₁cε₀ε_LF)]·I` | a, b | consistent | Linear intensity-to-voltage coupling. |
| 37 | `I_peak,min ≥ ΔV_th / coupling`, plus an expanded form | b | consistent | The expanded form drops the κ² of T (≈ 4% for water at 1 THz). |
| 29 | "HWI Standard Equation" `I_peak,min ≥ (1/D)[2n₂cε₀ε_LF/(χ⁽²⁾d)][((n₁+n₂)²+κ²)/(2ωκ)] ln(I₀/I_t) V_th` | b | **INCONSISTENT** | Its right side has units of intensity × time (J m⁻²), not W m⁻². `ln(I₀/I_t)/(2ωκ)` equals z/c, so the exponential depth factor of p. 37 becomes linear. The Fresnel factor differs from p. 37. With the 1/D scaling, the time-averaged intensity D·I_peak does not fall with duty cycle. |
| 29, 38 | `τ_th = ρC_p w²/(4k)` | b | consistent | Standard thermal-diffusion time. |
| 40 | `SNR = q_eff ΔV/(k_B T)` | b | consistent | The paper's k_B T = 4.11×10⁻²¹ J corresponds to ≈ 298 K, not 310 K (4.28×10⁻²¹ J). |

### Quantum Wave Memory / BCI (pp. 41–57)

| page | equation | class | note |
|---|---|---|---|
| 42–43 | memory "compression" by Fourier transform | c (a as a generic FFT) | No neural data model. |
| 43–45 | memory copy and erase operators | c | Undefined operators. |
| 45–47 | smartphone↔brain link via a two-tone THz difference frequency (0.5–50 Hz beat) | a for the beat itself | Only the beat is modelled as a transmit mapping; nothing neural. |
| 51 | STDP "hub" equation | c | Symbols undefined. |
| 54 | hippocampal tensor | c | No mapping. |
| 55–57 | J_Holo / E_True | c | No units or measurement. |

### Metaverse hologram / CMB (pp. 64–77)

| page | equation | class | note |
|---|---|---|---|
| 65 | Rodrigues rotation | a | Standard geometry, not specific. |
| 73–74 | phase-locked loop | a | Standard PLL; no hologram-specific parameters. |
| remainder | real-space hologram, CMB coupling | c | |

### Wave affective AI (pp. 86–94)

| page | equation | class | note |
|---|---|---|---|
| 86–94 | emotion-wave equations | c | No defined observables, units or data. |

The phrase "Digital to Wave 2" does not appear in the PDF; the paper calls itself the second paper / Part II.

## 3. Plausibility of the HWI equations with standard reference values

**Assumptions.** These deliberately favour the paper:
- liquid water at 1 THz: n₂ = 2.1, α = 220 cm⁻¹ (0.99 THz), which gives κ = 0.525 and T = 0.850
- χ⁽²⁾ = 1.37×10⁻¹⁰ m/V, the ZnTe level (d₁₄ ≈ 68.5 pm/V), an extreme upper bound because water's bulk value is 0
- d = 5 nm, ε_LF = 2
- ΔV_th = 15 mV (−70 → −55 mV)

| quantity | value (from the run) |
|---|---|
| coupling at surface (p. 36) | 2.19×10⁻¹⁶ V per W m⁻² |
| penetration depth 1/α (Xu et al.) | 81 µm at 0.30 THz, 60 µm at 0.60 THz, 45 µm at 0.99 THz, 29 µm at 1.98 THz |
| I_peak,min at 0 / 45 µm / 100 µm / 1 mm / 2 mm / 10 mm (p. 37) | 10^13.8 / 10^14.3 / 10^14.8 / 10^23.4 / 10^32.9 / 10^109.4 W m⁻² |
| ratio to the ICNIRP long-exposure skin limit (1000 W m⁻² at 0.01 m²) at the surface | 10^10.8 |
| incident field at the surface | 10^8.36 V m⁻¹ ≈ 76× the dielectric strength of dry air (3 MV m⁻¹); ≈ 4.5×10⁶× at 1 mm |
| absorbed power density at the surface | 1.28×10¹⁸ W m⁻³; adiabatic ΔT = 0.5 K after ≈ 1.6 ps (< 2 THz periods) |
| τ_th (p. 29) for w = 10 µm / 100 µm / 1 mm | 0.17 ms / 17 ms / 1.74 s |
| SNR at ΔV = V_th (p. 40), q_eff = 13 e₀ | 7.3: plausible, but it does not show that ΔV_th can be reached |


**Findings.**
1. The p. 34–37 and p. 40 HWI chain is dimensionally consistent standard physics.
2. The p. 29 headline equation is not dimensionally consistent and should not be used numerically.
3. Even with an extreme χ⁽²⁾ upper bound, the required intensity at the skin surface is about 10¹¹ times the ICNIRP
   long-exposure limit. The implied field would ionise air. Water-dominated tissue absorbs THz within tens of µm, so any
   neural depth (mm) needs physically meaningless intensities (> 10²³ W m⁻² at 1 mm).
4. The two-tone beat (pp. 45–47) is a standard way to make a low-frequency envelope. The channel benchmark shows it needs THz
   tone stability better than about 2.5×10⁻¹⁴ relative at 1 THz to carry the Part I code at 40 Hz (README, E4).

## 4. Sources

- Xu, J., Plaxco, K. W., Allen, S. J. (2006). Absorption spectra of liquid water and aqueous buffers between 0.3 and 3.72 THz. *J. Chem. Phys.* 124, 036101, Table I. https://www.itst.ucsb.edu/~sjallen/Pubs/PubJChemPhys.pdf
- Kindt, J. T., Schmuttenmaer, C. A. (1996). Far-infrared dielectric properties of polar liquids probed by femtosecond THz pulse spectroscopy. *J. Phys. Chem.* 100, 10373. doi:10.1021/jp960141g. Also Thrane, L. et al. (1995), *Chem. Phys. Lett.* 240, 330.
- Pickwell, E. et al. (2004). In vivo study of human skin using pulsed terahertz radiation. *Phys. Med. Biol.* 49, 1595. doi:10.1088/0031-9155/49/9/001
- ICNIRP (2013). Guidelines on limits of exposure to laser radiation of wavelengths between 180 nm and 1,000 µm. *Health Phys.* 105, 271–295.
- Boyd, R. W. (2008). *Nonlinear Optics*, 3rd ed., sec. 1.5 (χ⁽²⁾ vanishes in centrosymmetric media).
- Aggarwal, S. K., MacKinnon, R. (1996). Contribution of the S4 segment to gating charge in the Shaker K⁺ channel. *Neuron* 16, 1169. doi:10.1016/s0896-6273(00)80143-9. Also Schoppa, N. E. et al. (1992), *Science* 255, 1712.
- ZnTe d₁₄ ≈ 68.5 pm/V: standard electro-optic/THz rectification literature value.
- Water ρ, C_p, k: CRC Handbook. Neural resting and threshold potentials: Kandel et al., *Principles of Neural Science*, 6th ed. (2021).
