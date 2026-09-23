# Third-party notices and source attribution

The manuscript is a research manuscript with a BINAVO LABS masthead. No publisher endorsement or acceptance is implied. Original software contributions by Sabik Bin Sultan are covered by the [MIT License](LICENSE.md) within the [documented code-only scope](LICENSING.md). Other original contributions and third-party content retain their existing reuse terms.

## Reproduced research figures

The following attribution is carried forward from the final manuscript and its provenance record. Each figure caption identifies the external experiment and distinguishes it from BLUESHIELD measurements. Full citations are in the paper and [references.csv](manuscript/references.csv).

| Figure | Asset | Source | Copyright and license | Changes |
|---|---|---|---|---|
| 16 | `figures/krupinska2020_fig3.jpg` | [DOI 10.3390/molecules25030641](https://pmc.ncbi.nlm.nih.gov/articles/PMC7037863/) | 2020 the author; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Reproduced without altering plotted content; dose is mg elemental Al/L. Error-bar definition not specified in source. |
| 19 | `figures/original_18.png` | [DOI 10.1038/s41467-023-44626-9](https://www.nature.com/articles/s41467-023-44626-9) | The Author(s) 2024; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Panels excerpted and stacked; plotted values unchanged. Source-specific conditions and error bars identified in caption. |
| 21 | `figures/original_20.png` | [DOI 10.3390/w11091894](https://www.mdpi.com/2073-4441/11/9/1894) | The Authors 2019; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Plotted content unchanged; source MS2 and UVT conditions identified in caption. |
| 26 | `figures/original_21.png` | [DOI 10.1371/journal.pone.0026132](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0026132) | 2011 Luoto et al.; Creative Commons Attribution License as stated in source; version not asserted | Plotted content unchanged; assigned product, self-reported use and standard errors identified in caption. |

## Original project figures

The survey graphs and equipment diagrams were supplied with the project manuscript. They are preserved in the publication assets; preservation does not independently verify ownership, instrument provenance or measurements. No broad third-party license is asserted for them. The Blender publication renders communicate conceptual designs.

## Template dependencies

The manuscript uses the IEEE Access LaTeX class for layout, with custom BINAVO LABS front matter. Obtain template files directly from the [official IEEE Access author page](https://ieeeaccess.ieee.org/authors/preparing-your-article/). The public repository omits the 44 standalone template/font dependencies listed in `manuscript/template_dependencies.json`; the optional build helper uses separately supplied, hash-checked dependencies. This avoids asserting redistribution rights for standalone commercial font binaries. The included finished PDF is preserved as supplied.

## Blender scene fonts

Public scene copies replace packed proprietary fonts with Blender's built-in Bfont. Scene sanitization and geometry checks are recorded under `models/`. Archived publication figures are retained unchanged; regenerated lettering may differ. No Microsoft font binaries are distributed as standalone files or packed scene resources.

## Tools

Python, matplotlib, Blender, LaTeX and the GitHub workflow actions are separately distributed tools. Their software is not vendored here. Using their names describes file formats and reproduction dependencies; it does not imply endorsement. See the respective tools' own license terms for installations.
