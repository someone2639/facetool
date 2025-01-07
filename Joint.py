import bpy
import math
import mathutils

from .utils import editmode, objectmode

class Joint():
    def __init__(self, name):
        self.name = name
        self.shape = 0
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.parent = 0 # 0 means root
        self.weights = {}
        self.bone = None
        self.vtxGroup = None

def addBone(j):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = j.name
    new_bone.use_deform = True
    new_bone.head = (0, 0, 0)
    new_bone.tail = (0, 0, 1)

    objctmode()
    return new_bone

def position_bone(bone, position, rotation):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    scale = (bone.tail - bone.head)[2]
    bone.head = tuple(position)
    rotLen = math.sqrt(
        (rotation[0]**2) +
        (rotation[1]**2) +
        (rotation[2]**2)
    )
    normRot = []
    if (rotLen == 0):
        normRot = [0, 0, 1]
    else:
        normRot = [r / rotLen for r in rotation]
    headPos = (
        position[0] + (scale * normRot[0]),
        position[1] + (scale * normRot[1]),
        position[2] + (scale * normRot[2])
    )
    bone.tail = headPos
    objectmode()

def parent_bone(bone, to):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    pbone = armature.data.edit_bones.get(f"Joint_{to}")
    if pbone:
        bone.parent = pbone
    objectmode()


