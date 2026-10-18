import bpy
from mathutils import Euler, Matrix, Vector

from .Animation import parseAnimation
from .commands import DLCmd
from .constants import DYNOBJ_MARIO_MAIN_NET, ROOT_ANIMATOR_NAME, DYNOBJ_MARIO_MAIN_SHAPES_GROUP
from .Face import Face
from .GMaterial import GMaterial
from .Joint import Joint
from .Net import Net
from .node_types import *
from .Shape import Shape, constructShape
from .utils import (
    JOINT_ROTATION_MODE,
    vec_deg2rad,
    base_rotation_coord_space_correction,
    rotation_coord_space_correction,
    position_coord_space_correction,
    angle_wrap_deg,
)
from .Scene import Scene

current_object_pos = [0, 0, 0]
stashed_object_pos = [0, 0, 0]

def stash_obj_pos():
    global stashed_object_pos
    global current_object_pos
    stashed_object_pos = current_object_pos

def unstash_obj_pos():
    global stashed_object_pos
    global current_object_pos
    current_object_pos = stashed_object_pos

def set_current_obj_pos(pos):
    global current_object_pos
    current_object_pos = pos

def get_world_pos() -> list[float]:
    global current_object_pos
    return current_object_pos

def add_vecs(a, b) -> list:
    return [x + y for x, y in zip(a, b)]

def subtract_vecs(a, b) -> list:
    return [x - y for x, y in zip(a, b)]

def parseDL(face: Face, name: str, root: bool = False):
    curObjType = 0
    curObjName = "0"
    subGroupName = 0
    curSkinShape = 0

    curBone = None

    curEmpty = None

    scene = Scene()

    rootNet = 0
    iAM_MODIFYING_THE_SUBGROUP = False

    cmdList = face.dynlists[name]

    scene = Scene()

    for cmd in cmdList:
        match cmd.type:
            case DLCmd.CallList:
                newscene = parseDL(face, cmd.arg1)
                scene.update(newscene)
            case DLCmd.MakeDynObj:
                curObjType = cmd.arg2
                curObjName = cmd.arg1
                match curObjType:
                    case "D_DATA_GRP":
                        scene.dataGroups[curObjName] = []
                    case "D_NET":
                        scene.joints[curObjName] = Joint(curObjName)
                        scene.joints[curObjName].name = curObjName
                        scene.nets[curObjName] = Net(curObjName)

                        # Parent the animated bones to the root bone
                        if rootNet == 0:
                            rootNet = curObjName
                            scene.joints[curObjName].parent = 0
                    case "D_SHAPE":
                        scene.shapes[curObjName] = Shape(curObjName, 0, 0, 0)
                    case "D_ANIMATOR":
                        pass
                    case "D_MATERIAL":
                        scene.materials[curMatGroup].append(GMaterial())
            case DLCmd.LinkWithPtr:
                scene.dataGroups[curObjName].append(cmd.arg1)
            case DLCmd.SetType:
                # Type 2 is a root net?
                # type 3 is a sub net?
                # TODO: make an enum in branch
                scene.nets[curObjName].type = int(cmd.arg2)
            case DLCmd.SetNodeGroup:
                if curObjType == "D_SHAPE":
                    scene.shapes[curObjName].verts = scene.dataGroups[cmd.arg1][0].replace(
                        "&", ""
                    )
                elif curObjType == "D_ANIMATOR":
                    scene.animations[curObjName] = scene.dataGroups[cmd.arg1][0].replace("&", "")
            case DLCmd.SetPlaneGroup:
                if curObjType == "D_SHAPE":
                    scene.shapes[curObjName].faces = scene.dataGroups[cmd.arg1][0].replace(
                        "&", ""
                    )
            case DLCmd.SetMaterialGroup:
                if curObjType == "D_SHAPE":
                    scene.shapes[curObjName].materials = cmd.arg1.replace("&", "")
            case DLCmd.EndList:
                pass
            case DLCmd.SetScale:
                # dont have to impl on the importer since always [1,1,1]
                pass
            case DLCmd.SetRotation:
                cur_rotation = rotation_coord_space_correction(cmd.vec)
                parent_rotation = [0, 0, 0]

                if curObjName in scene.nets:
                    scene.nets[curObjName].rotation = cur_rotation
                else:
                    if scene.joints[curObjName].parent != 0:
                        if scene.joints[curObjName].parent in scene.nets:
                            parent_rotation = scene.nets[scene.joints[curObjName].parent].rotation
                        else:
                            parent_rotation = scene.joints[scene.joints[curObjName].parent].rotation

                    # scene.joints[curObjName].rotation = add_vecs(cur_rotation, parent_rotation)
                    scene.joints[curObjName].rotation = cur_rotation

            case DLCmd.SetAttachOffset:
                posvec = position_coord_space_correction(cmd.vec)
                if curObjType == "D_NET":
                    if iAM_MODIFYING_THE_SUBGROUP:
                        scene.nets[subGroupName].position = posvec
                    else:
                        scene.nets[curObjName].position = posvec
                elif curObjType == "D_JOINT":
                    if scene.joints[curObjName].parent in scene.joints:
                        parentpos = scene.joints[scene.joints[curObjName].parent].position
                        parentpos = [a + b for a, b in zip(parentpos, posvec)]
                        scene.joints[curObjName].position = parentpos
                    else:
                        scene.joints[curObjName].position = posvec
                    if iAM_MODIFYING_THE_SUBGROUP:
                        scene.nets[subGroupName].position = posvec
                    else:
                        if cmd.vec == [0, 0, 0] and subGroupName != 0:
                            if subGroupName in scene.joints:
                                scene.joints[curObjName].position = scene.joints[subGroupName].position
                            elif subGroupName in scene.nets:
                                scene.joints[curObjName].position = scene.nets[subGroupName].position
                        else:
                            scene.joints[curObjName].position = posvec
            case DLCmd.AttachTo:
                flag = int(cmd.arg2, 16)
                attachTarget = cmd.arg1

                if curObjType != "D_ANIMATOR":
                    attachToKey = subGroupName if subGroupName != 0 else curObjName
                    if curObjType == "D_NET":
                        scene.nets[attachToKey].parent = attachTarget
                    elif curObjType == "D_JOINT":
                        scene.joints[attachToKey].parent = attachTarget
                # TODO: REDO D_JOINT anD D_NET
                if curObjName in scene.nets and not iAM_MODIFYING_THE_SUBGROUP:
                    if scene.nets[curObjName].type == 3:
                        print(f"{curObjName} attachto {flag:02X} {attachTarget}")
                        if flag & 0x9:
                            scene.nets[curObjName].joint = attachTarget
                            scene.nets[curObjName].default_vertex_weight = 1.0
                            scene.shapes[scene.nets[curObjName].shape].position = scene.joints[attachTarget].position
                            scene.nets[curObjName].rotation = scene.joints[attachTarget].rotation
            case DLCmd.LinkWith:
                boneID = cmd.arg1
                # if boneID == DYNOBJ_MARIO_MAIN_NET:
                #     boneID = ROOT_ANIMATOR_NAME
                if boneID in scene.joints:
                    scene.joints[boneID].animation = scene.animations[curObjName]
            case DLCmd.MakeNetWithSubGroup:
                subGroupName = cmd.arg1
                curObjType = "D_NET"
                iAM_MODIFYING_THE_SUBGROUP = True

                scene.nets[subGroupName] = Net(subGroupName)
            case DLCmd.EndNetWithSubGroup:
                subGroupName = 0
                curSkinShape = 0
                iAM_MODIFYING_THE_SUBGROUP = False
            case DLCmd.MakeAttachedJoint:
                if curObjType == "D_NET":
                    if iAM_MODIFYING_THE_SUBGROUP:
                        if subGroupName in scene.nets:
                            scene.nets[subGroupName].joint = cmd.arg1
                    else:
                        if curObjName in scene.nets:
                            scene.nets[curObjName].joint = cmd.arg1

                if iAM_MODIFYING_THE_SUBGROUP:
                    # edit commands will now apply to the joints themselves
                    iAM_MODIFYING_THE_SUBGROUP = False

                parentName = subGroupName
                if curObjType == "D_JOINT":
                    parentName = curObjName

                curObjType = "D_JOINT"
                curObjName = cmd.arg1
                scene.joints[curObjName] = Joint(curObjName)
                scene.joints[curObjName].name = curObjName
                scene.joints[curObjName].parent = parentName
            case DLCmd.SetShapePtr:
                if curObjType == "D_NET":
                    scene.nets[curObjName].shape = cmd.arg1
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1

                if iAM_MODIFYING_THE_SUBGROUP:
                    if subGroupName in scene.nets:
                        scene.nets[subGroupName].shape = curSkinShape
                else:
                    if curObjName in scene.nets:
                        scene.nets[curObjName].shape = curSkinShape
            case DLCmd.SetSkinWeight:
                scene.joints[curObjName].weights[int(cmd.arg2)] = cmd.vec[0] / 100.0
            case DLCmd.StartGroup:
                if cmd.arg1 != DYNOBJ_MARIO_MAIN_SHAPES_GROUP and cmd.arg1 != 1:
                    curMatGroup = cmd.arg1
                    scene.materials[curMatGroup] = []
            case DLCmd.SetId:
                if curObjType == "D_MATERIAL":
                    scene.materials[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.SetAmbient:
                if curObjType == "D_MATERIAL":
                    scene.materials[curMatGroup][-1].ambient = cmd.vec + [1.0]
            case DLCmd.SetDiffuse:
                if curObjType == "D_MATERIAL":
                    scene.materials[curMatGroup][-1].diffuse = cmd.vec + [1.0]
            # case DLCmd.SetTexturePath:
            #     scene.materials[curMatGroup][-1].matId = cmd.arg1
            case DLCmd.EndGroup:
                curMatGroup = 0
            case _:
                pass

    scene.end_frame = 820
    return scene
    # if DYNOBJ_MARIO_MAIN_NET in scene.objects:
    #     scene.objects[DYNOBJ_MARIO_MAIN_NET].rotation_euler = (math.radians(90), 0, 0)
