"""Output serialization, immutable baseline checks and portable provenance."""
import contextlib
import importlib.util
import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("blueshield_reproduce", ROOT / "scripts" / "reproduce.py")
reproduce = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reproduce)


class ReproductionTests(unittest.TestCase):
    def test_json_is_stable_sorted_and_lf_terminated(self):
        first = reproduce.json_text({"z": 40 / 7, "a": [1, 2]})
        second = reproduce.json_text({"a": [1, 2], "z": 40 / 7})
        self.assertEqual(first, second)
        self.assertTrue(first.endswith("\n"))
        self.assertNotIn("\r", first)

    def test_csv_has_consistent_precision_and_lf(self):
        text = reproduce.csv_text([{"quantity": "fixture", "value": 40 / 7}])
        self.assertEqual(text, "quantity,value\nfixture,5.71428571429\n")

    def test_digest_normalizes_git_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a.csv", Path(directory) / "b.csv"
            a.write_bytes(b"one,two\n1,2\n")
            b.write_bytes(b"one,two\r\n1,2\r\n")
            self.assertEqual(reproduce.input_digest(a), reproduce.input_digest(b))

    def test_baseline_differences_do_not_modify_files(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory)
            (baseline / "same.json").write_bytes(b"same\n")
            (baseline / "different.json").write_bytes(b"old\n")
            result = reproduce.compare_payloads({"same.json": "same\n", "different.json": "new\n", "missing.json": "x\n"}, baseline)
            self.assertEqual(result, ["different.json", "missing.json"])
            self.assertEqual((baseline / "different.json").read_bytes(), b"old\n")
            self.assertFalse((baseline / "missing.json").exists())

    def test_cli_detects_corrupted_baseline_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            shutil.copytree(ROOT / "data", fixture / "data")
            (fixture / "results").mkdir()
            reference = fixture / "results" / "engineering_results.json"
            reference.write_bytes(b"corrupted baseline fixture\n")
            destination = fixture / "generated"
            with patch.object(reproduce, "ROOT", fixture), contextlib.redirect_stderr(io.StringIO()):
                status = reproduce.main(["--check", "--no-plots", "--output-dir", str(destination)])
            self.assertEqual(status, 1)
            self.assertEqual(reference.read_bytes(), b"corrupted baseline fixture\n")
            self.assertFalse(destination.exists())

    def test_cli_rejects_check_output_in_committed_results(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
            reproduce.main(["--check", "--output-dir", str(ROOT / "results")])
        self.assertEqual(result.exception.code, 2)

    def test_cli_rejects_source_output_collisions(self):
        for name in ["data", "src", "tests", "scripts", "manuscript", "models", "docs", ".github"]:
            with self.subTest(folder=name), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                reproduce.main(["--output-dir", str(ROOT / name / "nested")])
            self.assertEqual(result.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
