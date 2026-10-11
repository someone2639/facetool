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
from .Shape import Shape, constructShape, matGroups
from .utils import (
    JOINT_ROTATION_MODE,
    vec_deg2rad,
    base_rotation_coord_space_correction,
    rotation_coord_space_correction,
    position_coord_space_correction,
    angle_wrap_deg,
)

from .blender_helpers import (
    editmode,
    objectmode,
    posemode,

    new_joint,
    set_joint_position,
    parent_joint,

    get_root_animator,

    new_object,
    set_object_position,
    set_object_parent,
    set_object_joint,
    clear_object_weights,
    make_object_vertex_group,
    # position_object_at_joint,
    # get_current_object_position,
    weight_mesh_to_joint,
)

dataGrpMap = {}
shapeMap = {}
vtxGroups = {}
objMap = {}
jointMap = {}
animMap = {}
netMap = {}


def parseDL(face: Face, name: str) -> int:
    global objMap
    global shapeMap
    global dataGrpMap
    global matGroups
    global vtxGroups
    global jointMap
    global animMap
    global netMap
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
                        jointMap[curObjName].bone = new_joint(
                            f"Joint_{curObjName}", orient = False
                        )
                        netMap[curObjName] = Net(curObjName)

                        # Parent the animated bones to the root bone
                        if rootNet == 0:
                            rootNet = curObjName
                            parent_joint(curObjName, ROOT_ANIMATOR_NAME)
                            jointMap[curObjName].parent = 0
                    case "D_SHAPE":
                        shapeMap[curObjName] = Shape(curObjName, 0, 0, 0)
                        objMap[curObjName] = new_object(curObjName)
                        set_object_position(objMap[curObjName], [0, 0, 0])
                        set_object_parent(objMap[curObjName], ROOT_ANIMATOR_NAME)
                    case "D_ANIMATOR":
                        pass
                    case "D_MATERIAL":
                        matGroups[curMatGroup].append(GMaterial())
            case DLCmd.LinkWithPtr:
                dataGrpMap[curObjName].append(cmd.arg1)
            case DLCmd.SetType:
                # Type 2 is a root net?
                # type 3 is a sub net?
                # TODO: make an enum in branch
                netMap[curObjName].type = int(cmd.arg2)
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
                cur_rotation = rotation_coord_space_correction(cmd.vec)

                jointMap[curObjName].rotation = cur_rotation
            case DLCmd.SetAttachOffset:
                if curObjType == "D_NET":
                    obj = bpy.data.objects[netMap[curObjName].shape]
                    newvec = position_coord_space_correction(cmd.vec)
                    set_object_position(obj, newvec)
                if jointMap[curObjName].parent in jointMap:
                    parentpos = [
                        j for j in jointMap[jointMap[curObjName].parent].position
                    ]
                    parentpos = [a + b for a, b in zip(parentpos, position_coord_space_correction(cmd.vec))]
                    set_joint_position(curObjName, parentpos, [0, 0, 0])
                else:
                    set_joint_position(
                        curObjName,
                        position_coord_space_correction(cmd.vec),
                        jointMap[curObjName].rotation
                    )
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
                    jointMap[subGroupName].position = position_coord_space_correction(cmd.vec)
                    # print(f"Set SubJoint_{subGroupName} to pos {cmd.vec}")
                    set_joint_position(
                        subGroupName,
                        jointMap[subGroupName].position,
                        jointMap[subGroupName].rotation,
                    )
                else:
                    if cmd.vec == [0, 0, 0] and subGroupName != 0:
                        jointMap[curObjName].position = jointMap[subGroupName].position
                    else:
                        jointMap[curObjName].position = position_coord_space_correction(cmd.vec)
                    set_joint_position(
                        curObjName,
                        jointMap[curObjName].position,
                        jointMap[curObjName].rotation,
                    )
            case DLCmd.AttachTo:
                if curObjType != "D_ANIMATOR":
                    if subGroupName != 0:
                        print(f"Attaching subgroup {subGroupName} to {cmd.arg1}...")
                        parent_joint(subGroupName, cmd.arg1)
                        jointMap[subGroupName].parent = cmd.arg1
                    else:
                        print(f"Attaching {curObjName} to {cmd.arg1}...")
                        parent_joint(curObjName, cmd.arg1)
                        jointMap[curObjName].parent = cmd.arg1
                if curObjType == "D_NET":
                    current_obj_world_pos = bpy.data.objects[netMap[curObjName].shape].matrix_world.translation
                    flag: int = int(cmd.arg2, 16)
                    zerovec = [0, 0, 0]
                    if netMap[curObjName].type == 3:
                        obj = bpy.data.objects[netMap[curObjName].shape]
                        jointToCopy = jointMap[cmd.arg1]

                        # Logic for 'flag & 9' (Maintaining relative offset)
                        if (flag & 9):
                            # C code: currObjPos = currentWorldPos - targetWorldPos
                            # targetWorldPos is jointToCopy.position
                            offset = [
                                current_obj_world_pos[0] - jointToCopy.position[0],
                                current_obj_world_pos[1] - jointToCopy.position[1],
                                current_obj_world_pos[2] - jointToCopy.position[2]
                            ]
                           
                            # Apply the target position PLUS the offset
                            if jointToCopy.name != DYNOBJ_MARIO_MAIN_NET:
                                obj.location = [a + b for a, b in zip(jointToCopy.position, offset)]
                            else:
                                obj.location = offset
                        else:
                            # Original "Snap" behavior (flag & 9 is false)
                            if jointToCopy.name != DYNOBJ_MARIO_MAIN_NET:
                                obj.location = jointToCopy.position
                            else:
                                obj.location = [0, 0, 0]

                        print(f"Setting {netMap[curObjName].shape} to {jointToCopy.position}")

                        obj.rotation_euler = Euler(
                            jointToCopy.rotation, JOINT_ROTATION_MODE
                        )
                        set_object_joint(obj, cmd.arg1)
                        weight_mesh_to_joint(obj, f"{netMap[curObjName].shape}_mesh", f"Joint_{cmd.arg1}")
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
                jointMap[subGroupName].bone = new_joint(f"Joint_{subGroupName}", True)
            case DLCmd.EndNetWithSubGroup:
                subGroupName = 0
                curSkinShape = 0
            case DLCmd.MakeAttachedJoint:
                if iAM_MODIFYING_THE_SUBGROUP:
                    # Only 1 joint can be in a subgroup at a time?
                    iAM_MODIFYING_THE_SUBGROUP = False

                curObjType = "D_JOINT"
                curObjName = cmd.arg1
                jointMap[curObjName] = Joint(curObjName)
                jointMap[curObjName].name = curObjName
                # override the vtx group
                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new(
                    name=f"Joint_{curObjName}"
                )
                clear_object_weights(objMap[curSkinShape])
                jointMap[curObjName].bone = new_joint(f"Joint_{curObjName}", False)
                parent_joint(curObjName, subGroupName)
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
                    # mod = o.modifiers.new("Armature_Root", "ARMATURE")
                    # mod.object = bpy.data.objects[ROOT_ANIMATOR_NAME]
                    # mod.vertex_group = f"Joint_{ROOT_ANIMATOR_NAME}"
                if curObjType == "D_NET":
                    netMap[curObjName].shape = f"Shape_{cmd.arg1}"
            case DLCmd.SetSkinShape:
                curSkinShape = cmd.arg1
                o = bpy.data.objects[f"Shape_{curSkinShape}"]

                mod = o.modifiers.new(f"Armature_{curSkinShape}", "ARMATURE")
                mod.object = get_root_animator()

                vtxGroups[curSkinShape] = objMap[curSkinShape].vertex_groups.new(
                    name=f"Joint_{subGroupName}"
                )
                clear_object_weights(objMap[curSkinShape])
                mod.vertex_group = f"Joint_{curObjName}"
                objectmode()
            case DLCmd.SetSkinWeight:
                # Add this weight to the vertex group
                group = vtxGroups[curSkinShape]
                group.add([int(cmd.arg2)], cmd.vec[0] / 100.0, "REPLACE")
            case DLCmd.StartGroup:
                if cmd.arg1 != DYNOBJ_MARIO_MAIN_SHAPES_GROUP and cmd.arg1 != 1:
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
