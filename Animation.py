import bpy
import math
import mathutils
from .main import readStruct
from itertools import zip_longest
from mathutils import Euler, Matrix
from .utils import editmode, posemode, objectmode, coord_space_correction, JOINT_ROTATION_MODE

def rotposzip(*iterables):
    for result in (grp for grp in zip_longest(*iterables, fillvalue=None)):
        yield tuple(v for v in result)

class GDAnimType():
    EMPTY                 = 0  # Listed types are how the data are arranged in memory; maybe not be exact type
    MTX4x4                = 1  # f32[4][4]
    SCALE3F_ROT3F_POS3F   = 2  # f32[3][3]
    SCALE3S_POS3S_ROT3S   = 3  # s16[9]
    SCALE3F_ROT3F_POS3F_2 = 4  # f32[3][3]
    STUB                  = 5
    ROT3S                 = 6  # s16[3]
    POS3S                 = 7  # s16[3]
    ROT3S_POS3S           = 8  # s16[6]
    MTX4x4F_SCALE3F       = 9  # {f32 mtx[4][4]; f32 vec[3];}
    CAMERA_EYE3S_LOOKAT3S = 11 # s16[6]

class GDAnimation():
    pass

animLookup = {
    GDAnimType.ROT3S: ">hhh",
    GDAnimType.POS3S: ">hhh",
    GDAnimType.ROT3S_POS3S: ">hhhhhh",
}

def makeAction(action):
    action_name = f"FaceAction_{action}"
    action = bpy.data.actions.get(action_name)
    if not action:
        action = bpy.data.actions.new(name=action_name)

def set_local_rotation(obj, value):
    rot = Euler(value, 'XYZ')
    obj.rotation_euler = (obj.rotation_euler.to_matrix() @ rot.to_matrix()).to_euler(obj.rotation_mode)

def LinkAnimation(baserot, boneID, action, rotation, position):
    action_name = f"FaceAction_{action}"
    action = bpy.data.actions.get(action_name)
    armature = bpy.data.objects.get("Root_Animator_1001")

    base_rotation = baserot
    editmode(armature)
    # Link the action to the armature's animation data
    if not armature.animation_data:
        armature.animation_data_create()
    armature.animation_data.action = action
    objectmode()

    # Step 2: Get Pose Bone (Pose mode is required for animation)
    posemode(armature)
    # get bone from joint name, parse and add keyframes to animation
    bone = armature.pose.bones.get(f'Joint_{boneID}')
    if not bone:
        print(f"Bone Joint_{boneID} not found.")
        objectmode()
        return
    
    # Step 3: Apply Transformations (position or rotation)
    if len(rotation) > 0:
        posemode(armature)
        bpy.data.objects["Root_Animator_1001"].pose.bones[f'Joint_{boneID}'].rotation_mode = JOINT_ROTATION_MODE
        objectmode()
    for frame, (rot, pos) in enumerate(rotposzip(rotation, position)):
        if rot:
            cur_rotation = [angle / 10.0 for angle in coord_space_correction(rot)]

            # cur_rotation[2] *= -1

            if frame==0:
                print(f"{boneID}: Cur_rot {cur_rotation} Base {base_rotation}")

            cur_rotation[0] -= base_rotation[0]
            cur_rotation[1] -= base_rotation[1]
            cur_rotation[2] -= base_rotation[2]
            # if boneID != 1001:
            # # TODO: rotation/2 seems to be correct, except when mario spins
            # else:
            #     cur_rotation[0] /= 2.0
            #     cur_rotation[1] /= 2.0
            #     cur_rotation[2] /= 2.0

            cur_rotation_rad = Euler([math.radians(angle) for angle in cur_rotation], JOINT_ROTATION_MODE)

            bone.rotation_euler = cur_rotation_rad
            bone.keyframe_insert(data_path="rotation_euler", frame=frame, index=-1)

        if pos:
            bone.location = [p / 10.0 for p in pos]
            bone.keyframe_insert(data_path="location", frame=frame, index=-1)
        # else:
        #     bone.location = (0, 0, 0)
        #     bone.keyframe_insert(data_path="location", frame=frame, index=-1)
    objectmode()


# Anim data format:
#  s32 count (-1 if done, 0 if empty)
#  u32 dataType (use the lookup struct)
#  u32 address
def parseAnimation(baseRot, jointID, offset):
    animdata = []
    animdata.append(readStruct(">lLL", offset))
    offset += 12
    while (animdata[-1][0] != -1):
        animdata.append(readStruct(">lLL", offset))
        offset += 12
    for i, a in enumerate(animdata):
        (a_count, a_type, a_offset) = a
        if a_count == -1:
            break
        makeAction(i)
        animPos = []
        animRot = []
        for j in range(a_count):
            structLookup = animLookup[a_type]
            if a_type == GDAnimType.ROT3S:
                animRot.append(readStruct(structLookup, a_offset))
                a_offset += 6
            elif a_type == GDAnimType.POS3S:
                animPos.append(readStruct(structLookup, a_offset))
                a_offset += 6
            elif a_type == GDAnimType.ROT3S_POS3S:
                vals = readStruct(structLookup, a_offset)
                animRot.append(vals[0:3])
                animPos.append(vals[3:6])
                a_offset += 12
        LinkAnimation(coord_space_correction(baseRot), jointID, i, animRot, animPos)
