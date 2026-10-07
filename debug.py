import bpy
import math

def print_anim_info(bone_name: str):
    obj = bpy.context.active_object

    if obj is None or obj.type != 'ARMATURE':
        raise PluginError("Active object is not an armature")

    action = obj.animation_data.action

    bone = obj.pose.bones.get(bone_name)

    scene = bpy.context.scene
    old_frame = scene.frame_current

    start = int(action.frame_range[0])
    end = int(action.frame_range[1])

    for frame in range(start, end + 1):
        scene.frame_set(frame)

        r = bone.rotation_euler

        print(f"{frame}: {{{math.degrees(r.x):.6f}, {math.degrees(r.y):.6f}, {math.degrees(r.z):.6f}}}")

    scene.frame_set(old_frame)