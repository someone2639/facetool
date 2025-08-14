from .commands import DLCmd
from .node_types import *
from .main import readDL
from .Shape import Shape, constructShape, matGroups
from .Joint import Joint
from .Animation import parseAnimation
from .Net import Net
import bpy
import math
from mathutils import Euler, Vector, Matrix

from .GMaterial import GMaterial
from .utils import editmode, posemode, objectmode, to_xzy, vec_deg2rad

dataGrpMap = {}
shapeMap = {}
vtxGroups = {}
objMap = {}
jointMap = {}

def addRootAnimator():
    global objMap
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', 
        location=(0, 0, 0), scale=(1, 1, 1))
    armature = bpy.context.object
    objMap[1001] = armature
    scene = bpy.context.scene
    scene.collection.objects.link(armature)
    editmode(armature)
    armature.name = 'Root_Animator_1001'
    bone0 = armature.data.edit_bones[-1]
    bone0.name = "Joint_1001"
    bone0.head = (0, 0, 0)
    bone0.tail = (0, 0, 10)
    objectmode()
    bpy.data.objects["Root_Animator_1001"].show_in_front = True

def addBone(name, orient):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = name
    new_bone.use_deform = True
    objectmode()
    if orient:
        posemode(armature)
        bpy.data.objects["Root_Animator_1001"].pose.bones[name].rotation_mode = "XYZ"
        objectmode()
    return new_bone

def parent_bone(name, to):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{name}")
    pbone = armature.data.edit_bones.get(f"Joint_{to}")
    if pbone:
        bone.parent = pbone
    objectmode()


def position_bone(boneName, position, rotation):
    # print("position_bone",boneName,position,rotation)
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{boneName}")
    bone.head = tuple(position)
    # rotLen = math.sqrt(
    #     (rotation[0]**2) +
    #     (rotation[1]**2) +
    #     (rotation[2]**2)
    # )
    # normRot = []
    # if (rotLen == 0):
    #     normRot = [0, 0, 1]
    # else:
    #     normRot = [r / rotLen for r in rotation]
    # headPos = (
    #     position[0] + (100 * normRot[0]),
    #     position[1] + (100 * normRot[1]),
    #     position[2] + (100 * normRot[2])
    # )
    bone.tail = tuple([position[0], position[1], position[2] + 100])
    objectmode()

def parseDL(cmdList):
    global objMap
    global shapeMap
    global dataGrpMap
    global matGroups
    global vtxGroups
    curObjType = 0
    curObjName = 0
    subGroupName = 0
    curSkinShape = 0

    curBone = None

    curEmpty = None

    jointMap = {}
    animMap = {}
    netMap = {}

    rootNet = 0
    iAM_MODIFYING_THE_SUBGROUP=False

    for cmd in cmdList:
        match cmd.type:
            case DLCmd.CallList:
                tmpList = readDL(cmd.arg1)
                parseDL(tmpList)
            case DLCmd.MakeDynObj:
                curObjType = cmd.arg2
                curObjName = cmd.arg1
                match curObjType:
                    case DNode.D_DATA_GRP:
                        dataGrpMap[curObjName] = []
                    case DNode.D_NET:
                        jointMap[curObjName] = Joint(curObjName)
                        jointMap[curObjName].bone = addBone(f"Joint_{curObjName}", False)
                        netMap[curObjName] = Net(curObjName)
                        if rootNet == 0:
                            rootNet = curObjName
                            parent_bone(curObjName, 1001)
                            jointMap[curObjName].parent = 0
                    case DNode.D_SHAPE:
                        shapeMap[curObjName] = Shape(curObjName, 0,0,0)
                        mesh = bpy.data.meshes.new(f'Shape_{curObjName}_mesh')
                        obj = bpy.data.objects.new(f'Shape_{curObjName}', mesh)
                        scene = bpy.context.scene
                        scene.collection.objects.link(obj)
                        bpy.context.view_layer.objects.active = obj
                        objMap[curObjName] = obj
                    case DNode.D_ANIMATOR:
                        pass
                    case DNode.D_MATERIAL:
                        matGroups[curMatGroup].append((GMaterial()))
            case DLCmd.LinkWithPtr:
                dataGrpMap[curObjName].append(cmd.arg1)
            case DLCmd.SetType:
                netMap[curObjName].type = cmd.arg2
            case DLCmd.SetNodeGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].verts = dataGrpMap[cmd.arg1][0]
                elif curObjType == DNode.D_ANIMATOR:
                    animMap[curObjName] = dataGrpMap[cmd.arg1][0]
            case DLCmd.SetPlaneGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].faces = dataGrpMap[cmd.arg1][0]
            case DLCmd.SetMaterialGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].materials = cmd.arg1
            case DLCmd.EndList:
                pass
            case DLCmd.SetScale:
                # dont have to impl on the importer since always [1,1,1]
                pass
            case DLCmd.SetRotation:
                if jointMap[curObjName].rotation == [0, 0, 0]:
                    jointMap[curObjName].rotation = to_xzy(cmd.vec)
            case DLCmd.SetAttachOffset:
                if subGroupName != 0:
                    if cmd.vec == [0, 0, 0]:
                        jointMap[curObjName].position = jointMap[subGroupName].position
                        position_bone(curObjName, jointMap[curObjName].position, [0, 0, 0])
                    else:
                        subgrot = Matrix.LocRotScale(
                            jointMap[subGroupName].position,
                            Euler(vec_deg2rad(jointMap[subGroupName].rotation), "XYZ"),
                            None
                        )

                        finalmtx = Matrix.Translation(cmd.vec) @ subgrot
                        jointMap[curObjName].position = finalmtx.to_translation()
                        print(f"Using matrix math to set Joint_{curObjName} to {jointMap[curObjName].position}")
                        print(f"btw the matrix was {finalmtx}")
                        position_bone(curObjName, jointMap[curObjName].position, [0, 0, 0])
                else:
                    jointMap[curObjName].position = cmd.vec
                    position_bone(curObjName, cmd.vec, jointMap[curObjName].rotation)
            case DLCmd.AttachTo:
                if curObjType != DNode.D_ANIMATOR:
                    if subGroupName != 0:
                        print(f"Attaching subgroup {subGroupName} to {cmd.arg1}...")
                        parent_bone(subGroupName, cmd.arg1)
                        jointMap[subGroupName].parent = cmd.arg1
                    else:
                        print(f"Attaching {curObjName} to {cmd.arg1}...")
                        parent_bone(curObjName, cmd.arg1)
                        jointMap[curObjName].parent = cmd.arg1
                if curObjType == DNode.D_NET:
                    if netMap[curObjName].type == 3:
                        obj = bpy.data.objects[netMap[curObjName].shape]
                        obj.location = jointMap[cmd.arg1].bone.head
                        mesh = bpy.data.meshes[f"{netMap[curObjName].shape}_mesh"]
                        rootgroup = obj.vertex_groups.new( name = f"Joint_{cmd.arg1}" )
                        all_indices = [v.index for v in mesh.vertices]
                        rootgroup.add(all_indices, 1.0, 'REPLACE')
                        mod = obj.modifiers.new("Armature_Root", "ARMATURE")
                        mod.object = bpy.data.objects['Root_Animator_1001']
                        mod.vertex_group = f"Joint_{cmd.arg1}"
                        # obj.rotation_euler = [math.radians(a) for a in 
                        #     jointMap[cmd.arg1].rotation
                        # ]
            case DLCmd.LinkWith:
                boneID = cmd.arg1
                if boneID == 221:
                    boneID = 1001
                parseAnimation(boneID, animMap[curObjName])
                objectmode()
            case DLCmd.MakeNetWithSubGroup:
                iAM_MODIFYING_THE_SUBGROUP = True
                subGroupName = cmd.arg1
                print(f"MakeNetWithSubGroup {cmd.arg1}")
                jointMap[subGroupName] = Joint(subGroupName)
                jointMap[subGroupName].bone = addBone(f'Joint_{subGroupName}', True)
            case DLCmd.EndNetWithSubGroup:
                subGroupName = 0
                curSkinShape = 0
            case DLCmd.MakeAttachedJoint:
                iAM_MODIFYING_THE_SUBGROUP = False
                curObjType = DNode.D_JOINT
                curObjName = cmd.arg1
                jointMap[curObjName] = Joint(cmd.arg1)
                # override the vtx group
                # print(f"MakeAttachedJoint vtxgroup Joint_{curObjName}")
                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new(
                    name = f"Joint_{curObjName}"
                )
                mesh = bpy.data.meshes[f"Shape_{curSkinShape}_mesh"]
                editmode(objMap[curSkinShape])
                for v in mesh.vertices:
                    for g in v.groups:
                        g.weight = 0.0
                objectmode()
                jointMap[curObjName].bone = addBone(f'Joint_{curObjName}', False)
                parent_bone(curObjName, subGroupName)
            case DLCmd.SetShapePtr:
                if cmd.arg1 in shapeMap:
                    constructShape(cmd.arg1, shapeMap[cmd.arg1])
                    o = bpy.data.objects[f"Shape_{cmd.arg1}"]
                    mesh = bpy.data.meshes[f"Shape_{cmd.arg1}_mesh"]
                    rootgroup = objMap[cmd.arg1].vertex_groups.new( name = f"Joint_1001" )
                    all_indices = [v.index for v in mesh.vertices]
                    rootgroup.add(all_indices, 0.5, 'REPLACE')
                    mod = o.modifiers.new("Armature_Root", "ARMATURE")
                    mod.object = bpy.data.objects['Root_Animator_1001']
                    mod.vertex_group = "Joint_1001"
                if curObjType == DNode.D_NET:
                    netMap[curObjName].shape = f"Shape_{cmd.arg1}"
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1
                o = bpy.data.objects[f"Shape_{curSkinShape}"]

                mod = o.modifiers.new(f"Armature_{curSkinShape}", "ARMATURE")
                mod.object = bpy.data.objects['Root_Animator_1001']

                # print(f"SetSkinShape    vtxgroup Joint_{curObjName}")
                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new( name = f"Joint_{subGroupName}" )
                editmode(objMap[curSkinShape])
                mesh = bpy.data.meshes[f"Shape_{curSkinShape}_mesh"]
                for v in mesh.vertices:
                    for g in v.groups:
                        g.weight = 0.0
                mod.vertex_group = f"Joint_{curObjName}"
                objectmode()
            case DLCmd.SetSkinWeight:
                # Add this weight to the vertex group
                group = vtxGroups[curSkinShape]
                group.add( [cmd.arg2], cmd.vec[0] / 100.0, 'REPLACE' )
            case DLCmd.StartGroup:
                if cmd.arg1 != 1000 and cmd.arg1 != 1:
                    curMatGroup = cmd.arg1
                    matGroups[curMatGroup] = []
            case DLCmd.SetId:
                if curObjType == DNode.D_MATERIAL:
                    matGroups[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.SetAmbient:
                if curObjType == DNode.D_MATERIAL:
                    matGroups[curMatGroup][-1].ambient = cmd.vec + [1.0]
            case DLCmd.SetDiffuse:
                if curObjType == DNode.D_MATERIAL:
                    matGroups[curMatGroup][-1].diffuse = cmd.vec + [1.0]
            # case DLCmd.SetTexturePath:
            #     matGroups[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.EndGroup:
                curMatGroup = 0
            case _:
                pass
    # if 221 in objMap:
    #     objMap[221].rotation_euler = (math.radians(90), 0, 0)