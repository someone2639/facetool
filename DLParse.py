import bpy
from mathutils import Euler, Matrix

from .Animation import parseAnimation
from .commands import DLCmd
from .constants import DYNOBJ_MARIO_MAIN_NET, ROOT_ANIMATOR_NAME
from .Face import Face
from .GMaterial import GMaterial
from .Joint import Joint
from .Net import Net
from .node_types import *
from .Shape import Shape, constructShape, matGroups
from .utils import (
    JOINT_ROTATION_MODE,
    editmode,
    objectmode,
    posemode,
    vec_deg2rad,
)

dataGrpMap = {}
shapeMap = {}
vtxGroups = {}
objMap = {}
jointMap = {}


def addRootAnimator():
    global objMap
    bpy.ops.object.armature_add(
        enter_editmode=False, align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
    )
    armature = bpy.context.object
    objMap[ROOT_ANIMATOR_NAME] = armature
    scene = bpy.context.scene
    scene.collection.objects.link(armature)
    editmode(armature)
    armature.name = f"Root_Animator_{ROOT_ANIMATOR_NAME}"
    bone0 = armature.data.edit_bones[-1]
    bone0.name = f"Joint_{ROOT_ANIMATOR_NAME}"
    bone0.head = (0, 0, 0)
    bone0.tail = (0, 0, 10)
    objectmode()
    bpy.data.objects[f"Root_Animator_{ROOT_ANIMATOR_NAME}"].show_in_front = True


def addBone(name: str, orient: bool):
    armature = bpy.data.objects.get(f"Root_Animator_{ROOT_ANIMATOR_NAME}")
    editmode(armature)
    bpy.ops.armature.bone_primitive_add()
    new_bone = armature.data.edit_bones[-1]
    new_bone.name = name
    new_bone.use_deform = True
    objectmode()
    if orient:
        posemode(armature)
        bpy.data.objects[f"Root_Animator_{ROOT_ANIMATOR_NAME}"].pose.bones[
            name
        ].rotation_mode = JOINT_ROTATION_MODE
        objectmode()
    return new_bone


def parent_bone(name: str, parent_name: str):
    armature = bpy.data.objects.get(f"Root_Animator_{ROOT_ANIMATOR_NAME}")
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{name}")
    pbone = armature.data.edit_bones.get(f"Joint_{parent_name}")
    if pbone:
        bone.parent = pbone
    objectmode()


def position_bone(boneName, position, rotation_deg):
    # print("position_bone",boneName,position,rotation_deg)
    armature = bpy.data.objects.get(f"Root_Animator_{ROOT_ANIMATOR_NAME}")
    editmode(armature)
    bone = armature.data.edit_bones.get(f"Joint_{boneName}")
    bone.head = (0, 0, 0)
    bone.tail = (0, 0, 100)

    R = Matrix.LocRotScale(
        position,
        None,
        # Euler(vec_deg2rad(rotation_deg), JOINT_ROTATION_MODE),
        None,
    )

    bone.transform(R)
    objectmode()


def parseDL(face: Face, name: str) -> int:
    global objMap
    global shapeMap
    global dataGrpMap
    global matGroups
    global vtxGroups
    global jointMap
    curObjType = 0
    curObjName = "0"
    subGroupName = 0
    curSkinShape = 0

    curBone = None

    curEmpty = None

    jointMap = {}
    animMap = {}
    netMap = {}

    rootNet = 0
    iAM_MODIFYING_THE_SUBGROUP = False

    cmdList = face.dynlists[name]

    for cmd in cmdList:
        match cmd.type:
            case DLCmd.CallList:
                parseDL(face, cmd.arg1)
            case DLCmd.MakeDynObj:
                curObjType = cmd.arg2
                curObjName = cmd.arg1
                match curObjType:
                    case "D_DATA_GRP":
                        dataGrpMap[curObjName] = []
                    case "D_NET":
                        jointMap[curObjName] = Joint(curObjName)
                        jointMap[curObjName].name = curObjName
                        jointMap[curObjName].bone = addBone(
                            f"Joint_{curObjName}", False
                        )
                        netMap[curObjName] = Net(curObjName)

                        # Parent the animated bones to the root bone
                        if rootNet == 0:
                            rootNet = curObjName
                            parent_bone(curObjName, ROOT_ANIMATOR_NAME)
                            jointMap[curObjName].parent = 0
                    case "D_SHAPE":
                        shapeMap[curObjName] = Shape(curObjName, 0, 0, 0)
                        mesh = bpy.data.meshes.new(f"Shape_{curObjName}_mesh")
                        obj = bpy.data.objects.new(f"Shape_{curObjName}", mesh)
                        scene = bpy.context.scene
                        scene.collection.objects.link(obj)
                        bpy.context.view_layer.objects.active = obj
                        objMap[curObjName] = obj
                        obj.location[0] = 0
                        obj.location[1] = 0
                        obj.location[2] = 0
                        # obj.rotation_euler[0] = math.pi / 2
                        # obj.rotation_euler[2] = math.pi
                        obj.parent = bpy.data.objects[
                            f"Root_Animator_{ROOT_ANIMATOR_NAME}"
                        ]
                    case "D_ANIMATOR":
                        pass
                    case "D_MATERIAL":
                        matGroups[curMatGroup].append(GMaterial())
            case DLCmd.LinkWithPtr:
                dataGrpMap[curObjName].append(cmd.arg1)
            case DLCmd.SetType:
                # Type 2 is a root net?
                # type 3 is a sub net?
                netMap[curObjName].type = cmd.arg2
            case DLCmd.SetNodeGroup:
                if curObjType == "D_SHAPE":
                    shapeMap[curObjName].verts = dataGrpMap[cmd.arg1][0].replace(
                        "&", ""
                    )
                elif curObjType == "D_ANIMATOR":
                    animMap[curObjName] = dataGrpMap[cmd.arg1][0].replace("&", "")
            case DLCmd.SetPlaneGroup:
                if curObjType == "D_SHAPE":
                    shapeMap[curObjName].faces = dataGrpMap[cmd.arg1][0].replace(
                        "&", ""
                    )
            case DLCmd.SetMaterialGroup:
                if curObjType == "D_SHAPE":
                    shapeMap[curObjName].materials = cmd.arg1.replace("&", "")
            case DLCmd.EndList:
                pass
            case DLCmd.SetScale:
                # dont have to impl on the importer since always [1,1,1]
                pass
            case DLCmd.SetRotation:
                jointMap[curObjName].rotation = cmd.vec
            case DLCmd.SetAttachOffset:
                if jointMap[curObjName].parent in jointMap:
                    parentpos = [
                        j for j in jointMap[jointMap[curObjName].parent].position
                    ]
                    parentpos[0] += cmd.vec[0]
                    parentpos[1] += cmd.vec[1]
                    parentpos[2] += cmd.vec[2]
                    position_bone(curObjName, parentpos, [0, 0, 0])
                else:
                    position_bone(curObjName, cmd.vec, jointMap[curObjName].rotation)
                if iAM_MODIFYING_THE_SUBGROUP:
                    # subgrot = Matrix.LocRotScale(
                    #     jointMap[subGroupName].position,
                    #     Euler(vec_deg2rad(jointMap[subGroupName].rotation), JOINT_ROTATION_MODE),
                    #     None
                    # )

                    # finalmtx = Matrix.Translation(cmd.vec) @ subgrot
                    # jointMap[curObjName].position = finalmtx.to_translation()
                    # print(f"Using matrix math to set Joint_{curObjName} to {jointMap[curObjName].position}")
                    # print(f"btw the matrix was {finalmtx}")
                    jointMap[subGroupName].position = cmd.vec
                    # print(f"Set SubJoint_{subGroupName} to pos {cmd.vec}")
                    position_bone(
                        subGroupName,
                        jointMap[subGroupName].position,
                        jointMap[subGroupName].rotation,
                    )
                else:
                    if cmd.vec == [0, 0, 0] and subGroupName != 0:
                        jointMap[curObjName].position = jointMap[subGroupName].position
                    else:
                        jointMap[curObjName].position = cmd.vec
                    position_bone(
                        curObjName,
                        jointMap[curObjName].position,
                        jointMap[curObjName].rotation,
                    )
            case DLCmd.AttachTo:
                if curObjType != "D_ANIMATOR":
                    if subGroupName != 0:
                        print(f"Attaching subgroup {subGroupName} to {cmd.arg1}...")
                        parent_bone(subGroupName, cmd.arg1)
                        jointMap[subGroupName].parent = cmd.arg1
                    else:
                        print(f"Attaching {curObjName} to {cmd.arg1}...")
                        parent_bone(curObjName, cmd.arg1)
                        jointMap[curObjName].parent = cmd.arg1
                if curObjType == "D_NET":
                    if netMap[curObjName].type == 3:
                        obj = bpy.data.objects[netMap[curObjName].shape]

                        jointToCopy = jointMap[cmd.arg1]
                        print(f"Setting {curObjName} to {jointToCopy.position}")

                        obj.rotation_euler = Euler(
                            jointToCopy.rotation, JOINT_ROTATION_MODE
                        )
                        if jointToCopy.name != DYNOBJ_MARIO_MAIN_NET:
                            # Don't set a net to -20010
                            obj.location = jointToCopy.position
                        else:
                            obj.location = (0, 0, 0)
                        mesh = bpy.data.meshes[f"{netMap[curObjName].shape}_mesh"]
                        rootgroup = obj.vertex_groups.new(name=f"Joint_{cmd.arg1}")
                        all_indices = [v.index for v in mesh.vertices]
                        rootgroup.add(all_indices, 1.0, "REPLACE")
                        mod = obj.modifiers.new("Armature_Root", "ARMATURE")
                        mod.object = bpy.data.objects[
                            f"Root_Animator_{ROOT_ANIMATOR_NAME}"
                        ]
                        mod.vertex_group = f"Joint_{cmd.arg1}"
            case DLCmd.LinkWith:
                boneID = cmd.arg1
                if boneID == DYNOBJ_MARIO_MAIN_NET:
                    boneID = ROOT_ANIMATOR_NAME
                if boneID in jointMap:
                    parseAnimation(
                        face, jointMap[boneID].rotation, boneID, animMap[curObjName]
                    )
                else:
                    parseAnimation(face, [0, 0, 0], boneID, animMap[curObjName])
                objectmode()
            case DLCmd.MakeNetWithSubGroup:
                iAM_MODIFYING_THE_SUBGROUP = True
                subGroupName = cmd.arg1
                jointMap[subGroupName] = Joint(subGroupName)
                jointMap[subGroupName].bone = addBone(f"Joint_{subGroupName}", True)
            case DLCmd.EndNetWithSubGroup:
                subGroupName = 0
                curSkinShape = 0
            case DLCmd.MakeAttachedJoint:
                if (
                    iAM_MODIFYING_THE_SUBGROUP
                ):  # Only 1 joint can be in a subgroup at a time?
                    iAM_MODIFYING_THE_SUBGROUP = False

                curObjType = "D_JOINT"
                curObjName = cmd.arg1
                jointMap[curObjName] = Joint(curObjName)
                jointMap[curObjName].name = curObjName
                # override the vtx group
                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new(
                    name=f"Joint_{curObjName}"
                )
                mesh = bpy.data.meshes[f"Shape_{curSkinShape}_mesh"]
                editmode(objMap[curSkinShape])
                for v in mesh.vertices:
                    for g in v.groups:
                        g.weight = 0.0
                objectmode()
                jointMap[curObjName].bone = addBone(f"Joint_{curObjName}", False)
                parent_bone(curObjName, subGroupName)
                jointMap[curObjName].parent = subGroupName
            case DLCmd.SetShapePtr:
                if cmd.arg1 in shapeMap:
                    constructShape(face, cmd.arg1, shapeMap[cmd.arg1])
                    o = bpy.data.objects[f"Shape_{cmd.arg1}"]
                    mesh = bpy.data.meshes[f"Shape_{cmd.arg1}_mesh"]
                    rootgroup = objMap[cmd.arg1].vertex_groups.new(
                        name=f"Joint_{ROOT_ANIMATOR_NAME}"
                    )
                    all_indices = [v.index for v in mesh.vertices]
                    rootgroup.add(all_indices, 0.5, "REPLACE")
                    mod = o.modifiers.new("Armature_Root", "ARMATURE")
                    mod.object = bpy.data.objects[f"Root_Animator_{ROOT_ANIMATOR_NAME}"]
                    mod.vertex_group = f"Joint_{ROOT_ANIMATOR_NAME}"
                if curObjType == "D_NET":
                    netMap[curObjName].shape = f"Shape_{cmd.arg1}"
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1
                o = bpy.data.objects[f"Shape_{curSkinShape}"]

                mod = o.modifiers.new(f"Armature_{curSkinShape}", "ARMATURE")
                mod.object = bpy.data.objects[f"Root_Animator_{ROOT_ANIMATOR_NAME}"]

                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new(
                    name=f"Joint_{subGroupName}"
                )
                print("before editmode")
                editmode(objMap[curSkinShape])
                print("done editmode")
                mesh = bpy.data.meshes[f"Shape_{curSkinShape}_mesh"]
                for v in mesh.vertices:
                    for g in v.groups:
                        g.weight = 0.0
                print("done weighting")
                mod.vertex_group = f"Joint_{curObjName}"
                objectmode()
                print("done cmd")
            case DLCmd.SetSkinWeight:
                # Add this weight to the vertex group
                group = vtxGroups[curSkinShape]
                group.add([int(cmd.arg2)], cmd.vec[0] / 100.0, "REPLACE")
            case DLCmd.StartGroup:
                if cmd.arg1 != 1000 and cmd.arg1 != 1:
                    curMatGroup = cmd.arg1
                    matGroups[curMatGroup] = []
            case DLCmd.SetId:
                if curObjType == "D_MATERIAL":
                    matGroups[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.SetAmbient:
                if curObjType == "D_MATERIAL":
                    matGroups[curMatGroup][-1].ambient = cmd.vec + [1.0]
            case DLCmd.SetDiffuse:
                if curObjType == "D_MATERIAL":
                    matGroups[curMatGroup][-1].diffuse = cmd.vec + [1.0]
            # case DLCmd.SetTexturePath:
            #     matGroups[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.EndGroup:
                curMatGroup = 0
            case _:
                pass
    return 820
    # if DYNOBJ_MARIO_MAIN_NET in objMap:
    #     objMap[DYNOBJ_MARIO_MAIN_NET].rotation_euler = (math.radians(90), 0, 0)
