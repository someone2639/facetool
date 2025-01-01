import bpy
import math
import mathutils

class Joint():
    def __init__(self, name):
        self.name = name
        self.shape = 0
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.parent = 0 # 0 means root
        self.weights = {}

def addBone(j):
    armature = bpy.data.objects.get('Root_Animator_1001')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = j.name
    new_bone.use_deform = True

    bpy.ops.object.mode_set(mode='OBJECT')
    return new_bone

def position_bone(bone, position, rotation):
    armature = bpy.data.objects.get('Root_Animator_1001')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bone.tail = tuple(position)
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
        position[0] + (10 * normRot[0]),
        position[1] + (10 * normRot[1]),
        position[2] + (10 * normRot[2])
    )
    bone.head = headPos
    bpy.ops.object.mode_set(mode='OBJECT')

def parent_bone(bone, to):
    armature = bpy.data.objects.get('Root_Animator_1001')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects.get('Root_Animator_1001')
    pbone = armature.data.edit_bones.get(f"Joint_{to}")
    if pbone:
        bone.parent = pbone
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


