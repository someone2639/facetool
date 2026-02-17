import struct
from .display_list import DLCmd
from .commands import *

fb = []


def readFile(binfile: str):
    global fb
    with open(binfile, "rb") as f:
        fb = f.read()


def readStruct(fmt: str, offset: int) -> list:
    global fb
    return struct.unpack_from(fmt, fb, offset)


class Command:
    def __init__(self, command: int, arg1: int, arg2: int, vec: list[float]):
        self.type = command
        self.arg1 = arg1
        self.arg2 = arg2
        self.vec = vec

    def __str__(self) -> str:
        return f"cmd {self.type}: ({self.arg1}, {self.arg2}) {self.vec}"


def readCMD(offset: int) -> GoddardCommand:
    global fb
    argvals = struct.unpack_from(">LLLfff", fb, offset)
    match argvals[0]:
        case DLCmd.BeginList:
            pass
        case DLCmd.UseIntegerNames:
            pass
        case DLCmd.SetInitialPosition:
            pass
        case DLCmd.SetRelativePosition:
            pass
        case DLCmd.SetWorldPosition:
            pass
        case DLCmd.SetNormal:
            pass
        case DLCmd.SetScale:
            pass
        case DLCmd.SetRotation:
            pass
        case DLCmd.SetDrawFlag:
            pass
        case DLCmd.SetFlag:
            pass
        case DLCmd.ClearFlag:
            pass
        case DLCmd.SetFriction:
            pass
        case DLCmd.SetSpring:
            pass
        case DLCmd.CallList:
            pass
        case DLCmd.SetColourNum:
            pass
        case DLCmd.MakeDynObj:
            pass
        case DLCmd.StartGroup:
            pass
        case DLCmd.EndGroup:
            pass
        case DLCmd.AddToGroup:
            pass
        case DLCmd.SetType:
            pass
        case DLCmd.SetMaterialGroup:
            pass
        case DLCmd.SetNodeGroup:
            pass
        case DLCmd.SetSkinShape:
            pass
        case DLCmd.SetPlaneGroup:
            pass
        case DLCmd.SetShapePtrPtr:
            pass
        case DLCmd.SetShapePtr:
            pass
        case DLCmd.SetShapeOffset:
            pass
        case DLCmd.SetCenterOfGravity:
            pass
        case DLCmd.LinkWith:
            pass
        case DLCmd.LinkWithPtr:
            pass
        case DLCmd.UseObj:
            pass
        case DLCmd.SetControlType:
            pass
        case DLCmd.SetSkinWeight:
            pass
        case DLCmd.SetAmbient:
            pass
        case DLCmd.SetDiffuse:
            pass
        case DLCmd.SetId:
            pass
        case DLCmd.SetMaterial:
            pass
        case DLCmd.MapMaterials:
            pass
        case DLCmd.MapVertices:
            pass
        case DLCmd.Attach:
            pass
        case DLCmd.AttachTo:
            pass
        case DLCmd.SetAttachOffset:
            pass
        case DLCmd.SetNameSuffix:
            pass
        case DLCmd.SetParamF:
            pass
        case DLCmd.SetParamPtr:
            pass
        case DLCmd.MakeNetWithSubGroup:
            pass
        case DLCmd.MakeAttachedJoint:
            pass
        case DLCmd.EndNetWithSubGroup:
            pass
        case DLCmd.MakeVertex:
            pass
        case DLCmd.MakeValPtr:
            pass
        case DLCmd.UseTexture:
            pass
        case DLCmd.SetTextureST:
            pass
        case DLCmd.MakeNetFromShape:
            pass
        case DLCmd.MakeNetFromShapePtrPtr:
            pass
        case DLCmd.EndList:
            return EndList()
        case _:
            return EndList()


def readDL(offset) -> list[Command]:
    print("Reading DL...")
    cmdList = [readCMD(offset)]
    offset += 24
    while cmdList[-1].type != int(EndList()):
        cmdList.append(readCMD(offset))
        offset += 24
    return cmdList
