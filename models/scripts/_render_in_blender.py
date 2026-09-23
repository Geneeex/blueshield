"""Internal Blender entry point. Never saves changes to the input .blend files."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_signature(scene):
    return [(obj.name, obj.type, tuple(tuple(row) for row in obj.matrix_world),
             len(obj.data.vertices) if obj.type == "MESH" else 0)
            for obj in scene.objects if obj.type not in {"FONT", "CAMERA", "LIGHT"}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("scenes", nargs="*")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)
    records = json.loads((ROOT / "clean_model_manifest.json").read_text(encoding="utf-8"))
    audits, rendered = [], []
    for record in records:
        stem = record["stem"]
        if args.scenes and stem not in args.scenes:
            continue
        path = ROOT / "scenes" / (stem + "_clean.blend")
        before = sha256(path)
        bpy.ops.wm.open_mainfile(filepath=str(path))
        scene = bpy.context.scene
        if scene.camera is None:
            raise RuntimeError("No active camera in " + path.name)
        fonts = [{"name": font.name, "packed": font.packed_file is not None,
                  "external_reference": bool(font.filepath and font.filepath != "<builtin>" and not font.packed_file),
                  "resource_name": Path(font.filepath.replace("\\", "/")).name}
                 for font in bpy.data.fonts]
        images = [{"name": image.name, "packed": bool(image.packed_file),
                   "external_reference": bool(image.filepath and not image.packed_file)}
                  for image in bpy.data.images if image.source == "FILE"]
        audits.append({"scene": path.name, "sha256": before, "blender_version": bpy.app.version_string,
                       "camera": scene.camera.name, "objects": len(scene.objects),
                       "fonts": fonts, "images": images,
                       "linked_libraries": len(bpy.data.libraries)})
        if args.inspect:
            continue
        geometry_before = geometry_signature(scene)
        scene.render.film_transparent = True
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.resolution_x, scene.render.resolution_y = 2600, 1750
        scene.render.resolution_percentage = 100
        scene.render.filepath = str(args.output / (stem + "_clean.png"))
        anchors = []
        for anchor in record["anchors"]:
            point = world_to_camera_view(scene, scene.camera, Vector(anchor["xyz"]))
            anchors.append({**anchor, "u": point.x, "v": point.y})
        started = time.time()
        bpy.ops.render.render(write_still=True)
        if geometry_before != geometry_signature(scene) or before != sha256(path):
            raise RuntimeError("Unexpected source or geometry change: " + stem)
        rendered.append({**record, "anchors": anchors, "geometry_unchanged": True,
                         "rendered_scene_sha256": before,
                         "render_seconds": round(time.time() - started, 2)})
        print("Rendered", stem, flush=True)
    (args.output / "scene_resource_audit.json").write_text(json.dumps(audits, indent=2), encoding="utf-8")
    if rendered:
        (args.output / "clean_model_manifest.json").write_text(json.dumps(rendered, indent=2), encoding="utf-8")
    print("Inspected" if args.inspect else "Rendered", len(audits), "scene(s).", flush=True)


if __name__ == "__main__":
    main()
