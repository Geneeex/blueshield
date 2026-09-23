"""Blender entry point: make redistributable copies without external font data.

Run using Blender --background --factory-startup --python-exit-code 1
--python models/scripts/sanitize_scenes.py -- --source PATH_TO_CLEAN_SCENES.
The source directory is read-only. Output defaults to models/scenes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    if isinstance(value, (bool, int, float, str)) or value is None:
        return value
    try:
        return [plain(item) for item in value]
    except TypeError:
        return getattr(value, "name", type(value).__name__)


def rna_values(item, exclude=()):
    values = {}
    for prop in item.bl_rna.properties:
        key = prop.identifier
        if key in set(exclude) | {"rna_type"} or prop.type == "COLLECTION":
            continue
        try:
            value = getattr(item, key)
            if prop.type == "POINTER":
                values[key] = getattr(value, "name", None)
            else:
                values[key] = plain(value)
        except (AttributeError, TypeError, RuntimeError):
            pass
    return values


def signature():
    """Hash actual geometry, transforms, text content, materials, cameras/lights.

    Font references, source resource paths, and ID save-state flags are excluded.
    Font substitution is the one intentional appearance change.
    """
    common = {"is_updated", "is_updated_data", "is_runtime_data", "users",
              "use_fake_user", "is_embedded_data", "session_uid", "is_editable",
              "original", "is_evaluated", "library", "override_library",
              "asset_data", "preview", "tag", "name_full"}
    data = {"objects": [], "meshes": [], "curves": [], "materials": [],
            "cameras": [], "lights": [], "worlds": []}
    for obj in sorted(bpy.data.objects, key=lambda x: x.name):
        data["objects"].append({"name": obj.name, "type": obj.type,
            "data": getattr(obj.data, "name", None), "parent": getattr(obj.parent, "name", None),
            "matrix": plain(obj.matrix_world), "hide_render": obj.hide_render,
            "hide_viewport": obj.hide_viewport, "visible_camera": obj.visible_camera,
            "materials": [getattr(s.material, "name", None) for s in obj.material_slots],
            "modifiers": [rna_values(m) for m in obj.modifiers]})
    for mesh in sorted(bpy.data.meshes, key=lambda x: x.name):
        data["meshes"].append({"name": mesh.name,
            "vertices": [list(v.co) for v in mesh.vertices],
            "edges": [list(e.vertices) for e in mesh.edges],
            "polygons": [(list(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
            "materials": [getattr(m, "name", None) for m in mesh.materials],
            "uv_layers": [[list(d.uv) for d in uv.data] for uv in mesh.uv_layers]})
    for curve in sorted(bpy.data.curves, key=lambda x: x.name):
        excluded = common | {"font", "font_bold", "font_italic", "font_bold_italic", "edit_format"}
        if isinstance(curve, bpy.types.TextCurve):
            excluded |= {"texspace_location", "texspace_size"}  # derived glyph bounds
        props = rna_values(curve, excluded)
        data["curves"].append({"properties": props,
            "splines": [{"type": s.type, "cyclic": s.use_cyclic_u,
                "points": [list(p.co) for p in s.points],
                "bezier": [(list(p.co), list(p.handle_left), list(p.handle_right)) for p in s.bezier_points]}
                for s in curve.splines]})
    def nodes(tree):
        if tree is None:
            return None
        return {"nodes": [{"properties": rna_values(n),
            "inputs": [(s.identifier, plain(s.default_value)) for s in n.inputs if hasattr(s, "default_value")]}
            for n in tree.nodes],
            "links": [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in tree.links]}
    for material in sorted(bpy.data.materials, key=lambda x: x.name):
        data["materials"].append({"properties": rna_values(material, common), "nodes": nodes(material.node_tree)})
    for category in ("cameras", "lights", "worlds"):
        for item in sorted(getattr(bpy.data, category), key=lambda x: x.name):
            data[category].append({"properties": rna_values(item, common), "nodes": nodes(getattr(item, "node_tree", None))})
    scene = bpy.context.scene
    data["scene"] = {"camera": scene.camera.name, "engine": scene.render.engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage],
        "world": getattr(scene.world, "name", None), "film_transparent": scene.render.film_transparent}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), data


def builtin_font():
    probe = bpy.data.curves.new("__builtin_font_probe", "FONT")
    font = probe.font
    bpy.data.curves.remove(probe)
    if font.filepath != "<builtin>":
        raise RuntimeError("Blender did not provide its built-in Bfont")
    return font


def audit():
    fonts = [{"name": f.name, "filepath": f.filepath, "packed": bool(f.packed_file)} for f in bpy.data.fonts]
    paths = list(bpy.utils.blend_paths(absolute=False, packed=True, local=True))
    return {"fonts": fonts, "resource_paths": paths, "objects": len(bpy.data.objects),
            "meshes": len(bpy.data.meshes), "materials": len(bpy.data.materials),
            "cameras": len(bpy.data.cameras), "lights": len(bpy.data.lights),
            "linked_libraries": len(bpy.data.libraries), "text_blocks": len(bpy.data.texts)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "scenes")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    source, destination = args.source.resolve(), args.destination.resolve()
    if source == destination:
        raise ValueError("Source and destination must differ")
    destination.mkdir(parents=True, exist_ok=True)
    records = json.loads((ROOT / "clean_model_manifest.json").read_text(encoding="utf-8"))
    results = []
    bpy.context.preferences.filepaths.save_version = 0
    for record in records:
        filename = record["stem"] + "_clean.blend"
        original, target = source / filename, destination / filename
        original_hash = sha256(original)
        bpy.ops.wm.open_mainfile(filepath=str(original))
        signature_before, before_detail = signature()
        before_audit = audit()
        font = builtin_font()
        substitutions = []
        for curve in bpy.data.curves:
            if not isinstance(curve, bpy.types.TextCurve):
                continue
            for slot in ("font", "font_bold", "font_italic", "font_bold_italic"):
                old = getattr(curve, slot)
                if old != font:
                    substitutions.append({"curve": curve.name, "slot": slot,
                                          "old_font": old.name if old else None, "new_font": font.name})
                    setattr(curve, slot, font)
        removed_fonts = []
        for old in list(bpy.data.fonts):
            if old != font:
                removed_fonts.append({"name": old.name, "packed": bool(old.packed_file),
                    "source_filename": Path(old.filepath.replace("\\", "/")).name})
                bpy.data.fonts.remove(old, do_unlink=True)
        if bpy.data.libraries:
            raise RuntimeError("Linked libraries require manual review")
        if bpy.data.texts:
            raise RuntimeError("Embedded script/text blocks require manual review")
        # These procedural scenes must be self-contained after font removal.
        remaining_paths = list(bpy.utils.blend_paths(absolute=False, packed=True, local=True))
        if remaining_paths:
            raise RuntimeError("Unexpected resources: " + repr(remaining_paths))
        for screen in bpy.data.screens:
            for area in screen.areas:
                for space in area.spaces:
                    if space.type == "FILE_BROWSER" and space.params:
                        # Overwrite the fixed-size saved buffer before shortening
                        # it, so stale bytes cannot retain a private directory.
                        space.params.directory = b"/" * 1023
                        space.params.directory = b"//"
                        space.params.filename = ""
        for scene in bpy.data.scenes:
            scene.render.filepath = "//../generated/renders/" + record["stem"] + "_clean.png"
        signature_changed, _ = signature()
        if signature_before != signature_changed:
            raise RuntimeError("Unintended geometry/material/camera change before save")
        bpy.ops.wm.save_as_mainfile(filepath=str(target), check_existing=False, compress=False)
        bpy.ops.wm.open_mainfile(filepath=str(target))
        signature_reopened, reopened_detail = signature()
        if signature_before != signature_reopened:
            (destination.parent / "signature_debug.json").write_text(json.dumps({"before": before_detail, "after": reopened_detail}, indent=2))
            raise RuntimeError("Native reopen changed protected scene data")
        after_audit = audit()
        if any(f["packed"] or f["filepath"] != "<builtin>" for f in after_audit["fonts"]):
            raise RuntimeError("Non-builtin font remains")
        if after_audit["resource_paths"]:
            raise RuntimeError("External/packed resource remains")
        if sha256(original) != original_hash:
            raise RuntimeError("Source scene was modified")
        results.append({"scene": filename, "source_clean_sha256": original_hash,
            "sanitized_sha256": sha256(target), "sanitized_bytes": target.stat().st_size,
            "protected_scene_signature_sha256": signature_before,
            "native_reopen_signature_matches": True, "source_unchanged": True,
            "removed_fonts": removed_fonts, "font_substitutions": substitutions,
            "render_output_path": bpy.context.scene.render.filepath,
            "resource_audit": after_audit,
            "original_counts": {k: v for k, v in before_audit.items() if k not in {"fonts", "resource_paths"}}})
        print("Sanitized and reopened:", filename, flush=True)
    report = {"blender_version": bpy.app.version_string,
        "intentional_changes": ["All FONT curve slots use Blender built-in Bfont.",
            "Removed all other font datablocks, including packed Segoe UI binaries.",
            "Render output paths are relative to the saved scene.",
            "Font substitution changes glyph outlines and derived text bounds; text body and placement are retained.",
            "Saved file-browser directory buffers are cleared and point to the scene-relative directory."],
        "signature_scope": "Mesh vertices/topology/UVs; non-font curves; text content and non-font properties; object transforms/visibility/modifiers; material node inputs and links; camera, light and world properties; active camera and render configuration.",
        "scenes": results}
    (destination.parent / "sanitization_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Completed", len(results), "scenes", flush=True)


if __name__ == "__main__":
    main()
