# Verification and proposed testing

## Completed computational and document checks

Existing calculation records and manuscript release checks document the following completed work.

| Check | Recorded result | Scope |
|---|---|---|
| Aggregate arithmetic | Country, status and discipline totals reconcile to 125; favorable percentages reconcile to 84.0%, 86.4% and 92.0% | Checks supplied summaries, not collection history or individual responses |
| Conditional count equivalents | 105, 108 and 115 when denominator 125 is assumed | Arithmetic equivalents, not recovered response counts |
| Impact comparison | Conflicting versions identified and excluded | Discrepancy remains unresolved |
| Engineering calculations | Batch, coagulant/stock, mixing, membrane/head, ideal UV and pump arithmetic recomputed; units reviewed | Conditional mathematics, not device performance |
| Figure preservation | Prior release verifies 21 existing assets and 16 original-image hashes | Byte preservation, not scientific validation of image claims |
| Document compilation | Prior release records no undefined citations/references, overfull boxes or out-of-page characters | Document quality |
| Archive rebuild | Prior source archive compiled and all 14 rendered pages matched its delivered PDF | Reproducibility of that release |

Build checks are version-specific. Changes to author order, manuscript source, layout or figures require verification of the new build.

Repository software checks produce a separate report, such as **software_test_report.json**. Only a report from an actual run establishes which checks were executed. Passing code checks does not make an assumption a measurement or supply missing study records.

No flow field or radiation field was solved. The trajectory-fluence and LRV definitions describe required calculations; absent physical or microbial data are not replaced with synthetic observations.

## Run the repository checks

From the repository root, with Python 3.11 or newer:

```console
python -m unittest discover -s tests -v
python scripts/reproduce.py --output-dir build/reproduced --no-plots --check
python scripts/verify_repository.py
```

The reproduction command also runs the unit tests after its baseline comparison passes. Its **--check** option compares ten deterministic CSV/JSON products with committed **results/**, while **--no-plots** skips optional plotting. Checking defaults to **build/reproduced/** and rejects writing under committed **results/**. A failed comparison lists differing or missing files and exits before writing; an existing report is not evidence for that failed run. After a passing comparison, inspect the newly written **software_test_report.json** for tests run, failures and errors. These commands check software and repository integrity; they do not perform the proposed laboratory or field work below.

## Proposed experimental evaluation — not completed

This is a planning outline. The blank [templates](templates/) are record structures, not approved protocols, completed tests or acceptance criteria. Study-specific methods, endpoints and operating ranges must be documented before experiments.

| Area | Questions to evaluate | Prospective records |
|---|---|---|
| Coagulation/settling | Effects of source water, dose basis, mixing and separation on clarification and aluminium residuals | Jar tests, water characterization, replicates and volume accounting |
| Supported GO | Effects of material, support, area, pressure and feed on flux, rejection, fouling and release | Membrane runs, characterization, paired concentrations and cleaning history |
| UV-C | Exposure and microbial response under documented hydraulic, optical and water-quality conditions | UV runs linked to microbial pairs, methods and detection limits |
| Monitoring/interlocks | Calibration error, drift, disturbances and alarm/valve behavior under documented faults | Sensor/reference measurements and functional checks |
| Integrated operation | Whole-cycle volume, energy, residuals, downtime and maintenance | System runs and cost/maintenance events |
| Protected storage/use | Point-of-use quality, cleaning, dispensing and sustained actual use | A separately specified field-evaluation record linked to relevant treatment runs |

Component evidence motivates these questions; it does not answer them for BLUESHIELD. Existing manuscript keys are **r4/r5** for coagulation, **r6–r9/r17** for GO architectures, **r10–r12/epa_uv2006** for UV, **r13/r14** for monitoring, and **r2/r3** for household use. **who_hwt2018** is a prospective framework, not assigned certification or performance.

## Reporting future results

Retain source/run/sample identifiers, units, methods, replicate information, detection limits, qualifiers and quality-control status. Record dose basis, pressure measurement locations and the basis of optical quantities. Distinguish measurements from nominal settings and derived values.

A nondetect must retain its qualifier and detection limit; it must not be silently converted to zero. Paired measurements need compatible bases and documented dilution corrections. Physicochemical indicators do not establish microbial safety, and electrical power does not establish delivered fluence.

Costs and energy need a stated boundary and denominator. Pumping-only energy per volume pumped differs from total demand per volume delivered. Maintenance, idle time, consumables, rejected water and storage effects need their own records.

Future surveys require a documented instrument, recruitment plan, denominator/missingness rules and applicable participant procedures. This repository cannot retrospectively establish consent or ethics approval for the original survey.
