#!/usr/bin/env python3
"""Reproduce aggregate checks and illustrative equations with Python 3.11+.

Run from the repository root:
    python -m unittest discover -s tests -v
    python scripts/reproduce.py
    python scripts/reproduce.py --output-dir build/reproduced --no-plots --check

Core calculations and tests require only the standard library. Matplotlib is
optional. --check compares deterministic JSON/CSV against committed results/;
software_test_report.json and plots are excluded because software can differ.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from blueshield import __version__
from blueshield.engineering import EQUATIONS, calculate_scenarios, sensitivity_rows
from blueshield.plotting import create_plots
from blueshield.survey import audit_survey


def normalized(value):
    """Stable public precision, independent of insignificant float tail digits."""
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite output is not permitted")
        return float(f"{value:.12g}")
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def json_text(value) -> str:
    return json.dumps(normalized(value), indent=2, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + "\n"


def csv_text(rows: list[dict]) -> str:
    if not rows:
        raise ValueError("output CSV requires a defined schema")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: format(v, ".12g") if isinstance(v, float) else v
                         for k, v in row.items()})
    return stream.getvalue()


def input_digest(path: Path) -> str:
    """Hash UTF-8 text after universal-newline normalization for Git portability."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def compare_payloads(payloads: dict[str, str], reference_dir: Path) -> list[str]:
    """Compare bytes without changing the baseline, including missing files."""
    differences = []
    for name, content in payloads.items():
        reference = reference_dir / name
        if not reference.exists() or reference.read_bytes() != content.encode("utf-8"):
            differences.append(name)
    return differences


def unit_for(name: str) -> str:
    suffix_units = [("kWh_m3_pumped", "kWh/m^3 pumped"), ("s_inverse", "1/s"),
                    ("mW_cm2", "mW/cm^2"), ("mg_L", "mg/L commercial product"),
                    ("L_h", "L/h"), ("LMH", "L/(m^2*h)"), ("mL", "mL"),
                    ("m2", "m^2"), ("Pa", "Pa"), ("bar", "bar"), ("min", "min"),
                    ("W", "W"), ("L", "L"), ("h", "h"), ("s", "s"), ("g", "g"), ("m", "m")]
    for suffix, unit in suffix_units:
        if name.endswith("_" + suffix):
            return unit
    raise ValueError(f"output quantity lacks an explicit unit: {name}")


def engineering_csv(results: dict) -> list[dict]:
    rows = []

    def walk(group: str, obj, path: str = "main"):
        if isinstance(obj, list):
            for index, child in enumerate(obj, 1):
                walk(group, child, f"{path}.{index}")
        elif isinstance(obj, dict):
            for key, child in obj.items():
                if isinstance(child, (list, dict)):
                    walk(group, child, f"{path}.{key}")
                elif isinstance(child, (float, int)) and not isinstance(child, bool):
                    rows.append({"equation_group": group, "scenario": path,
                                 "quantity": key, "value": child, "unit": unit_for(key),
                                 "status": "illustrative_assumption" if key.startswith("assumed_") else "illustrative_calculation"})
    for equation in EQUATIONS:
        group = equation["id"]
        walk(group, results[group])
        if group in {"uvpath", "lrv"}:
            rows.append({"equation_group": group, "scenario": "function_only",
                         "quantity": "not_calculated", "value": "", "unit": "not_applicable",
                         "status": equation["status"]})
    return rows


def run_tests() -> dict:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=1).run(suite)
    return {"status": "passed" if result.wasSuccessful() and result.testsRun else "failed",
            "tests_run": result.testsRun,
            "failures": [{"test": str(test), "detail": detail} for test, detail in result.failures],
            "errors": [{"test": str(test), "detail": detail} for test, detail in result.errors],
            "skipped": [{"test": str(test), "reason": reason} for test, reason in result.skipped],
            "expected_failures": len(result.expectedFailures),
            "unexpected_successes": len(result.unexpectedSuccesses),
            "scope": "Software arithmetic, dimensions, invalid inputs and source-aggregate consistency only; no empirical validation."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: results/; with --check: build/reproduced/).")
    parser.add_argument("--no-plots", action="store_true", help="Do not attempt optional matplotlib plots.")
    parser.add_argument("--check", action="store_true",
                        help="Compare deterministic payloads with repository results/ before writing outputs.")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        parser.error("Python 3.11 or newer is required")
    output_dir = (args.output_dir or (ROOT / "build" / "reproduced" if args.check else ROOT / "results")).resolve()
    protected = [ROOT / name for name in ["data", "src", "tests", "scripts", "manuscript", "models", "docs", ".github"]]
    if output_dir == ROOT.resolve() or any(p.resolve() == output_dir or p.resolve() in output_dir.parents for p in protected):
        parser.error("output directory must not overwrite source, manuscript, model, documentation or input folders")
    if args.check and (output_dir == (ROOT / "results").resolve() or (ROOT / "results").resolve() in output_dir.parents):
        parser.error("--check must write outside committed results/; omit --output-dir to use build/reproduced/")
    data_dir = ROOT / "data"
    inputs = json.loads((data_dir / "engineering_inputs.json").read_text(encoding="utf-8"))
    engineering = calculate_scenarios(inputs)
    survey = audit_survey(data_dir)
    cycle_rows, membrane_rows = sensitivity_rows(inputs)
    manifest = {"algorithm": "SHA-256", "canonicalization": "UTF-8 text with line endings normalized to LF; not a raw byte-file checksum", "files": {
        path.name: input_digest(path)
        for path in sorted(data_dir.iterdir()) if path.suffix in {".json", ".csv"}}}
    payloads = {
        "engineering_results.json": json_text(engineering),
        "equation_catalog.json": json_text({"groups": EQUATIONS, "note": "Equations are implemented; only supplied illustrative scenarios are calculated."}),
        "survey_audit.json": json_text(survey),
        "input_manifest.json": json_text(manifest),
        "engineering_scenarios.csv": csv_text(engineering_csv(engineering)),
        "demographic_audit.csv": csv_text(survey["demographics"]["rows"]),
        "perception_audit.csv": csv_text(survey["perceptions"]),
        "interview_audit.csv": csv_text(survey["interviews"]["rows"]),
        "design_sensitivity.csv": csv_text(cycle_rows),
        "membrane_sensitivity.csv": csv_text(membrane_rows)}
    differences = compare_payloads(payloads, ROOT / "results") if args.check else []
    if differences:
        print("Baseline check failed; no outputs were written: " + ", ".join(differences), file=sys.stderr)
        return 1
    tests = run_tests()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in payloads.items():
        (output_dir / name).write_bytes(content.encode("utf-8"))
    if args.no_plots:
        plots = {"status": "skipped", "reason": "--no-plots requested.", "files": []}
    else:
        try:
            plots = create_plots(output_dir, inputs, engineering, survey, cycle_rows, membrane_rows)
        except Exception as exc:
            plots = {"status": "failed", "reason": f"{type(exc).__name__}: {exc}", "files": []}
    report = {"software": {"python": platform.python_version(),
                            "implementation": platform.python_implementation(),
                            "package_version": __version__, "core_dependencies": "Python standard library"},
              "tests": tests, "plots": plots,
              "baseline_check": {"requested": args.check,
                                 "status": ("failed" if differences else "passed") if args.check else "not_requested",
                                 "different_or_missing_files": differences,
                                 "excluded_from_comparison": ["software_test_report.json", "*.png"]},
              "determinism": "Core JSON/CSV use fixed 12-significant-digit precision, UTF-8 and LF line endings; no clocks or random sampling.",
              "scope": "Software tests verify implemented arithmetic, not the reported data, treatment performance or clinical safety."}
    (output_dir / "software_test_report.json").write_bytes(json_text(report).encode("utf-8"))
    print(json.dumps({"output_directory": str(output_dir), "deterministic_files": len(payloads),
                      "equation_groups": len(EQUATIONS), "tests_run": tests["tests_run"],
                      "test_status": tests["status"], "plot_status": plots["status"],
                      "baseline_check": report["baseline_check"]["status"]}, indent=2))
    if differences:
        print("Different or missing committed outputs: " + ", ".join(differences), file=sys.stderr)
    return 1 if tests["status"] != "passed" or differences or plots["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
