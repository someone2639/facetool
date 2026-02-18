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
from .utils import (
    editmode,
    posemode,
    objectmode,
    getFrameInterval,
    vec_rad2deg,
    get_weights,
)


# TODO: binary exporter too (as a separate thing?)
# TODO: write all names into an enum before writing data
class Exporter:
    def __init__(self, file, is_binary=False):
        self.is_binary = is_binary
        self.armature = None
        self.namesToWrite = []
        self.enums = []
        self.actionCount = 0

        self.animGroups = []
        self.skinWeights = {}
        if is_binary:
            self.file = open(file, "wb+")
        else:
            self.file = open(file, "w+")

    def WriteHeader(self):
        self.file.write("""#include <PR/ultratypes.h>

#include "macros.h"
#include "dynlist_macros.h"
#include "dynlists.h"
#include "animdata.h"
#include "../dynlist_proc.h"
#include "../shape_helper.h"
#include "../gd_types.h"
""")

    def getShapeOutput(self, mesh, name):
        vtxScale = 100
        # export vertices
        vertBuffer = f"static s16 verts_{name}[][3] = {{"

        for i, vtx in enumerate(mesh.vertices):
            vertBuffer += f"{{ {int(vtxScale * vtx.co[0])}, {int(vtxScale * vtx.co[1])}, {int(vtxScale * vtx.co[2])} }}, "
        vertBuffer += f"}};\n"
        vertBuffer += f"static struct GdVtxData vtx_{name} = {{ ARRAY_COUNT(verts_{name}), 1, verts_{name}}};\n"

        # export triangles
        triBuffer = f"static u16 facedata_{name}[][4] = {{"

        for i, poly in enumerate(mesh.polygons):
            vtxIdx = poly.vertices
            # TODO: make sure theres no n-gons
            triBuffer += (
                f"{{ {poly.material_index}, {vtxIdx[0]}, {vtxIdx[1]}, {vtxIdx[2]} }}, "
            )

        triBuffer += f"}};\n"
        triBuffer += f"static struct GdFaceData faces_{name} = {{ ARRAY_COUNT(facedata_{name}), 1, facedata_{name}}};\n"

        # Start dynlist, link vtx and faces
        dynlistBuf = f"struct DynList dynlist_{name}_shape[] = {{\n"
        dynlistBuf += "    BeginList(),\n"
        dynlistBuf += (
            f"        MakeDynObj(D_DATA_GRP, DYNOBJ_{name.upper()}_VTX_GROUP),\n"
        )
        dynlistBuf += f"            LinkWithPtr(&vtx_{name}),\n"
        dynlistBuf += (
            f"        MakeDynObj(D_DATA_GRP, DYNOBJ_{name.upper()}_TRI_GROUP),\n"
        )
        dynlistBuf += f"            LinkWithPtr(&faces_{name}),\n"

        # Write the Material Group
        dynlistBuf += f"    StartGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        for i, mtl in enumerate(mesh.materials):
            color = mtl.node_tree.nodes["Principled BSDF"].inputs[0].default_value
            dynlistBuf += "        MakeDynObj(D_MATERIAL, 0),\n"
            dynlistBuf += f"            SetId({i}),\n"
            dynlistBuf += (
                f"            SetAmbient({color[0]}, {color[1]}, {color[2]}),\n"
            )
            # TODO: no diffuse color yet
            dynlistBuf += (
                f"            SetDiffuse({color[0]}, {color[1]}, {color[2]}),\n"
            )

        dynlistBuf += f"    EndGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        # Make the Shape definition
        self.enums.append(f"DYNOBJ_{name.upper()}_SHAPE")
        self.enums.append(f"DYNOBJ_{name.upper()}_VTX_GROUP")
        self.enums.append(f"DYNOBJ_{name.upper()}_TRI_GROUP")
        self.enums.append(f"DYNOBJ_{name.upper()}_MTL_GROUP")
        dynlistBuf += f"    MakeDynObj(D_SHAPE, DYNOBJ_{name.upper()}_SHAPE),\n"
        dynlistBuf += f"        SetNodeGroup(DYNOBJ_{name.upper()}_VTX_GROUP),\n"
        dynlistBuf += f"        SetPlaneGroup(DYNOBJ_{name.upper()}_TRI_GROUP),\n"
        dynlistBuf += f"        SetMaterialGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        # Finish
        dynlistBuf += "    EndList(),\n"
        dynlistBuf += "};\n"

        return (vertBuffer, triBuffer, dynlistBuf)

    def getAnimData(self, joint):
        # count actions (only once?)
        # if self.actionCount == 0:
        #     self.actionCount = len(bpy.data.actions)

        animType = "GD_ANIM_EMPTY"

        animBuffer = ""
        animArray = f"struct AnimDataInfo anim_{joint.name}[] = {{\n"

        # We need to do every action per joint
        for i, action in enumerate(bpy.data.actions):
            print(f"Exporting action {i} for joint {joint.name}...")
            # get frame range
            frame_start = int(action.frame_range[0])
            frame_end = int(action.frame_range[1])

            positions = []
            rotations = []

            # get animation values for position and rotation
            # TODO: we can do scale and full matrix
            # TODO: chooser for float/short anims
            currentFrame = bpy.context.scene.frame_current
            for frame in range(frame_start, frame_end):
                bpy.context.scene.frame_set(frame)
                curMtx = joint.matrix
                positions.append([int(p) * 10 for p in curMtx.to_translation()])
                rotations.append(
                    [
                        int(r) * 10
                        for r in coord_space_correction(vec_rad2deg(curMtx.to_euler()))
                    ]
                )

            # set frame back
            bpy.context.scene.frame_set(currentFrame)

            # Check if rot3s, pos3s, or both
            hasPositions = False
            hasRotations = False
            for p in positions:
                if p != (0, 0, 0):
                    hasPositions = True
                    break
            for r in rotations:
                if r != (0, 0, 0):
                    hasRotations = True
                    break

            # Start Writing
            if hasRotations and hasPositions:
                animType = "GD_ANIM_ROT3S_POS3S"
            elif hasPositions:
                animType = "GD_ANIM_POS3S"
            elif hasRotations:
                animType = "GD_ANIM_ROT3S"

            if animType == "GD_ANIM_EMPTY":
                pass
            else:
                animLength = 3
                if animType == "GD_ANIM_ROT3S_POS3S":
                    animLength = 6
                animBuffer += f"static s16 animdata_{joint.name}_action_{i}[][{animLength}] = {{\n"
                if animType == "GD_ANIM_ROT3S":
                    for rot in rotations:
                        animBuffer += f"{{ {rot[0]}, {rot[1]}, {rot[2]} }},"
                elif animType == "GD_ANIM_POS3S":
                    for pos in positions:
                        animBuffer += f"{{ {pos[0]}, {pos[1]}, {pos[2]} }},"
                elif animType == "GD_ANIM_ROT3S_POS3S":
                    for rot, pos in zip(rotations, positions):
                        animBuffer += f"{{ {rot[0]}, {rot[1]}, {rot[2]}, {pos[0]}, {pos[1]}, {pos[2]} }},"
                animBuffer += "\n};\n"

            if animType == "GD_ANIM_EMPTY":
                animArray += "    { 0, GD_ANIM_EMPTY, NULL },\n"
            else:
                arrlen = max(len(rotations), len(positions))
                animArray += f"    {{ {arrlen}, {animType}, animdata_{joint.name}_action_{i} }},\n"

        animArray += "    END_ANIMDATA_INFO_ARR,\n"
        animArray += "};\n"

        return animBuffer + animArray

    def getMainDListData(self, name):
        mainDListBuf = f"struct DynList dynlist_{name}[] = {{\n"
        mainDListBuf += "    BeginList(),\n"
        mainDListBuf += "    UseIntegerNames(1),\n"

        # TODO: unhardcode this in
        self.enums.append(f"DYNOBJ_{name.upper()}_SHAPES_GROUP = 1000")
        mainDListBuf += f"    StartGroup(DYNOBJ_{name.upper()}_SHAPES_GROUP),\n"
        for shape_name in self.namesToWrite:
            mainDListBuf += f"        CallList(dynlist_{shape_name}_shape),\n"
        mainDListBuf += f"    EndGroup(DYNOBJ_{name.upper()}_SHAPES_GROUP),\n"
        mainDListBuf += "    StartGroup(1),\n"

        self.enums.append(f"DYNOBJ_{name.upper()}_NET")
        mainDListBuf += f"        MakeDynObj(D_NET, DYNOBJ_{name.upper()}_NET),\n"
        mainDListBuf += "            SetType(2),\n"  # root
        # mainDListBuf +=  "            SetFlag(0x2),"

        # TODO: get the main shape name somehow
        self.enums.append("DYNOBJ_SHAPE_225_SHAPE")
        mainDListBuf += f"            SetShapePtr(DYNOBJ_SHAPE_225_SHAPE),\n"
        mainDListBuf += "            SetScale(1.0, 1.0, 1.0),\n"
        mainDListBuf += "            SetRotation(0.0, 0.0, 0.0),\n"
        mainDListBuf += "            SetAttachOffset(0.0, 0.0, 0.0),\n"

        # TODO: for EACH shape, make dynobj and then attachedjoints
        for obj in bpy.data.objects:
            if obj.parent == self.armature and obj.type == "MESH":
                loc = obj.location
                mainDListBuf += f"""
                MakeDynObj(D_NET, DYNOBJ_{obj.name.upper()}_NET),
                    SetType(3),
                    SetShapePtr(DYNOBJ_{obj.name.upper()}_SHAPE),
                    AttachTo(0xd, DYNOBJ_{name.upper()}_NET),
                    SetScale(1.0, 1.0, 1.0),
                    SetRotation(0.0, 0.0, 0.0),
                    SetAttachOffset({loc[0]}, {loc[1]}, {loc[2]}),
"""
                skins = [
                    name for skinName in self.skinWeights if obj.name.upper() in name
                ]
                for skin in skins:
                    mainDListBuf += self.skinWeights[skin]

        for animator in self.animGroups:
            mainDListBuf += animator

        mainDListBuf += "    EndGroup(0x1),\n"
        mainDListBuf += "    UseObj(0x1),\n"
        mainDListBuf += "    UseIntegerNames(FALSE),\n"
        mainDListBuf += "    EndList(),\n"
        mainDListBuf += "};\n"

        return mainDListBuf

    def WriteEnums(self):
        self.file.write("enum DynListCustomTypes {\n")
        for nm in set(self.enums):
            self.file.write(f"    {nm},\n")
        self.file.write("};\n")

    # return (shape to linkwith, skin_net name, skin data)
    def getSkinData(self, joint):
        myVertexGroup = None
        myShape = None
        for obj in bpy.data.objects:
            for vg in obj.vertex_groups:
                if vg.name == joint.name:
                    myVertexGroup = vg
                    myShape = obj

        if myVertexGroup is None:
            # Nothing to skin
            return ("", "", "")

        self.enums.append(
            f"DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}_SKIN_NET"
        )
        self.enums.append(f"DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}")
        self.enums.append(f"DYNOBJ_{myShape.name.upper()}_NET")

        rot = vec_rad2deg(joint.rotation_euler)
        pos = joint.location
        skinBuffer = f"    MakeNetWithSubGroup(DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}_SKIN_NET),\n"
        skinBuffer += f"        AttachTo(0xd, DYNOBJ_{myShape.name.upper()}_NET),\n"
        skinBuffer += f"        SetSkinShape(DYNOBJ_{myShape.name.upper()}_SHAPE),\n"
        skinBuffer += f"        SetScale(1.0, 1.0, 1.0),\n"
        skinBuffer += f"        SetRotation(0.0, 0.0, 0.0),\n"
        skinBuffer += f"        SetAttachOffset(0.0, 0.0, 0.0),\n"
        skinBuffer += f"        MakeAttachedJoint(DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}),\n"
        skinBuffer += f"            SetRotation({rot[0]}, {rot[1]}, {rot[2]}),\n"
        skinBuffer += f"            SetScale(1.0, 1.0, 1.0),\n"
        skinBuffer += f"            SetAttachOffset({pos[0]}, {pos[1]}, {pos[2]}),\n"

        weightcount = 0
        for idx, weight in get_weights(myShape, myVertexGroup):
            if weight != 0.0:
                weightcount += 1
                skinBuffer += (
                    f"                SetSkinWeight({idx}, {weight * 100.0}),\n"
                )
        skinBuffer += f"    EndNetWithSubGroup(DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}_SKIN_NET),\n"

        return (
            f"DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}",
            f"DYNOBJ_{myShape.name.upper()}_{joint.name.upper()}_SKIN_NET",
            skinBuffer,
        )

    def export(self, armature):
        self.armature = armature
        self.namesToWrite = []

        # self.enums.append(f"DYNOBJ_MARIO_MAIN_ANIMATOR = 1001")

        # Get shape data
        vtxs = []
        tris = []
        shapes = []

        for obj in bpy.data.objects:
            if obj.parent == armature and obj.type == "MESH":
                v, t, s = self.getShapeOutput(obj.data, obj.name)
                vtxs.append(v)
                tris.append(t)
                shapes.append(s)
                self.namesToWrite.append(obj.name)

        # Get anim data and skin weights
        animData = []
        posemode(armature)
        import time

        start_time = time.time()
        for bone in armature.pose.bones:
            shapetolink, skinName, skinData = self.getSkinData(bone)
            if skinName == "":
                # No data
                pass
            elif skinName not in self.skinWeights:
                self.skinWeights[skinName] = skinData
            else:
                self.skinWeights[skinName] += skinData
            # animData.append(self.getAnimData(bone))
            # generate the commands
            self.enums.append(f"DYNOBJ_{bone.name.upper()}_ANIMDATA_GROUP")
            self.enums.append(f"DYNOBJ_{bone.name.upper()}_ANIMATOR")

        #     if shapetolink != "":
        #         self.animGroups.append(f"""
        # MakeDynObj(D_DATA_GRP, DYNOBJ_{bone.name.upper()}_ANIMDATA_GROUP),
        #     LinkWithPtr(&anim_{bone.name}),
        # MakeDynObj(D_ANIMATOR, DYNOBJ_{bone.name.upper()}_ANIMATOR),
        #     AttachTo(0x0, DYNOBJ_MARIO_MAIN_ANIMATOR),
        #     SetNodeGroup(DYNOBJ_{bone.name.upper()}_ANIMDATA_GROUP),
        #     LinkWith({shapetolink}),
        #         """)
        end_time = time.time()
        print(f"Animations exported in {end_time - start_time} seconds.")
        objectmode()

        # Get the final shape
        mainDList = self.getMainDListData("mario")

        # Write to file
        self.WriteHeader()
        self.WriteEnums()

        # for anim in animData:
        #     self.file.write(anim)

        for v, t, s in zip(vtxs, tris, shapes):
            self.file.write(v)
            self.file.write(t)
            self.file.write(s)

        self.file.write(mainDList)

    def closeFile(self):
        self.file.close()
