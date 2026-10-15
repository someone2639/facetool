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
                parseDL(face, cmd.arg1)
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

                scene.joints[curObjName].rotation = cur_rotation
            case DLCmd.SetAttachOffset:
                if curObjType == "D_NET":
                    scene.nets[curObjName].position = position_coord_space_correction(cmd.vec)
                if scene.joints[curObjName].parent in scene.joints:
                    parentpos = [
                        j for j in scene.joints[scene.joints[curObjName].parent].position
                    ]
                    parentpos = [a + b for a, b in zip(parentpos, position_coord_space_correction(cmd.vec))]
                    scene.joints[curObjName].position = parentpos
                else:
                    scene.joints[curObjName].position = position_coord_space_correction(cmd.vec)
                if iAM_MODIFYING_THE_SUBGROUP:
                    scene.joints[subGroupName].position = position_coord_space_correction(cmd.vec)
                else:
                    if cmd.vec == [0, 0, 0] and subGroupName != 0:
                        scene.joints[curObjName].position = scene.joints[subGroupName].position
                    else:
                        scene.joints[curObjName].position = position_coord_space_correction(cmd.vec)
            case DLCmd.AttachTo:
                if curObjType != "D_ANIMATOR":
                    if subGroupName != 0:
                        print(f"{curObjType} Attaching subgroup {subGroupName} to {cmd.arg1}...")
                        # parent_joint(subGroupName, cmd.arg1)
                        scene.joints[subGroupName].parent = cmd.arg1
                    else:
                        print(f"Attaching {curObjName} to {cmd.arg1}...")
                        parent_joint(curObjName, cmd.arg1)
                        scene.joints[curObjName].parent = cmd.arg1
                # TODO: REDO D_JOINT anD D_NET
            case DLCmd.LinkWith:
                boneID = cmd.arg1
                if boneID == DYNOBJ_MARIO_MAIN_NET:
                    boneID = ROOT_ANIMATOR_NAME
                if boneID in scene.joints:
                    scene.joints[boneID].animation = scene.animations[curObjName]
            case DLCmd.MakeNetWithSubGroup:
                iAM_MODIFYING_THE_SUBGROUP = True
                subGroupName = cmd.arg1
                scene.joints[subGroupName] = Joint(subGroupName)
                # scene.joints[subGroupName].bone = new_joint(f"Joint_{subGroupName}", True)
                # curObjType = "D_JOINT"
            case DLCmd.EndNetWithSubGroup:
                subGroupName = 0
                curSkinShape = 0
            case DLCmd.MakeAttachedJoint:
                if iAM_MODIFYING_THE_SUBGROUP:
                    # Only 1 joint can be in a subgroup at a time?
                    iAM_MODIFYING_THE_SUBGROUP = False

                curObjType = "D_JOINT"
                curObjName = cmd.arg1
                scene.joints[curObjName] = Joint(curObjName)
                scene.joints[curObjName].name = curObjName
                # override the vtx group
                # scene.vtxGroups[curSkinShape] = scene.objects[curSkinShape].vertex_groups.new(
                #     name=f"Joint_{curObjName}"
                # )
                # clear_object_weights(scene.objects[curSkinShape])
                # scene.joints[curObjName].bone = new_joint(f"Joint_{curObjName}", False)
                # parent_joint(curObjName, subGroupName)
                scene.joints[curObjName].parent = subGroupName
            case DLCmd.SetShapePtr:
                # if cmd.arg1 in scene.shapes:
                    # constructShape(face, cmd.arg1, scene.shapes[cmd.arg1])
                    # o = bpy.data.objects[f"Shape_{cmd.arg1}"]
                    # mesh = bpy.data.meshes[f"Shape_{cmd.arg1}_mesh"]
                    # rootgroup = scene.objects[cmd.arg1].vertex_groups.new(
                    #     name=f"Joint_{ROOT_ANIMATOR_NAME}"
                    # )
                    # all_indices = [v.index for v in mesh.vertices]
                    # rootgroup.add(all_indices, 0.5, "REPLACE")
                    # mod = o.modifiers.new("Armature_Root", "ARMATURE")
                    # mod.object = bpy.data.objects[ROOT_ANIMATOR_NAME]
                    # mod.vertex_group = f"Joint_{ROOT_ANIMATOR_NAME}"
                if curObjType == "D_NET":
                    scene.nets[curObjName].shape = f"Shape_{cmd.arg1}"
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1
                # o = bpy.data.objects[f"Shape_{curSkinShape}"]

                # mod = o.modifiers.new(f"Armature_{curSkinShape}", "ARMATURE")
                # mod.object = get_root_animator()

                # scene.vtxGroups[curSkinShape] = scene.objects[curSkinShape].vertex_groups.new(
                #     name=f"Joint_{subGroupName}"
                # )
                # clear_object_weights(scene.objects[curSkinShape])
                # mod.vertex_group = f"Joint_{curObjName}"
                # objectmode()
            case DLCmd.SetSkinWeight:
                # Add this weight to the vertex group
                group = scene.vtxGroups[curSkinShape]
                group.add([int(cmd.arg2)], cmd.vec[0] / 100.0, "REPLACE")
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
    return 820
    # if DYNOBJ_MARIO_MAIN_NET in scene.objects:
    #     scene.objects[DYNOBJ_MARIO_MAIN_NET].rotation_euler = (math.radians(90), 0, 0)
