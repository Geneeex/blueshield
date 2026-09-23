# Data dictionary

Data are separated into **reported aggregates**, **illustrative assumptions**, **derived calculations** and **prospective measurement templates**. No current file represents respondent-level records or observed prototype performance.

## Conventions

Reported aggregates are transcribed from the supplied manuscript/graphics. Engineering assumptions are selected scenario inputs, not survey estimates. Derived values inherit their inputs' limitations. Unavailable information is not zero, “No,” a negative result or evidence of consent.

Percentages use a 0–100 scale; recoverable-volume and efficiency fractions use 0–1. Every physical quantity needs a stated unit. Missing values must not be inferred from plot appearance.

## Survey inputs

### data/demographics.csv

| Field | Meaning |
|---|---|
| group | Demographic dimension: country, participant status or discipline |
| category | Category within that dimension |
| count | Reported aggregate count, not accessible individual records |
| denominator | Reported total for that dimension |
| status | Evidence-status marker |
| source | Source description |

Country totals are 75/25/25; status totals 70/55; discipline totals 10/12/8/45/50. These are separate marginal distributions, not cross-tabulations or individual links.

### data/perceptions.csv

| Field | Meaning |
|---|---|
| item | Perception item |
| very_label, somewhat_label | Reported favorable response-category labels |
| very_pct, somewhat_pct | Reported percentages, 0–100 |
| assumed_denominator | Denominator used for conditional reconstruction |
| status, source | Evidence status and provenance |

The favorable percentage is the sum of the two categories. Applying denominator 125 produces equivalents of 105/108/115 for the principal items; these remain **conditional**. Actual item-level exports, missingness and joint distributions are unavailable.

### data/interview_summaries.csv

| Field | Meaning |
|---|---|
| item | Reported prompt, concern or agreement category |
| count | Reported count |
| denominator | Reported interview-component size, 25 |
| interpretation | Whether the count concerns a concern, agreement or another stated summary |
| status, source | Evidence status and provenance |

The six summaries are environmental conditions (20), energy efficiency or scalability (15), affordability concerns (18), public-health-benefit agreement (22), regional-factor agreement (23) and cross-border-relevance agreement (22). Categories can overlap. They must not be summed into one mutually exclusive distribution or treated as a recoverable qualitative coding matrix.

### data/impact_discrepancy.json

Records the unresolved conflict without entering unverified chart percentages.

| Field | Meaning |
|---|---|
| item | anticipated_impact |
| status | unresolved_conflicting_source_summaries |
| exclude_from_analysis | true; this item does not enter substantive analysis |
| selected_distribution | null; neither source is selected as authoritative |
| narrative_and_summary_percentages | Reported social/environmental/economic values 65.6/21.6/12.8 |
| original_pie_percentages | null; chart values have not been independently verified for transcription |
| original_pie_source | A source-provenance identifier, not a command input path |
| source, reason | Provenance and explanation of the unresolved conflict |
| resolution_needed | Original wording, response export, denominator and chart-generation evidence needed to resolve the discrepancy |

Null does not mean zero or an empty response category. The retained source graphic remains part of the manuscript record.

### data/metadata.json

Describes reported sample 125, reported interview subsample 25, source provenance and missing records. Missing recruitment, instrument, dates, transcripts and consent/ethics information are part of the dataset's interpretation.

## Engineering inputs

**data/engineering_inputs.json** organizes nine groups: cycle, alum, mixing, membrane, head, uvpath, uvvolume, energy and lrv.

| Quantity-object field | Meaning |
|---|---|
| value | Scalar or list of scenario values |
| unit | Explicit physical unit or dimensionless-fraction descriptor |
| status | illustrative_assumption for assumed engineering parameters |
| source | Scenario/manuscript basis |

Group and parameter names identify physical meaning. A cited formula does not make the selected input a measured literature value. Symbolic groups lacking measurements remain distinguishable from numerical scenarios.

Core units are L for batch volume, L/h for flow, explicitly named s/min/h for time, m² for active area, LMH for flux, explicitly named bar/Pa for pressure, mW/cm² for fluence rate and mJ/cm² for fluence. See [CALCULATIONS.md](CALCULATIONS.md) for conversions.

The main scenario uses 20 L, recoverable fraction 0.90, discharge 10 L/h, and 1/20/60 min rapid mixing/flocculation/settling. The recoverable fraction is a lumped volume allowance. No measured membrane recovery, rejection, radiation field or microbial LRV is supplied.

## Generated outputs

Generation defaults to **results/**; **--check** defaults to **build/reproduced/** and protects committed **results/** from being overwritten. These products contain calculations and checks, not new observations.

| File | Meaning |
|---|---|
| engineering_results.json | Conditional engineering quantities and context |
| equation_catalog.json | Nine equation groups, definitions and status |
| engineering_scenarios.csv | Tabular scenario results |
| survey_audit.json | Aggregate arithmetic and consistency checks |
| input_manifest.json | SHA-256 hashes of UTF-8 source CSV/JSON text after normalizing line endings to LF; these are not raw-byte file hashes |
| demographic_audit.csv | Separate demographic totals/proportions |
| perception_audit.csv | Favorable sums and conditional count equivalents |
| interview_audit.csv | Checks of overlapping prompt summaries |
| design_sensitivity.csv | Deterministic design sensitivity |
| membrane_sensitivity.csv | Area/flux sensitivity |
| software_test_report.json | Checks actually executed by software, not laboratory outcomes |

The first ten CSV/JSON products are deterministic comparison targets. The software report and optional **design_sensitivity.png** and **perception_aggregates.png** plots are excluded from the baseline comparison because environment-dependent details can differ. The uvpath and lrv groups remain function-only with no experimental inputs or calculated prototype result. Plots inherit these evidence classes; scenario curves have no fitted prototype parameters or empirical uncertainty intervals.

## Blank prospective templates

Every supplied CSV under [templates/](templates/) has **one header row and zero data rows**. They are separate from current aggregates and assumptions. Protocol identifiers are spaces to record future procedures, not evidence of approved protocols.

| Template | One future row represents |
|---|---|
| [jar_tests.csv](templates/jar_tests.csv) | A condition/replicate with water, dose basis, mixing, settling and analytical results |
| [membrane_runs.csv](templates/membrane_runs.csv) | A membrane collection interval and analyte pair |
| [uv_runs.csv](templates/uv_runs.csv) | A reactor interval and optical-quantity basis |
| [paired_microbial_results.csv](templates/paired_microbial_results.csv) | An influent/effluent pair for one organism/surrogate and compatible assay |
| [sensor_calibration.csv](templates/sensor_calibration.csv) | Sensor and reference measurements |
| [cost_maintenance.csv](templates/cost_maintenance.csv) | A cost/maintenance event with allocation basis |
| [system_runs.csv](templates/system_runs.csv) | Whole-cycle volume, time and energy accounting |

### Field rules

Identifiers link related records and are not participant names. Timestamps should include a time zone. A replicate_id denotes an actual documented repeat, not a copied row. A quality_control_status records applicable method checks or their pending status; it does not certify drinking-water safety.

**Jar tests:** dose_basis specifies commercial product or elemental Al; stock concentration must use that basis. target_dose_mg_L is a setting, not a removal result. Record material identity, lot and assay where available. Alkalinity is mg/L as CaCO₃; residual aluminium is mg/L Al.

**Membrane:** feed/retentate/permeate pressures are separate so transmembrane pressure can be calculated. Permeate volume and duration support flux calculation. Feed and permeate qualifiers retain analytical-limit information. Rejection needs compatible concentration units and methods; material release has its own result, unit and method.

**UV:** wavelength and optical path define the transmittance measurement. fluence_basis distinguishes nominal/model estimates, measured fluence and documented reduction-equivalent-dose determinations. fluence_rate_method_id identifies the supporting method. Electrical power is separate and cannot replace an optical measurement. Blank fields remain unknown.

**Microbial pairs:** retain values, qualifiers, detection limits, sample volumes and dilution-correction basis. A below_detection_limit qualifier needs the actual method context; never replace it with zero solely to obtain an LRV. run_id links the pair to treatment conditions.

**Sensors:** parameter and unit apply to sensor/reference values. Preserve the raw reading and any correction separately, with a correction version.

**Cost/maintenance:** record currency, quantity, evidence and allocation basis. Avoid repeating a run's total volume/energy across event rows when aggregating. **System runs** separately record product, residual, sampling and retained volumes, complete-cycle delays and energy categories.
