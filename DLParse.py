from .commands import DLCmd
from .node_types import *
from .main import readDL
from .Shape import Shape
import bpy
import math

def parseDL(cmdList):
    curObjType = 0
    curObjName = 0

    curEmpty = None

    dataGrpMap = {}
    shapeMap = {}

    objMap = {}

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
                        mesh = bpy.data.meshes.new(f'Shape_{curObjName}_mesh')
                        obj = bpy.data.objects.new(f'Shape_{curObjName}', mesh)
                        scene = bpy.context.scene
                        scene.collection.objects.link(obj)
                        bpy.context.view_layer.objects.active = obj
                        objMap[curObjName] = obj
                    case DNode.D_SHAPE:
                        shapeMap[curObjName] = Shape(0,0,0)
            case DLCmd.LinkWithPtr:
                dataGrpMap[curObjName].append(cmd.arg1)
            case DLCmd.SetNodeGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].verts = cmd.arg1
            case DLCmd.SetPlaneGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].faces = cmd.arg1
            case DLCmd.SetMaterialGroup:
                if curObjType == DNode.D_SHAPE:
                    shapeMap[curObjName].materials = cmd.arg1
            case DLCmd.EndList:
                pass
            case DLCmd.SetScale:
                objMap[curObjName].scale = cmd.vec
                pass
            case DLCmd.SetRotation:
                objMap[curObjName].rotation_euler = [math.radians(r) for r in cmd.vec]
                pass
            case DLCmd.SetAttachOffset:
                objMap[curObjName].location = cmd.vec
                # objMap[curObjName].update()
                pass
            case _:
                pass