import bpy
import math

JOINT_ROTATION_MODE = 'XYZ'

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
        bpy.ops.object.mode_set(mode='OBJECT')

def coord_space_correction(xyz):
    return [xyz[0], xyz[2], -xyz[1]]

def vec_deg2rad(rot):
    return [math.radians(angle) for angle in rot]

def vec_rad2deg(rot):
    return [math.degrees(angle) for angle in rot]

# From Fast64
def getFrameInterval(action: bpy.types.Action):
    scene = bpy.context.scene
    def getIntersectionInterval():
        """
        intersect action range and scene range
        Note: this doesn't handle correctly the case where the two ranges don't intersect, not a big deal
        """

        frame_start = max(
            scene.frame_start,
            int(round(action.frame_range[0])),
        )

        frame_last = max(
            min(
                scene.frame_end,
                int(round(action.frame_range[1])),
            ),
            frame_start,
        )

        return frame_start, frame_last

    range_get_by_choice = {
        "action": lambda: (int(round(action.frame_range[0])), int(round(action.frame_range[1]))),
        "scene": lambda: (int(round(scene.frame_start)), int(round(scene.frame_end))),
        "intersect_action_and_scene": getIntersectionInterval,
    }

    return range_get_by_choice["action"]()

def findStartBones(armatureObj):
    noParentBones = sorted(
        [
            bone.name
            for bone in armatureObj.data.bones
            if bone.parent is None
        ]
    )

    if len(noParentBones) == 0:
        raise PluginError(
            "No non switch option start bone could be found "
            + "in "
            + armatureObj.name
            + ". Is this the root armature?"
        )
    else:
        return noParentBones

    if len(noParentBones) == 1:
        return noParentBones[0]
    elif len(noParentBones) == 0:
        raise PluginError(
            "No non switch option start bone could be found "
            + "in "
            + armatureObj.name
            + ". Is this the root armature?"
        )
    else:
        raise PluginError(
            "Too many parentless bones found. Make sure your bone hierarchy starts from a single bone, "
            + 'and that any bones not related to a hierarchy have their geolayout command set to "Ignore".'
        )

def get_weights(ob, vgroup):
    group_index = vgroup.index
    for i, v in enumerate(ob.data.vertices):
        for g in v.groups:
            if g.group == group_index:
                yield (i, g.weight)
                break
