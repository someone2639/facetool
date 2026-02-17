from .commands import GoddardCommand

class DLCmd:
    BeginList = 53716
    UseIntegerNames = 0
    SetInitialPosition = 1
    SetRelativePosition = 2
    SetWorldPosition = 3
    SetNormal = 4
    SetScale = 5
    SetRotation = 6
    SetDrawFlag = 7
    SetFlag = 8
    ClearFlag = 9
    SetFriction = 10
    SetSpring = 11
    CallList = 12
    SetColourNum = 13
    MakeDynObj = 15
    StartGroup = 16
    EndGroup = 17
    AddToGroup = 18
    SetType = 19
    SetMaterialGroup = 20
    SetNodeGroup = 21
    SetSkinShape = 22
    SetPlaneGroup = 23
    SetShapePtrPtr = 24
    SetShapePtr = 25
    SetShapeOffset = 26
    SetCenterOfGravity = 27
    LinkWith = 28
    LinkWithPtr = 29
    UseObj = 30
    SetControlType = 31
    SetSkinWeight = 32
    SetAmbient = 33
    SetDiffuse = 34
    SetId = 35
    SetMaterial = 36
    MapMaterials = 37
    MapVertices = 38
    Attach = 39
    AttachTo = 40
    SetAttachOffset = 41
    SetNameSuffix = 43
    SetParamF = 44
    SetParamPtr = 45
    MakeNetWithSubGroup = 46
    MakeAttachedJoint = 47
    EndNetWithSubGroup = 48
    MakeVertex = 49
    MakeValPtr = 50
    UseTexture = 52
    SetTextureST = 53
    MakeNetFromShape = 54
    MakeNetFromShapePtrPtr = 55
    EndList = 58

class DisplayList:
    def __init__(self, name: str, cmdlist: list[GoddardCommand]):
        self.cmdlist = cmdlist
        self.name = name

    def write(self) -> str:
        initStr  = f"struct DynList dynlist_{self.name}[] = {{\n"
        for cmd in self.cmdlist:
            initStr += str(cmd)
        initStr += "};"

        return initStr
