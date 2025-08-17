# MIT License

# Copyright (c) 2018-2020 Nathan Letwory, Joel Putnam, Tom Svilans, Lukas Fertig

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


bl_info = {
    "name": "Goddard Importer",
    "author": "Faris Awan, someone2639",
    "version": (1, 0, 0),
    "blender": (4, 30, 0),
    "location": "3DView",
    "description": "Import the Mario Face (with every feature supported)",
    "warning": "does this show up",
    "wiki_url": "does THIS show up",
    "category": "Import-Export",
}

import bpy
from bpy.utils import register_class, unregister_class
from bpy.path import abspath
from bpy.props import StringProperty, PointerProperty, BoolProperty

from .main import readDL, readFile
from .DLParse import parseDL, addRootAnimator
from .exporter import Exporter

from bpy.types import Operator
from bpy.types import Panel, PropertyGroup

import sys, os
sys.dont_write_bytecode = True

class FaceProperties(PropertyGroup):
    gd_bin_file: StringProperty(
        name="Path to gd.bin",
        description="This file has all the face data to import.",
        subtype= 'FILE_NAME'
    )
    gd_out_file: StringProperty(
        name="Output C file",
        description="Where should this go?",
        subtype= 'FILE_NAME'
    )


class ImportFaceButton(Operator):
    """ tooltip goes here """
    bl_idname = "demo.importoperator"
    bl_label = "Import from gd.bin"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        input_file = bpy.path.abspath(context.scene.face_props.gd_bin_file)
        if input_file and os.path.isfile(input_file):
            addRootAnimator()
            readFile(input_file)
            cmdList = readDL(0)
            parseDL(cmdList)
            bpy.context.scene.frame_end = 820
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, "No import file specified!")
            return {"CANCELLED"}

class ExportFaceButton(Operator):
    """ tooltip goes here """
    bl_idname = "demo.exportoperator"
    bl_label = "Export Face as binary"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        armatureList = []
        for armature in bpy.data.objects:
            if armature.type == 'ARMATURE':
                armatureList.append(armature)

        if len(armatureList) == 0:
            self.report({"ERROR"}, "Nothing to export! Make sure you've imported or built a Mario Face!")
            return {"CANCELLED"}

        output_file = bpy.path.abspath(context.scene.face_props.gd_out_file)

        if output_file and os.path.isfile(output_file):
            pass
        else:
            self.report({"ERROR"}, "No Output file specified!")
            return {"CANCELLED"}

        exp = Exporter(output_file)

        for armature in armatureList:
            exp.export(armature)

        exp.closeFile()

        return {"FINISHED"}


class PANEL_PT_GoddardSidebar(Panel):
    bl_label = "Mario Face"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Mario Face"


    def draw(self, context):
        scene = context.scene
        faceprops = scene.face_props
        col = self.layout.column(align=True)
        col.prop(faceprops, "gd_bin_file")
        prop = col.operator(ImportFaceButton.bl_idname, text="Import Mario Face")
        col.prop(faceprops, "gd_out_file")
        prop = col.operator(ExportFaceButton.bl_idname, text="Export Mario Face")


classes = [
    ImportFaceButton,
    ExportFaceButton,
    FaceProperties,
    PANEL_PT_GoddardSidebar,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.face_props = PointerProperty(type=FaceProperties)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_3dm.some_data('INVOKE_DEFAULT')
