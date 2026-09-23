"""Render publication scene copies using a user-supplied Blender executable."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenes", nargs="*", help="Scene basenames; omit to process all eight.")
    parser.add_argument("--blender", help="Path to Blender 4.3 or later; otherwise search PATH.")
    parser.add_argument("--output", type=Path, default=ROOT / "generated" / "renders")
    parser.add_argument("--inspect", action="store_true", help="Audit scene dependencies without rendering.")
    parser.add_argument("--dry-run", action="store_true", help="Print the command without running Blender.")
    args = parser.parse_args()
    records = json.loads((ROOT / "clean_model_manifest.json").read_text(encoding="utf-8"))
    available = {record["stem"] for record in records}
    unknown = set(args.scenes) - available
    if unknown:
        parser.error("Unknown scene(s): " + ", ".join(sorted(unknown)))
    blender = args.blender or shutil.which("blender")
    if not blender:
        parser.error("Blender was not found; pass --blender with the executable path.")
    command = [str(blender), "--background", "--factory-startup", "--python-exit-code", "1",
               "--python", str(ROOT / "scripts" / "_render_in_blender.py"), "--",
               "--output", str(args.output.resolve())]
    if args.inspect:
        command.append("--inspect")
    command.extend(args.scenes)
    if args.dry_run:
        print(json.dumps(command, indent=2))
        return 0
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
