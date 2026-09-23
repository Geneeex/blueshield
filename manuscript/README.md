# Manuscript and publication assets

`BLUESHIELD_FILTER.pdf` is the supplied final 14-page manuscript. `latex/BLUESHIELD_BINAVO.tex` retains its source bytes and author order: Sabik Bin Sultan, then Shafi Bin Sultan. The manuscript's 28 figures, three tables and nine numbered equation groups are preserved.

`latex/figures/` contains the publication assets; `latex/editable_figure_labels/` contains the eight editable model-label SVGs. Figure captions and the reference list are maintained in the LaTeX source. `latex/FIGURE_PROVENANCE.json` records attribution, image preservation and source licenses; `latex/FIGURE_SECTION_MAP.json` records placement. `PRIOR_LAYOUT_REPORT.json` is the earlier manuscript-layout audit, not new scientific validation.

## Optional PDF rebuild

Install a pdfLaTeX distribution with the packages used in the preamble, including IEEEtran, cite, amsmath, amssymb, graphicx, textcomp, booktabs, array, placeins, etoolbox, xurl, multicol, needspace and hyperref. A reasonably complete TeX Live or MiKTeX installation is appropriate.

Download the LaTeX template from [IEEE Access's official author page](https://ieeeaccess.ieee.org/authors/preparing-your-article/). This release was built with [`ACCESS_latex_template_20260513`](https://ieeeaccess.ieee.org/wp-content/uploads/2026/05/ACCESS_latex_template_20260513-1-1.zip). The 44 required dependency hashes are recorded in `template_dependencies.json`; this public repository does not redistribute the standalone template fonts. Preserve the downloaded ZIP outside the tracked repository.

From the repository root:

```console
python scripts/build_manuscript.py --template-zip /path/to/official_template.zip
```

On Windows, use a quoted Windows path for the ZIP. If needed, add `--pdflatex "path/to/pdflatex.exe"`. An extracted template can instead be supplied with `--template-dir /path/to/template`.

The helper validates each dependency, stages the build in a temporary directory and runs three passes with shell execution disabled. The output goes to `build/manuscript/BLUESHIELD_FILTER.pdf`. It never overwrites the archived paper. Changed upstream template files are rejected so that silent layout drift is not mistaken for the original build; the manifest should only be updated after reviewing and checking a newer template build.

PDF timestamps, identifiers and compiler versions can alter the rebuilt file hash even when page appearance is identical. The local release verification includes a page-render comparison using the matching template.

## Scientific interpretation

Rebuilding a PDF verifies document production. It does not verify raw survey records, ethics procedures, experimental performance or journal readiness. Read [the study scope](../docs/STUDY_SCOPE.md) for those limits.
