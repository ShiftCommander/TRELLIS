#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

import bpy


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_glb(glb_path: Path):
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RuntimeError("No mesh found after GLB import.")
    return meshes


def join_meshes(meshes):
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def cleanup_and_uv(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def make_image(tex_dir: Path, name: str, size: int, non_color: bool = False):
    tex_dir.mkdir(parents=True, exist_ok=True)
    image = bpy.data.images.new(name, width=size, height=size, alpha=False)
    image.filepath_raw = str(tex_dir / f"{name}.png")
    image.file_format = "PNG"
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def assign_bake_target_nodes(obj, base_img, normal_img, rough_img):
    if not obj.data.materials:
        mat = bpy.data.materials.new("AvatarSourceMaterial")
        mat.use_nodes = True
        obj.data.materials.append(mat)

    for mat in obj.data.materials:
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        # Target nodes used by Blender bake op when active.
        for node_name, img in (
            ("BAKE_BASE", base_img),
            ("BAKE_NORMAL", normal_img),
            ("BAKE_ROUGHNESS", rough_img),
        ):
            node = nodes.get(node_name) or nodes.new(type="ShaderNodeTexImage")
            node.name = node_name
            node.label = node_name
            node.image = img


def bake_pass(obj, target_node_name: str, bake_type: str):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for mat in obj.data.materials:
        nodes = mat.node_tree.nodes
        for n in nodes:
            n.select = False
        target = nodes.get(target_node_name)
        if target is None:
            continue
        target.select = True
        nodes.active = target

    if bake_type == "DIFFUSE":
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
    bpy.ops.object.bake(type=bake_type)


def build_final_material(obj, base_img, normal_img, rough_img):
    mat = bpy.data.materials.new(name="AvatarBakedMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    out = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    tex_base = nodes.new(type="ShaderNodeTexImage")
    tex_normal = nodes.new(type="ShaderNodeTexImage")
    tex_rough = nodes.new(type="ShaderNodeTexImage")
    nmap = nodes.new(type="ShaderNodeNormalMap")
    tex_base.image = base_img
    tex_normal.image = normal_img
    tex_rough.image = rough_img
    tex_normal.colorspace_settings.name = "Non-Color"
    tex_rough.colorspace_settings.name = "Non-Color"
    links.new(tex_base.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])
    links.new(tex_normal.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def export_glb(out_glb: Path):
    bpy.ops.export_scene.gltf(
        filepath=str(out_glb),
        export_format="GLB",
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_yup=True,
    )


def main():
    argv = os.sys.argv[os.sys.argv.index("--") + 1 :] if "--" in os.sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-glb", required=True)
    parser.add_argument("--out-glb", required=True)
    parser.add_argument("--tex-dir", required=True)
    parser.add_argument("--texture-size", type=int, default=2048)
    args = parser.parse_args(argv)

    input_glb = Path(args.input_glb).resolve()
    out_glb = Path(args.out_glb).resolve()
    tex_dir = Path(args.tex_dir).resolve()

    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.bake.use_clear = True

    meshes = import_glb(input_glb)
    avatar = join_meshes(meshes)
    cleanup_and_uv(avatar)

    base = make_image(tex_dir, "baseColor", args.texture_size, non_color=False)
    normal = make_image(tex_dir, "normal", args.texture_size, non_color=True)
    rough = make_image(tex_dir, "roughness", args.texture_size, non_color=True)

    assign_bake_target_nodes(avatar, base, normal, rough)
    bake_pass(avatar, "BAKE_BASE", "DIFFUSE")
    bake_pass(avatar, "BAKE_NORMAL", "NORMAL")
    bake_pass(avatar, "BAKE_ROUGHNESS", "ROUGHNESS")
    base.save()
    normal.save()
    rough.save()

    build_final_material(avatar, base, normal, rough)
    export_glb(out_glb)


if __name__ == "__main__":
    main()
