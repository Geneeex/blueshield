# Local release verification

This is the supplied archive-preparation record. Current repository checks are reported separately in [GitHub Actions](https://github.com/Geneeex/blueshield/actions/workflows/reproduce.yml).

Verified on 23 September 2026. These checks concern reproducibility and file quality; they do not establish treatment performance or validate unavailable source records.

| Check | Result | Evidence |
|---|---|---|
| Unit tests | 41 passed; no failures, errors or skips | [Python 3.12 report](python312_reproduction.json), [Python 3.13 report](python313_reproduction.json) |
| Core reproduction | All 10 deterministic JSON/CSV files match committed results on Python 3.12.14 and 3.13.5 | Same reports |
| Engineering coverage | Nine equation groups; unmeasured rejection, trajectory fluence and LRV are explicitly not reported as prototype results | [Equation catalogue](../results/equation_catalog.json) |
| Plot generation | Two PNGs generated with Matplotlib 3.11.2; labels, values and spacing visually reviewed | [Generation report](../results/software_test_report.json) |
| Manuscript build | Three passes using 44 hash-matched external template dependencies; no overfull boxes or undefined citations/references | [Build record](manuscript_build.json) |
| Manuscript appearance | All 14 rebuilt pages match the archived PDF pixel for pixel at 108 dpi | [Render comparison](manuscript_rebuild.json) |
| Native models | Eight scenes reopened in Blender 4.3.2; geometry/material/camera signatures preserved | [Model checks](../models/verification.json) |
| Figure-label regeneration | Eight preview images match archived pixels; SVG and JPEG outputs match bytes | [Model checks](../models/verification.json) |
| Prospective laboratory sheets | Seven CSVs; header row only and zero measurement rows | [Templates](../docs/templates/) |
| Citation metadata | CITATION.cff passes the official CFF 1.2.0 schema | [Metadata checks](metadata_checks.json) |
| Workflow configuration | YAML parses; six planned OS/Python combinations | [Metadata checks](metadata_checks.json) |

The exact-layout template emits a TS1/times font-substitution warning. This is recorded in the build report; the rebuilt page appearance still matches the archived paper. No native scene rerender is claimed: scene reopening and archived-image relabeling were tested separately. Public scene fonts differ from the archived render fonts as documented in the model README.

Python 3.11 and the GitHub-hosted Windows/Linux matrix have not been run locally. The workflow is configured to execute after upload; no remote CI pass is claimed.

The release integrity manifest records the files actually packaged. Verify it with:

```console
python scripts/verify_repository.py
```

A checksum match only establishes file identity. It does not prove scientific validity, safe drinking-water production, study consent, publication acceptance or completeness of unavailable records.
