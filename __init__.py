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

from .main import readDL, readFile
from .DLParse import parseDL

from bpy.types import Operator
from bpy.types import Panel

class TLA_OT_operator(Operator):
    """ tooltip goes here """
    bl_idname = "demo.operator"
    bl_label = "I'm a Skeleton Operator"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        readFile()
        cmdList = readDL(0)
        parseDL(cmdList)
        return {"FINISHED"}


class TLA_PT_sidebar(Panel):
    bl_label = "Mario Face"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Mario Face"

    def draw(self, context):
        col = self.layout.column(align=True)
        prop = col.operator(TLA_OT_operator.bl_idname, text="Import Mario Face")


classes = [
    TLA_OT_operator,
    TLA_PT_sidebar,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_3dm.some_data('INVOKE_DEFAULT')
