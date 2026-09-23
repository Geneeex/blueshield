# Maintain the BLUESHIELD GitHub repository

The public project repository is [SABIKGIT/blueshield](https://github.com/SABIKGIT/blueshield). It contains the manuscript, aggregate summaries, reproducible calculations, conceptual Blender models, and future-testing templates.

## Get a working copy

Clone the existing repository once:

```console
git clone https://github.com/SABIKGIT/blueshield.git
cd blueshield
```

For an existing clone, start from a clean working tree and update before editing:

```console
git status
git switch main
git pull --ff-only origin main
```

GitHub Desktop can manage the same clone. Authentication is handled by your own Git/GitHub client.

## Check and publish a revision

After making changes, run the software checks from the repository root with Python 3.11 or later:

```console
python -m unittest discover -s tests -v
python scripts/reproduce.py --output-dir build/reproduced --no-plots --check
python scripts/verify_repository.py --write-manifest
python scripts/verify_repository.py
```

The reproduction check compares ten deterministic JSON/CSV outputs with the committed results. If a deliberate scientific or software revision changes those results, review the changes and regenerate the baseline explicitly with `python scripts/reproduce.py --no-plots` before rerunning the checks above. Do not refresh results merely to hide an unexpected mismatch. The integrity manifest records the reviewed release bytes; a new checksum does not certify scientific validity.

Inspect the changes, then commit and push to the existing repository:

```console
git status --short
git diff --stat
git diff
git add -A
git diff --cached --stat
git commit -m "Describe the BLUESHIELD revision"
git push origin main
```

This repository is public. Include only intended project changes; keep identifiable participant records and unapproved laboratory records out of tracked files. The ignored `data/private/` directory is not part of the published research companion.

## Verify the published revision

- Open the updated README, [model gallery](MODEL_GALLERY.md), PDF, and figure links.
- Check [GitHub Actions](https://github.com/SABIKGIT/blueshield/actions) for the pushed commit. The workflow runs unit tests, deterministic reproduction, and release verification on Windows and Ubuntu with Python 3.11, 3.12, and 3.13.
- Keep [CITATION.cff](../CITATION.cff) consistent with the actual repository and any future release metadata. Add an archive DOI only when an archiving service assigns one.
- Use a versioned GitHub release when preserving the exact revision accompanying a paper, and describe substantive changes in its notes.

## Files, sizes, and external dependencies

Commit the project contents, rather than using the delivery ZIP as the repository's sole file. GitHub browser uploads allow individual files up to 25 MiB, and regular Git pushes block individual files larger than 100 MiB. The prepared assets are below these limits, so this release does not require Git LFS. Future large animations or datasets may need release assets or Git LFS. See [GitHub's file-size guidance](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

The delivery omits old duplicate releases, local software runtimes, temporary build logs, packed proprietary model fonts, and standalone publisher font binaries. `build/` and regenerated model previews are ignored. Empty laboratory templates are included; no respondent records or laboratory measurements have been invented.

The manuscript's optional PDF rebuild requires the separately obtained official IEEE Access template. Keep the downloaded template ZIP outside the tracked repository and follow the [manuscript build guide](../manuscript/README.md#optional-pdf-rebuild); its dependency hashes protect against unnoticed template changes. Do not add standalone template fonts to this repository.

Core checks use only Python's standard library. Optional plots, PDF builds, and Blender workflows have separate requirements documented in their respective guides. Workflow actions follow the official [checkout](https://github.com/actions/checkout) and [setup-python](https://github.com/actions/setup-python) documentation.
