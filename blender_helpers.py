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
    armature = get_root_animator()
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{name}")
    pbone = armature.data.edit_bones.get(f"Joint_{parent_name}")
    rbone = armature.data.edit_bones.get(f"Joint_{DYNOBJ_MARIO_MAIN_NET}")
    if pbone:
        bone.parent = pbone
    else:
        bone.parent = rbone
    objectmode()

def new_object(name: str):
    mesh = bpy.data.meshes.new(f"Shape_{name}_mesh")
    obj = bpy.data.objects.new(f"Shape_{name}", mesh)
    scene = bpy.context.scene
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj, mesh

def set_object_position(obj, pos: list[float]):
    obj.location[0] = pos[0]
    obj.location[1] = pos[1]
    obj.location[2] = pos[2]

def set_object_parent(obj, parent_name: str):
    obj.parent = bpy.data.objects[parent_name]

def make_object_vertex_group(obj, name: str):
    return obj.vertex_groups.new(name=name)

def weight_mesh_to_joint(obj, mesh, joint_name: str):
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

def set_object_weights(obj, net_name: str, weight_info: dict[int, float]):
    # Add this weight to the vertex group
    group = obj.vertex_groups[net_name]
    for index in weight_info:
        group.add([index], weight_info[index], "REPLACE")

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

def delete_unused_bones():
    # Find all bones referenced by animation data on the armature.
    for armature_obj in [
        obj for obj in bpy.context.scene.objects
        if obj.type == 'ARMATURE'
    ]:
        armature = armature_obj.data

        animated_bones = set()

        # Check animation on the armature object and its armature data.
        for owner in (armature_obj, armature):
            anim_data = owner.animation_data
            if not anim_data:
                continue

            actions = []
            if anim_data.action:
                actions.append(anim_data.action)

            # Blender 4.x/5.x layered action support.
            for track in anim_data.nla_tracks:
                for strip in track.strips:
                    if strip.action:
                        actions.append(strip.action)

            for action in actions:
                for fc in action.fcurves:
                    path = fc.data_path
                    if path.startswith('pose.bones["'):
                        bone_name = path.split('"')[1]
                        animated_bones.add(bone_name)

        # Find bones with nonzero vertex weights.
        weighted_bones = set()

        for obj in bpy.context.scene.objects:
            if obj.type != 'MESH':
                continue

            # Only consider meshes using this armature.
            if not any(
                mod.type == 'ARMATURE' and mod.object == armature_obj
                for mod in obj.modifiers
            ):
                continue

            for group in obj.vertex_groups:
                for vertex in obj.data.vertices:
                    for assignment in vertex.groups:
                        if (
                            assignment.group == group.index
                            and assignment.weight > 0.0
                        ):
                            weighted_bones.add(group.name)
                            break

        # Delete bones meeting neither usage condition.
        unused_bones = [
            bone.name for bone in armature.bones
            if bone.name not in animated_bones
            and bone.name not in weighted_bones
        ]

        if not unused_bones:
            continue

        bpy.context.view_layer.objects.active = armature_obj
        armature_obj.select_set(True)

        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        for name in unused_bones:
            bone = armature.edit_bones.get(name)
            if bone:
                armature.edit_bones.remove(bone)
        bpy.ops.object.mode_set(mode='OBJECT')

        print(f"{armature_obj.name}: removed {len(unused_bones)} bones")
        print("  " + ", ".join(unused_bones))

