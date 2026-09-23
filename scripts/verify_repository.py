"""Check release contents, manuscript links and file hashes; no external packages."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "validation/file_manifest.json"
IGNORED_DIRS = {".git", "build", "__pycache__", ".venv", "venv", ".pytest_cache"}
IGNORED_SUFFIXES = {".pyc", ".pyo", ".aux", ".log", ".out"}

def release_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        relative = path.relative_to(ROOT)
        if relative.parts[:2] == ("models", "generated") or any(part in IGNORED_DIRS for part in relative.parts) or path.suffix in IGNORED_SUFFIXES:
            continue
        yield path

def inventory():
    return {p.relative_to(ROOT).as_posix(): {"bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in release_files()}

def inspect_structure():
    errors = []
    for name in ("README.md", "CITATION.cff", "LICENSE.md", "THIRD_PARTY_NOTICES.md",
                 "manuscript/BLUESHIELD_FILTER.pdf", "manuscript/latex/BLUESHIELD_BINAVO.tex",
                 "scripts/reproduce.py", "docs/CALCULATIONS.md", "docs/TESTING.md",
                 ".github/workflows/reproduce.yml", "models/README.md"):
        if not (ROOT / name).is_file():
            errors.append(f"Missing required file: {name}")
    main = ROOT / "manuscript/latex/BLUESHIELD_BINAVO.tex"
    if main.is_file():
        tex = main.read_text(encoding="utf-8")
        for asset in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex):
            if not (main.parent / asset).is_file():
                errors.append(f"Missing manuscript figure: {asset}")
        cited = {key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", tex) for key in group.split(",")}
        defined = re.findall(r"\\bibitem\{([^}]+)\}", tex)
        if cited - set(defined):
            errors.append(f"Undefined bibliography keys: {sorted(cited-set(defined))}")
        if len(defined) != len(set(defined)):
            errors.append("Duplicate bibliography keys")
        if "Sabik Bin Sultan\\textsuperscript{1}" not in tex or "Shafi Bin Sultan\\textsuperscript{2}" not in tex:
            errors.append("Manuscript author-number setting changed")
    scenes = list((ROOT / "models/scenes").glob("*.blend"))
    if len(scenes) != 8:
        errors.append(f"Expected 8 conceptual Blender scenes; found {len(scenes)}")
    for path in release_files():
        relative = path.relative_to(ROOT).as_posix()
        if path.stat().st_size >= 25 * 1024 * 1024:
            errors.append(f"File exceeds this release's browser-upload size budget: {relative}")
        if path.suffix.lower() in {".pfb", ".ttf", ".otf", ".blend1", ".blend2"}:
            errors.append(f"Excluded binary dependency or backup found: {relative}")
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true", help="Record current bytes after deliberate revisions")
    args = parser.parse_args()
    errors = inspect_structure()
    actual = inventory()
    if args.write_manifest:
        if errors:
            print("Manifest not updated because structure checks failed.", file=sys.stderr)
        else:
            MANIFEST.parent.mkdir(exist_ok=True)
            MANIFEST.write_text(json.dumps({"algorithm": "sha256", "scope": "Release files excluding this manifest, caches and ignored build products", "files": actual}, indent=2) + "\n", encoding="utf-8")
    elif not MANIFEST.is_file():
        errors.append("Missing validation/file_manifest.json")
    else:
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
        for name in sorted(set(expected) | set(actual)):
            if expected.get(name) != actual.get(name):
                errors.append(f"Release bytes changed, missing or added: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    total = sum(item["bytes"] for item in actual.values())
    print(f"PASS: {len(actual)} release files verified; {total / 1024**2:.2f} MiB; manuscript links and 8 scenes present.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
