# Editable BLUESHIELD concept models

Eight self-contained Blender scenes support the manuscript's six treatment stages, integrated machine, and industrial installation. Open any file in `scenes/` with Blender 4.3 or later; native reopening was checked with Blender 4.3.2.

**[Explore the model gallery](../docs/MODEL_GALLERY.md)** to see all eight labeled publication figures with links to the original renders and editable scenes.

| Basename | Scene |
| --- | --- |
| `01_Intake_and_Screen` | Screened intake and feed pump |
| `02_Coagulation_and_Flocculation` | Alum dosing, rapid mixing, and flocculation |
| `03_Settling_and_Sludge` | Settling and separate sludge withdrawal |
| `04_Supported_GO_Cartridge` | Supported, immobilized graphene-oxide cartridge cutaway |
| `05_Terminal_UVC_Reactor` | Closed terminal UV-C reactor |
| `06_Protected_Storage_and_Sensing` | Protected storage and sensing |
| `07_Integrated_Machine` | Connected treatment skid, pressure-control provisions, and divert path |
| `08_Industrial_Installation` | Conceptual installation, operations area, and service access |

These are explanatory concepts, not dimensioned fabrication drawings, CFD or optical simulations, pressure-vessel designs, or validation of treatment performance. Sizes and component spacing illustrate the arrangement. The manuscript supplies the engineering assumptions and limitations.

## Files and provenance

- `scenes/*_clean.blend`: editable public-release scenes. Equipment geometry, object transforms, materials, cameras, and lights match the source scenes. Floating explanatory text and the presentation floor were already hidden in the source clean scenes; device nameplates remain.
- `renders/archive/*_clean.png`: unchanged transparent 2600 × 1750 raster renders used for the published flat-label figures. No duplicate JPEG backgrounds are needed: the label script derives them from these PNGs.
- `clean_model_manifest.json`: preserved camera-projected label anchors and original cleaning metadata. Its historical `source_sha256` fields refer to the earlier publication scenes, **not** the sanitized files in `scenes/`.
- `sanitization_manifest.json`: original clean-scene SHA-256 hashes, public-copy hashes, exact font substitutions, file sizes, dependency audits, and native-reopen preservation checks.
- `assets_manifest.json`: hashes and sizes of the bundled scene/render assets and preserved layout metadata.
- `verification.json`: packaging checks and archived-render label reproduction results.

The canonical publication PDFs are in [`../manuscript/latex/figures`](../manuscript/latex/figures), and editable labeled SVGs are in [`../manuscript/latex/editable_figure_labels`](../manuscript/latex/editable_figure_labels). Those publication assets are unchanged by scene sanitization.

### Public-copy changes

The source scenes contained packed Microsoft Segoe UI font files. Every text-curve font slot in the public copies now uses Blender's built-in Bfont, and all other font datablocks and packed font binaries were removed. Render output paths are relative; saved file-browser directory buffers were cleared. No external images, linked libraries, or embedded scripts remain in the scenes.

Font substitution changes glyph outlines and text bounds, while retaining the text body, text-object placement, and equipment geometry. Re-rendering the sanitized native scenes is therefore **not guaranteed to reproduce the archived pixels**, and nameplates should be visually checked after edits. Blender version, renderer, and hardware can also affect raster output. The archived renders retain the publication appearance without distributing font software.

## Regenerate flat labels from archived renders

From the repository root, with Python 3.10 or later:

```sh
python -m pip install -r models/requirements.txt
python models/scripts/label_model_figures.py
```

Outputs go to `models/generated/labels/`: PDF, editable self-contained SVG, PNG preview, cropped JPEG background, and layout verification JSON. The PDF keeps the leader lines and legends as vectors. Stage legends are 11 pt at their native 3.3-inch width. PDF font references use the standard Helvetica family; the script does not bundle font binaries.

Pass a basename to regenerate one plate, or `--output` to choose another output directory:

```sh
python models/scripts/label_model_figures.py 05_Terminal_UVC_Reactor
```

Using the pinned dependencies, all eight regenerated previews matched the archived labeled previews pixel for pixel, and all SVGs and JPEG backgrounds matched byte for byte. PDF timestamps can differ.

## Inspect or re-render the native scenes

The render wrapper uses Python's standard library. Put Blender on `PATH`, or supply its executable using `--blender`:

```sh
python models/scripts/render_models.py --blender "/path/to/blender" --inspect
python models/scripts/render_models.py --blender "/path/to/blender"
```

The first command only opens and audits the scenes. The second exports clean transparent PNGs and updated projected anchors to `models/generated/renders/`; it does not save changes to the scene files. Omit `--blender` when Blender is on `PATH`. Add one or more scene basenames to process a subset. `--dry-run` prints the command without running Blender.

To label new renders with their matching anchor manifest:

```sh
python models/scripts/label_model_figures.py --renders models/generated/renders --manifest models/generated/renders/clean_model_manifest.json --output models/generated/new_labels
```

Review generated plates before replacing manuscript assets, especially if component geometry, camera framing, nameplates, or labels have changed.

`scripts/sanitize_scenes.py` records the public-copy conversion. It can process a separately supplied directory of original clean scenes through Blender's `--python` option and requires `--source` after Blender's `--` separator. Original proprietary font files are not included here. Geometry/material/camera signatures were compared before conversion and after saving and reopening every bundled scene; all matched, excluding the explicitly changed font references and derived glyph bounds.
