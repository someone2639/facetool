from .commands import DLCmd
from .node_types import *
from .main import readDL
from .Shape import Shape, constructShape, matGroups
from .Joint import Joint
from .Animation import parseAnimation
import bpy
import math
import mathutils

from .GMaterial import GMaterial

dataGrpMap = {}
shapeMap = {}
vtxGroups = {}
objMap = {}
jointMap = {}

def editmode(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bpy.context.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")

def objectmode():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode='OBJECT')

def addRootAnimator():
    global objMap
    bpy.ops.object.armature_add(enter_editmode=False, align='WORLD', 
        location=(0, 0, 0), scale=(1, 1, 1))
    armature = bpy.context.object
    objMap[1001] = armature
    editmode(armature)
    armature.name = 'Root_Animator_1001'
    bone0 = armature.data.edit_bones[-1]
    bone0.name = "Joint_1001"
    bone0.head = (0, 0, 0)
    bone0.tail = (0, 0, 10)
    objectmode()

def addBone(name):
    armature = bpy.data.objects.get('Root_Animator_1001')
    editmode(armature)
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = name
    new_bone.use_deform = True
    objectmode()

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
        position[0] + (100 * normRot[0]),
        position[1] + (100 * normRot[1]),
        position[2] + (100 * normRot[2])
    )
    bone.tail = headPos
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

    rootNet = 0

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
                        addBone(f"Joint_{curObjName}")
                        jointMap[curObjName] = Joint(curObjName)
                        if rootNet == 0:
                            rootNet = curObjName
                            parent_bone(curObjName, 1001)
                        # bpy.ops.object.empty_add()
                        # em = bpy.context.object
                        # em.name = f'Net_{curObjName}'
                        # objMap[curObjName] = em
                        # bpy.context.scene.collection.objects.link(em)
                    case DNode.D_SHAPE:
                        shapeMap[curObjName] = Shape(curObjName, 0,0,0)
                        mesh = bpy.data.meshes.new(f'Shape_{curObjName}_mesh')
                        obj = bpy.data.objects.new(f'Shape_{curObjName}', mesh)
                        scene = bpy.context.scene
                        scene.collection.objects.link(obj)
                        bpy.context.view_layer.objects.active = obj
                        objMap[curObjName] = obj
                    case DNode.D_ANIMATOR:
                        # addBone(f"Joint_{curObjName}")
                        # jointMap[curObjName] = Joint(curObjName)
                        pass
                        # bpy.ops.object.empty_add()
                        # em = bpy.context.object
                        # em.name = f'Animator_{curObjName}'
                        # objMap[curObjName] = em
                    case DNode.D_MATERIAL:
                        matGroups[curMatGroup].append((GMaterial()))
                        # bpy.context.scene.collection.objects.link(em)
            case DLCmd.LinkWithPtr:
                dataGrpMap[curObjName].append(cmd.arg1)
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
                xzy = [cmd.vec[0], cmd.vec[2], cmd.vec[1]]
                # if curObjType == DNode.D_JOINT:
                jointMap[curObjName].rotation = xzy
            case DLCmd.SetAttachOffset:
                jointMap[curObjName].position = cmd.vec
                position_bone(curObjName, cmd.vec, jointMap[curObjName].rotation)
            case DLCmd.AttachTo:
                if curObjType != DNode.D_ANIMATOR:
                    if subGroupName != 0:
                        print(f"Attaching {subGroupName} to {cmd.arg1} (subgroup)...")
                        parent_bone(subGroupName, cmd.arg1)
                    else:
                        print(f"Attaching {curObjName} to {cmd.arg1}...")
                        parent_bone(curObjName, cmd.arg1)
                # if curObjName in jointMap and curObjType == DNode.D_NET:
                #     objMap[curObjName].location = jointMap[curObjName].location
                #     objMap[curObjName].rotation_euler = [
                #         math.radians(d) for d in jointMap[curObjName].rotation
                #     ]
                # if curObjType == DNode.D_JOINT:
                #     if curBone:
                #         parent_bone(curBone, cmd.arg1)
                # else:
                #     if curObjType == DNode.D_ANIMATOR:
                #         pass
                #     if subGroupName != 0:
                #         objMap[subGroupName].parent = objMap[cmd.arg1]
                #     else:
                #         objMap[curObjName].parent = objMap[cmd.arg1]
            case DLCmd.LinkWith:
                boneID = cmd.arg1
                if boneID == 221:
                    boneID = 1001
                parseAnimation(boneID, animMap[curObjName])
            case DLCmd.MakeNetWithSubGroup:
                subGroupName = cmd.arg1
                addBone(f'Joint_{subGroupName}')
                # bpy.ops.object.empty_add()
                # em = bpy.context.object
                # em.name = f'Net_{subGroupName}'
                # objMap[subGroupName] = em
            case DLCmd.EndNetWithSubGroup:
                # TODO: commit weights
                subGroupName = 0
                curSkinShape = 0
            case DLCmd.MakeAttachedJoint:
                # TDO: make bone
                # TODO: make vertex group and add it to SkinShape
                curObjType = DNode.D_JOINT
                curObjName = cmd.arg1
                jointMap[curObjName] = Joint(cmd.arg1)
                # bpy.ops.object.empty_add()
                # em = bpy.context.object
                # em.name = f'JointEmpty_{curObjName}'
                addBone(f'Joint_{curObjName}')
                parent_bone(curObjName, subGroupName)
                # objMap[curObjName] = em
                # objMap[curObjName].parent = objMap[subGroupName];
            case DLCmd.SetShapePtr:
                if cmd.arg1 in shapeMap:
                    constructShape(cmd.arg1, shapeMap[cmd.arg1])
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1
                o = bpy.data.objects[f"Shape_{curSkinShape}"]

                # if len([m for m in o.modifiers if m.name == "Armature_Root"]) == 0:
                #     objMap[curSkinShape].vertex_groups.new(name = f"Joint_1001")
                #     mod = o.modifiers.new(f"Armature_Root", "ARMATURE")
                #     mod.object = bpy.data.objects['Root_Animator_1001']
                #     mod.vertex_group = f"Joint_{curObjName}"

                mod = o.modifiers.new(f"Armature_{curSkinShape}", "ARMATURE")
                mod.object = bpy.data.objects['Root_Animator_1001']
                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new( name = f"Joint_{curObjName}" )
                editmode(objMap[curSkinShape])
                mesh = bpy.data.meshes[f"Shape_{curSkinShape}_mesh"]
                for v in mesh.vertices:
                    for g in v.groups:
                        g.weight = 0.0
                mod.vertex_group = f"Joint_{curObjName}"


                objectmode()
                # .modifiers["Armature"].object
                #  and attach the shape to a joint
            case DLCmd.SetSkinWeight:
                # Add this weight to the vertex group
                group = vtxGroups[curSkinShape]
                group.add( [cmd.arg2], cmd.vec[0] / 100.0, 'ADD' )
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