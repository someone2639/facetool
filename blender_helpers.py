import bpy
from mathutils import Euler, Matrix, Vector
from .constants import DYNOBJ_MARIO_MAIN_NET, ROOT_ANIMATOR_NAME, DYNOBJ_MARIO_MAIN_SHAPES_GROUP
from .utils import (
    JOINT_ROTATION_MODE,
    vec_deg2rad,
    base_rotation_coord_space_correction,
    rotation_coord_space_correction,
    position_coord_space_correction,
    angle_wrap_deg,
)


def editmode(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bpy.context.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")


def posemode(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bpy.context.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")


def objectmode():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

def new_joint(name: str, orient: bool = False):
    armature = bpy.data.objects.get(ROOT_ANIMATOR_NAME)
    editmode(armature)
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = name
    new_bone.use_deform = True
    objectmode()
    if orient:
        posemode(armature)
        bpy.data.objects[ROOT_ANIMATOR_NAME].pose.bones[
            name
        ].rotation_mode = JOINT_ROTATION_MODE
        objectmode()
    return new_bone

def set_joint_position(boneName, position, rotation_deg):
    rotation_rad = vec_deg2rad(rotation_deg)
    # print("set_joint_position",boneName,position,rotation_deg)
    armature = bpy.data.objects.get(ROOT_ANIMATOR_NAME)
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{boneName}")
    bone.head = (0, 0, 0)
    bone.tail = (0, 0, 100)

    R = Matrix.LocRotScale(
        position,
        # None,
        Euler(rotation_rad, JOINT_ROTATION_MODE),
        None,
    )

    bone.transform(R)
    objectmode()

def parent_joint(name: str, parent_name: str):
    armature = bpy.data.objects.get(ROOT_ANIMATOR_NAME)
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{name}")
    pbone = armature.data.edit_bones.get(f"Joint_{parent_name}")
    if pbone:
        bone.parent = pbone
    objectmode()

def new_object(name: str):
    mesh = bpy.data.meshes.new(f"Shape_{name}_mesh")
    obj = bpy.data.objects.new(f"Shape_{name}", mesh)
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj

def set_object_position(obj, pos: list[float]):
    obj.location[0] = pos[0]
    obj.location[1] = pos[1]
    obj.location[2] = pos[2]

def set_object_parent(obj, parent_name: str):
    obj.parent = bpy.data.objects[parent_name]

def make_object_vertex_group(obj, name: str):
    return obj.vertex_groups.new(name=name)

def weight_mesh_to_joint(obj, mesh_name: str, joint_name: str):
    mesh = bpy.data.meshes[mesh_name]
    all_indices = [v.index for v in mesh.vertices]

    rootgroup = make_object_vertex_group(obj, joint_name)
    rootgroup.add(all_indices, 1.0, "REPLACE")

def clear_object_weights(obj):
    mesh = obj.data
    editmode(obj)
    for v in mesh.vertices:
        for g in v.groups:
            g.weight = 0.0
    objectmode()

def set_object_joint(obj, joint_name: str):
    mod = obj.modifiers.new("Armature_Root", "ARMATURE")
    mod.object = get_root_animator()
    mod.vertex_group = f"Joint_{joint_name}"

def make_root_animator():
    # global objMap
    # objMap[root_name] = armature
    bpy.ops.object.armature_add(
        enter_editmode=False, align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
    )
    armature = bpy.context.object
    scene = bpy.context.scene
    scene.collection.objects.link(armature)
    editmode(armature)
    armature.name = ROOT_ANIMATOR_NAME
    bone0 = armature.data.edit_bones[-1]
    bone0.name = f"Joint_{ROOT_ANIMATOR_NAME}"
    bone0.head = (0, 0, 0)
    bone0.tail = (0, 0, 10)
    objectmode()
    bpy.data.objects[ROOT_ANIMATOR_NAME].show_in_front = True

def get_root_animator():
    return bpy.data.objects[ROOT_ANIMATOR_NAME]

