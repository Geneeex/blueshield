"""Compile the unchanged manuscript with separately obtained template dependencies."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--template-zip", type=Path, help="Official IEEE Access LaTeX template ZIP")
    source.add_argument("--template-dir", type=Path, help="Directory containing extracted template dependencies")
    parser.add_argument("--pdflatex", default="pdflatex", help="Executable name or path")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "build" / "manuscript")
    args = parser.parse_args()
    executable = shutil.which(args.pdflatex)
    if not executable:
        parser.error("pdflatex is unavailable. Install a TeX distribution or supply --pdflatex.")
    manifest = json.loads((ROOT / "manuscript/template_dependencies.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    dependencies = {}
    if args.template_zip:
        with zipfile.ZipFile(args.template_zip) as archive:
            for name, digest in expected.items():
                matches = [i for i in archive.infolist() if Path(i.filename).name == name and not i.is_dir()]
                valid = [archive.read(i) for i in matches if i.file_size < 10 * 1024 * 1024]
                valid = [data for data in valid if hashlib.sha256(data).hexdigest() == digest]
                if not valid:
                    parser.error(f"Missing or changed template dependency: {name}. See manuscript/README.md.")
                dependencies[name] = valid[0]
    else:
        for name, digest in expected.items():
            matches = list(args.template_dir.rglob(name))
            valid = [p for p in matches if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == digest]
            if not valid:
                parser.error(f"Missing or changed template dependency: {name}.")
            dependencies[name] = valid[0].read_bytes()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Stage vendor files outside the repository; never commit unpacked font binaries.
    with tempfile.TemporaryDirectory(prefix="blueshield-tex-") as temp:
        stage = Path(temp)
        shutil.copytree(ROOT / "manuscript/latex/figures", stage / "figures")
        shutil.copy2(ROOT / "manuscript/latex/BLUESHIELD_BINAVO.tex", stage)
        for name, data in dependencies.items():
            (stage / name).write_bytes(data)
        for index in range(1, 4):
            result = subprocess.run(
                [executable, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "BLUESHIELD_BINAVO.tex"],
                cwd=stage, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", check=False,
            )
            (output / f"compile-{index}.txt").write_text(result.stdout, encoding="utf-8")
            if result.returncode:
                print(f"Compilation failed on pass {index}; inspect {output / f'compile-{index}.txt'}", file=sys.stderr)
                return result.returncode
        log = (stage / "BLUESHIELD_BINAVO.log").read_text(encoding="utf-8", errors="replace")
        problems = [line for line in log.splitlines() if "Overfull" in line or ("undefined" in line.lower() and ("Citation" in line or "Reference" in line))]
        shutil.copy2(stage / "BLUESHIELD_BINAVO.pdf", output / "BLUESHIELD_FILTER.pdf")
        summary = {"passes": 3, "template_dependencies_verified": len(dependencies), "layout_or_reference_warnings": problems, "font_warnings": [line for line in log.splitlines() if "Font Warning" in line],
                   "note": "PDF byte hashes may change with compiler versions, timestamps and document IDs."}
        (output / "build_report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Built {output / 'BLUESHIELD_FILTER.pdf'}")
        if problems:
            print("Inspect build_report.json before accepting this build.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
