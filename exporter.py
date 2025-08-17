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
from .utils import editmode, posemode, objectmode

# TODO: binary exporter too (as a separate thing?)
# TODO: write all names into an enum before writing data
class Exporter():
    def __init__(self, file, is_binary = False):
        self.is_binary = is_binary
        self.armature = None
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

    def WriteShape(self, mesh, name):
        # export vertices
        vertBuffer = f"static s16 verts_{name}[][3] = {{"

        for i, vtx in enumerate(mesh.vertices):
            vertBuffer += f"{{ {vtx.co[0]}, {vtx.co[1]}, {vtx.co[2]} }}, "
        vertBuffer += f"}};\n"
        vertBuffer += f"static struct GdVtxData vtx_{name} = {{ ARRAY_COUNT(verts_{name}), 1, verts_{name}}};\n"

        self.file.write(vertBuffer)

        # export triangles
        triBuffer = f"static u16 facedata_{name}[][4] = {{"

        for i, poly in enumerate(mesh.polygons):
            vtxIdx = poly.vertices
            # TODO: make sure theres no n-gons
            triBuffer += f"{{ {poly.material_index}, {vtxIdx[0]}, {vtxIdx[1]}, {vtxIdx[2]} }}, "

        triBuffer += f"}};\n"
        triBuffer += f"static struct GdFaceData faces_{name} = {{ ARRAY_COUNT(facedata_{name}), 1, facedata_{name}}};\n"

        self.file.write(triBuffer)

        # Start dynlist, link vtx and faces
        dynlistBuf =  f"struct Dynlist dynlist_{name}_shape[] = {{\n"
        dynlistBuf +=  "    BeginList(),\n"
        dynlistBuf += f"        MakeDynObj(D_DATA_GRP, DYNOBJ_{name.upper()}_VTX_GROUP),\n"
        dynlistBuf += f"            LinkWithPtr(&vtx_{name.upper()}),\n"
        dynlistBuf += f"        MakeDynObj(D_DATA_GRP, DYNOBJ_{name.upper()}_TRI_GROUP),\n"
        dynlistBuf += f"            LinkWithPtr(&faces_{name.upper()}),\n"

        # Write the Material Group
        dynlistBuf += f"    StartGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        for i, mtl in enumerate(mesh.materials):
            color = mtl.node_tree.nodes["Principled BSDF"].inputs[0].default_value
            dynlistBuf +=  "        MakeDynObj(D_MATERIAL, 0),\n"
            dynlistBuf += f"            SetId({i}),\n"
            dynlistBuf += f"            SetAmbient({color[0]}, {color[1]}, {color[2]}),\n"
            # TODO: no diffuse color yet
            dynlistBuf += f"            SetDiffuse({color[0]}, {color[1]}, {color[2]}),\n"

        dynlistBuf += f"    EndGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        # Make the Shape definition
        dynlistBuf += f"    MakeDynObj(D_SHAPE, DYNOBJ_{name.upper()}_SHAPE),\n"
        dynlistBuf += f"        SetNodeGroup(DYNOBJ_{name.upper()}_VTX_GROUP),\n"
        dynlistBuf += f"        SetPlaneGroup(DYNOBJ_{name.upper()}_TRI_GROUP),\n"
        dynlistBuf += f"        SetMaterialGroup(DYNOBJ_{name.upper()}_MTL_GROUP),\n"

        # Finish
        dynlistBuf +=  "    EndList(),\n"
        dynlistBuf +=  "};\n"
        self.file.write(dynlistBuf)

    def WriteAnimation(joint):
        pass

    def export(self, armature):
        self.armature = armature
        self.WriteHeader()

        for obj in bpy.data.objects:
            if obj.parent == armature and obj.type == "MESH":
                self.WriteShape(obj.data, obj.name)

    def closeFile(self):
        self.file.close()

