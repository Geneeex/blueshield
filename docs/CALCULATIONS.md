# Calculation reference

These nine groups follow the manuscript's preliminary engineering assessment. **Every numerical scenario input is illustrative. None is fitted to survey ratings or measured on a BLUESHIELD prototype.** Outputs are conditional calculations.

Inputs record values, units, status and source. Regenerate outputs when inputs change; retain full precision internally and round only for display.

## Reproduce the committed calculations

From the repository root, using Python 3.11 or newer:

```console
python scripts/reproduce.py --output-dir build/reproduced --no-plots --check
```

Core calculations and tests need only the Python standard library. This command first compares ten deterministic CSV/JSON products with the committed **results/** files. A missing or different baseline produces a nonzero exit status and lists the affected files without writing outputs. If the comparison passes, it runs the software tests and writes regenerated results and **build/reproduced/software_test_report.json**. Test or plot-generation failures also produce a nonzero exit status. The software report and PNGs are excluded from baseline comparison. With **--check**, the default output directory is **build/reproduced/** and writing under committed **results/** is rejected. Without **--check**, the default is **results/**.

Optional scientific plots require the package specified in the repository's plot requirements:

```console
python -m pip install -r requirements-plots.txt
python scripts/reproduce.py --output-dir build/with-plots --check
```

The nine groups below correspond to **cycle**, **alum**, **mixing**, **membrane**, **head**, **uvpath**, **uvvolume**, **energy** and **lrv** in the input and output catalogs. Function-only groups remain explicitly uncalculated where no physical measurements are supplied.

## 1. Batch volume and cycle throughput — eq:cycle

$$
V_p=f_rV_b,\qquad
t_{\mathrm{cycle}}=t_{\mathrm{rapid}}+t_{\mathrm{floc}}+t_{\mathrm{settle}}+\frac{V_p}{Q_p},
\qquad \overline Q_p=\frac{V_p}{t_{\mathrm{cycle}}}.
$$

Use litres, L/h and hours consistently.

| Assumption | Value |
|---|---:|
| Raw volume, $V_b$ | 20 L |
| Recoverable fraction, $f_r$ | 0.90 |
| Discharge flow, $Q_p$ | 10 L/h |
| Rapid mixing / flocculation / settling | 1 / 20 / 60 min |

Product volume is **18 L**. Pretreatment takes 81 min = 1.35 h, discharge takes 1.80 h and the cycle takes **3.15 h**. Average output is **5.7142857 L/h**, displayed as 5.71 L/h.

The recoverable fraction is a lumped volume allowance, not measured membrane recovery. Filling, cleaning, operator delays and stock-solution volume are omitted. Parallel tanks require a separate scheduling and mass-balance model.

## 2. Coagulant mass and stock volume — eq:alum

$$
m_a[\mathrm{g}]=\frac{D[\mathrm{mg/L}]V_b[\mathrm{L}]}{1000},
\qquad V_s[\mathrm{L}]=\frac{DV_b}{C_s}.
$$

Dose $D$ and stock concentration $C_s$ must use the **same material mass basis**. The example uses commercial-product mass.

| Assumed dose for 20 L | Product mass | Stock addition at 10,000 mg/L |
|---|---:|---:|
| 10 mg/L | 0.20 g | 20 mL |
| 30 mg/L | 0.60 g | 60 mL |
| 50 mg/L | 1.00 g | 100 mL |

These are accounting examples, not dose recommendations. Product grade, hydration state and assay matter. Elemental-Al dose is not interchangeable with commercial-product dose. Jar tests must establish conditions for the actual water (**epa_turbidity2004**). Include stock addition in a final volume balance.

## 3. Bulk mixing power — eq:mixing

$$
G=\sqrt{\frac{P_w}{\mu V}},\qquad P_w=\mu VG^2.
$$

$G$ is a bulk velocity gradient in s⁻¹; $P_w$ is power dissipated into water in W; dynamic viscosity $\mu$ is in Pa·s; water volume $V$ is in m³ (**epa_nutrient2010**).

For assumed $\mu=10^{-3}$ Pa·s and $V=0.020$ m³:

- 700 s⁻¹ gives **9.8 W**.
- 50 s⁻¹ gives **0.050 W**.

These are fluid powers, not motor electrical demand or impeller-speed specifications. The relation does not resolve local shear or determine settling-removal efficiency.

## 4. Membrane flux, apparent permeance and rejection — eq:membrane

$$
J=\frac{Q_p}{A_m},\qquad L_{p,\mathrm{app}}=\frac{J}{\Delta P},
\qquad R_i=1-\frac{C_{p,i}}{C_{f,i}}.
$$

$J$ is in L·m⁻²·h⁻¹ (LMH), $Q_p$ in L/h and active area $A_m$ in m². With pressure in bar, apparent permeance is in LMH/bar. Feed/permeate concentrations require matching units and analytical bases. $R_i$ is a fraction; multiply by 100 for percent rejection.

For cross-flow, approximate transmembrane pressure is

$$
\Delta P=\frac{P_f+P_r}{2}-P_p,
$$

using feed, retentate and permeate pressures. It differs from total pump differential pressure. The definitions are consistent with **r9**; its reported performance is not a BLUESHIELD input.

At 10 L/h, assumed fluxes of 10, 25 and 50 LMH require **1.00, 0.40 and 0.20 m²**. A 50% fall from 25 LMH through 0.40 m² gives **5 L/h**.

Apparent permeance depends on solution and operating conditions. Osmotic effects, salinity and concentration polarization must be considered in a desalination model. No paired concentration measurements establish BLUESHIELD rejection.

## 5. Hydrostatic pressure — eq:head

$$
\Delta P=\rho gh.
$$

With $\rho=1000$ kg/m³, $g=9.81$ m/s² and $h=0.50$ m, pressure is **4,905 Pa = 0.04905 bar**.

A hypothetical linear permeance of 25 LMH/bar would give **1.22625 LMH**, requiring approximately **8.15494 m²** for 10 L/h. Conversely, 1 bar corresponds to about **10.1937 m** of water head.

This illustration neglects additional losses and does not predict actual low-pressure GO performance. A laboratory pressure/flux result cannot be assigned to a compact gravity vessel without demonstrating compatible conditions.

## 6. UV fluence along a trajectory — eq:uvpath

$$
H_j=\int_0^{t_j}E_f(\mathbf{x}_j(t),t)\,\mathrm{d}t.
$$

$E_f$ is in-water fluence rate along trajectory $j$, $t_j$ is exposure time and $H_j$ is delivered fluence (**epa_uv2006**). In mW/cm² and seconds, fluence is in mJ/cm².

No measured radiation field or resolved reactor trajectories are available. This group states a governing relation, not a simulated or experimentally validated dose distribution.

## 7. Ideal UV volume — eq:uvvolume

$$
H_{\mathrm{nom}}=\overline E_f\frac{V_{\mathrm{UV}}}{Q},
\qquad V_{\mathrm{UV,ideal}}=\frac{QH_{\mathrm{study}}}{\overline E_f}.
$$

This is a uniform-field, plug-flow scenario. Convert 10 L/h to $10/3600$ L/s before using mW/cm² and mJ/cm².

| Assumed fluence rate | Exposure for assumed 40 mJ/cm² | Ideal water volume at 10 L/h |
|---|---:|---:|
| 0.25 mW/cm² | 160 s | 0.444444 L |
| 0.50 mW/cm² | 80 s | 0.222222 L |
| 1.00 mW/cm² | 40 s | 0.111111 L |

Volume excludes the lamp sleeve and displaced solids. **40 mJ/cm² is an illustrative study value, not a safety threshold or validated setpoint.** Nominal residence time and electrical wattage do not establish reduction-equivalent dose. No conversion from the original 6-W lamp label to these optical assumptions is made (**epa_uv2006**).

## 8. Pump work and specific energy — eq:energy

$$
P_{\mathrm{el}}=\frac{\Delta P_{\mathrm{tot}}Q_{\mathrm{pump}}}{\eta_{\mathrm{sys}}},
\qquad e_{\mathrm{pump}}=\frac{\Delta P_{\mathrm{tot}}}{3.6\times10^6\eta_{\mathrm{sys}}}.
$$

Use Pa and m³/s. Power is W; specific energy is kWh per m³ **pumped**, not necessarily per m³ of product (**doe_pump2005**).

| Assumed differential | Efficiency | Power at 10 L/h | Pumping energy |
|---|---:|---:|---:|
| 0.5 bar | 0.30 | 0.462963 W | 0.0462963 kWh/m³ |
| 2.0 bar | 0.30 | 1.851852 W | 0.1851852 kWh/m³ |

These scenarios do not imply equal membrane flux. Recirculation, pump operating point and small-pump losses affect actual demand. Total treatment energy also requires mixing, UV, control, standby and cleaning measurements per actual delivered volume.

## 9. Microbial log reduction — eq:lrv

$$
\mathrm{LRV}_i=\log_{10}\left(\frac{N_{\mathrm{in},i}}{N_{\mathrm{out},i}}\right),
\qquad \eta_i=1-10^{-\mathrm{LRV}_i}.
$$

Numerator and denominator must concern the same viable/infective organism, compatible concentrations and assay basis. $\eta_i$ is a dimensionless removal fraction.

No paired BLUESHIELD measurements are available, so no measured LRV is reported. A nondetect is an assay-limit statement, not numerical zero; an LRV bound requires actual detection-limit information. Stage reductions cannot be assembled from unrelated studies. **who_hwt2018** informs prospective evaluation without assigning this concept a performance class.

## Existing manuscript sources

| Key | Source and role |
|---|---|
| **epa_turbidity2004** | U.S. EPA, *LT1ESWTR Turbidity Provisions Technical Guidance Manual*, EPA 816-R-04-007, 2004; jar-test context. [Source](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=30005ZHV.TXT) |
| **epa_nutrient2010** | U.S. EPA, *Nutrient Control Design Manual*, EPA/600/R-10/100, 2010, §9.6.2.1; general mixing relation, not a treatment dose. [Source](https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1008KTD.TXT) |
| **r9** | H. Liu et al., *Nature Communications* 15, 164, 2024; defined membrane experiments. [DOI](https://doi.org/10.1038/s41467-023-44626-9) |
| **epa_uv2006** | U.S. EPA, *Ultraviolet Disinfection Guidance Manual*, EPA 815-R-06-007, 2006; fluence and validation. [Source](https://www.epa.gov/system/files/documents/2022-10/ultraviolet-disinfection-guidance-manual-2006.pdf) |
| **doe_pump2005** | U.S. DOE, *Test for Pumping System Efficiency*, Tip Sheet 4, 2005; hydraulic work. [Source](https://www1.eere.energy.gov/manufacturing/tech_assistance/pdfs/test_pumping_system__pumping_systemts4.pdf) |
| **who_hwt2018** | WHO, *Harmonized Testing Protocol—Technology Non-Specific*, v2.1, 2018; prospective microbial evaluation. [Source](https://www.who.int/docs/default-source/wash-documents/water-safety-and-quality/household-water-treatment/hwt-scheme-harmonized-test-protocol-2018.pdf) |
