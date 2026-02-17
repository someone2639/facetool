from abc import ABC, abstractmethod

class GoddardCommand(ABC):
    @abstractmethod
    def __int__(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str: ...

class BeginList(GoddardCommand):
    def __init__(self):
        pass

    def __int__(self) -> int:
        return 53716

    def __str__(self) -> str:
        return "BeginList(),"

class EndList(GoddardCommand):
    def __init__(self):
        pass

    def __int__(self) -> int:
        return 58

    def __str__(self) -> str:
        return "EndList(),"

class UseIntegerNames(GoddardCommand):
    def __init__(self, enable: int):
        self.enable = enable

    def __init__(self):
        self.enable = False

    def __int__(self) -> int:
        return 0

    def __str__(self) -> str:
        return f"UseIntegerNames({'TRUE' if self.enable else 'FALSE'}),"

class SetInitialPosition(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 1

    def __str__(self) -> str:
        return f"SetInitialPosition({self.x}, {self.y}, {self.z}),"


class SetRelativePosition(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 2

    def __str__(self) -> str:
        return f"SetRelativePosition({self.x}, {self.y}, {self.z}),"


class SetWorldPosition(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 3

    def __str__(self) -> str:
        return f"SetWorldPosition({self.x}, {self.y}, {self.z}),"


class SetNormal(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 4

    def __str__(self) -> str:
        return f"SetNormal({self.x}, {self.y}, {self.z}),"


class SetScale(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 5

    def __str__(self) -> str:
        return f"SetScale({self.x}, {self.y}, {self.z}),"


class SetRotation(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 6

    def __str__(self) -> str:
        return f"SetRotation({self.x}, {self.y}, {self.z}),"


class SetDrawFlag(GoddardCommand):
    def __init__(self, flags: int):
        self.flags = flags

    def __init__(self):
        self.flags = 0

    def __int__(self) -> int:
        return 7

    def __str__(self) -> str:
        return f"SetDrawFlag({self.flags}),"


class SetFlag(GoddardCommand):
    def __init__(self, flags: int):
        self.flags = flags

    def __init__(self):
        self.flags = 0

    def __int__(self) -> int:
        return 8

    def __str__(self) -> str:
        return f"SetFlag({self.flags}),"


class ClearFlag(GoddardCommand):
    def __init__(self, flags: int):
        self.flags = flags

    def __init__(self):
        self.flags = 0

    def __int__(self) -> int:
        return 9

    def __str__(self) -> str:
        return f"ClearFlag({self.flags}),"


class SetFriction(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 10

    def __str__(self) -> str:
        return f"SetFriction({self.x}, {self.y}, {self.z}),"


class SetSpring(GoddardCommand):
    def __init__(self, spring: float):
        self.spring = spring

    def __init__(self):
        self.spring = 0

    def __int__(self) -> int:
        return 11

    def __str__(self) -> str:
        return f"SetSpring({self.spring}),"


class CallList(GoddardCommand):
    def __init__(self, list_: int):
        self.list = list_

    def __init__(self):
        self.list = 0

    def __int__(self) -> int:
        return 12

    def __str__(self) -> str:
        return f"CallList({self.list}),"


class SetColourNum(GoddardCommand):
    def __init__(self, colourNum: int):
        self.colourNum = colourNum

    def __init__(self):
        self.colourNum = 0

    def __int__(self) -> int:
        return 13

    def __str__(self) -> str:
        return f"SetColourNum({self.colourNum}),"


class MakeDynObj(GoddardCommand):
    def __init__(self, type: int, name: int):
        self.type = type
        self.name = name

    def __init__(self):
        self.type = 0
        self.name = 0

    def __int__(self) -> int:
        return 15

    def __str__(self) -> str:
        return f"MakeDynObj({self.type}, {self.name}),"


class StartGroup(GoddardCommand):
    def __init__(self, grpName: int):
        self.grpName = grpName

    def __init__(self):
        self.grpName = 0

    def __int__(self) -> int:
        return 16

    def __str__(self) -> str:
        return f"StartGroup({self.grpName}),"


class EndGroup(GoddardCommand):
    def __init__(self, grpName: int):
        self.grpName = grpName

    def __init__(self):
        self.grpName = 0

    def __int__(self) -> int:
        return 17

    def __str__(self) -> str:
        return f"EndGroup({self.grpName}),"


class AddToGroup(GoddardCommand):
    def __init__(self, grpName: int):
        self.grpName = grpName

    def __init__(self):
        self.grpName = 0

    def __int__(self) -> int:
        return 18

    def __str__(self) -> str:
        return f"AddToGroup({self.grpName}),"


class SetType(GoddardCommand):
    def __init__(self, objType: int):
        self.objType = objType

    def __init__(self):
        self.objType = 0

    def __int__(self) -> int:
        return 19

    def __str__(self) -> str:
        return f"SetType({self.objType}),"


class SetMaterialGroup(GoddardCommand):
    def __init__(self, mtlGrpName: int):
        self.mtlGrpName = mtlGrpName

    def __init__(self):
        self.mtlGrpName = 0

    def __int__(self) -> int:
        return 20

    def __str__(self) -> str:
        return f"SetMaterialGroup({self.mtlGrpName}),"


class SetNodeGroup(GoddardCommand):
    def __init__(self, grpName: int):
        self.grpName = grpName

    def __init__(self):
        self.grpName = 0

    def __int__(self) -> int:
        return 21

    def __str__(self) -> str:
        return f"SetNodeGroup({self.grpName}),"


class SetSkinShape(GoddardCommand):
    def __init__(self, shapeName: int):
        self.shapeName = shapeName

    def __init__(self):
        self.shapeName = 0

    def __int__(self) -> int:
        return 22

    def __str__(self) -> str:
        return f"SetSkinShape({self.shapeName}),"


class SetPlaneGroup(GoddardCommand):
    def __init__(self, planeGrpName: int):
        self.planeGrpName = planeGrpName

    def __init__(self):
        self.planeGrpName = 0

    def __int__(self) -> int:
        return 23

    def __str__(self) -> str:
        return f"SetPlaneGroup({self.planeGrpName}),"


class SetShapePtrPtr(GoddardCommand):
    def __init__(self, shapePtr: int):
        self.shapePtr = shapePtr

    def __init__(self):
        self.shapePtr = 0

    def __int__(self) -> int:
        return 24

    def __str__(self) -> str:
        return f"SetShapePtrPtr({self.shapePtr}),"


class SetShapePtr(GoddardCommand):
    def __init__(self, shapeName: int):
        self.shapeName = shapeName

    def __init__(self):
        self.shapeName = 0

    def __int__(self) -> int:
        return 25

    def __str__(self) -> str:
        return f"SetShapePtr({self.shapeName}),"


class SetShapeOffset(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 26

    def __str__(self) -> str:
        return f"SetShapeOffset({self.x}, {self.y}, {self.z}),"


class SetCenterOfGravity(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 27

    def __str__(self) -> str:
        return f"SetCenterOfGravity({self.x}, {self.y}, {self.z}),"


class LinkWith(GoddardCommand):
    def __init__(self, w1: int):
        self.w1 = w1

    def __init__(self):
        self.w1 = 0

    def __int__(self) -> int:
        return 28

    def __str__(self) -> str:
        return f"LinkWith({self.w1}),"


class LinkWithPtr(GoddardCommand):
    def __init__(self, w1: int):
        self.w1 = w1

    def __init__(self):
        self.w1 = 0

    def __int__(self) -> int:
        return 29

    def __str__(self) -> str:
        return f"LinkWithPtr({self.w1}),"


class UseObj(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 30

    def __str__(self) -> str:
        return f"UseObj({self.name}),"


class SetControlType(GoddardCommand):
    def __init__(self, w2: int):
        self.w2 = w2

    def __init__(self):
        self.w2 = 0

    def __int__(self) -> int:
        return 31

    def __str__(self) -> str:
        return f"SetControlType({self.w2}),"


class SetSkinWeight(GoddardCommand):
    def __init__(self, vtxNum: int, weight: float):
        self.vtxNum = vtxNum
        self.weight = weight

    def __init__(self):
        self.vtxNum = 0
        self.weight = 0

    def __int__(self) -> int:
        return 32

    def __str__(self) -> str:
        return f"SetSkinWeight({self.vtxNum}, {self.weight}),"


class SetAmbient(GoddardCommand):
    def __init__(self, r: float, g: float, b: float):
        self.r, self.g, self.b = r, g, b

    def __init__(self):
        self.r, self.g, self.b = 0, 0, 0

    def __int__(self) -> int:
        return 33

    def __str__(self) -> str:
        return f"SetAmbient({self.r}, {self.g}, {self.b}),"


class SetDiffuse(GoddardCommand):
    def __init__(self, r: float, g: float, b: float):
        self.r, self.g, self.b = r, g, b

    def __init__(self):
        self.r, self.g, self.b = 0, 0, 0

    def __int__(self) -> int:
        return 34

    def __str__(self) -> str:
        return f"SetDiffuse({self.r}, {self.g}, {self.b}),"


class SetId(GoddardCommand):
    def __init__(self, id: int):
        self.id = id

    def __init__(self):
        self.id = 0

    def __int__(self) -> int:
        return 35

    def __str__(self) -> str:
        return f"SetId({self.id}),"


class SetMaterial(GoddardCommand):
    def __init__(self, mat_id: int):
        self.mat_id = mat_id

    def __init__(self):
        self.mat_id = 0

    def __int__(self) -> int:
        return 36

    def __str__(self) -> str:
        return f"SetMaterial({self.mat_id}),"


class MapMaterials(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 37

    def __str__(self) -> str:
        return f"MapMaterials({self.name}),"


class MapVertices(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 38

    def __str__(self) -> str:
        return f"MapVertices({self.name}),"


class Attach(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 39

    def __str__(self) -> str:
        return f"Attach({self.name}),"


class AttachTo(GoddardCommand):
    def __init__(self, flags: int, name: int):
        self.flags = flags
        self.name = name

    def __init__(self):
        self.flags = 0
        self.name = 0

    def __int__(self) -> int:
        return 40

    def __str__(self) -> str:
        return f"AttachTo({self.flags}, {self.name}),"


class SetAttachOffset(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 41

    def __str__(self) -> str:
        return f"SetAttachOffset({self.x}, {self.y}, {self.z}),"


class SetNameSuffix(GoddardCommand):
    def __init__(self, suffix: str):
        self.suffix = suffix

    def __init__(self):
        self.suffix = ""

    def __int__(self) -> int:
        return 43

    def __str__(self) -> str:
        return f"SetNameSuffix({self.suffix}),"


class SetParamF(GoddardCommand):
    def __init__(self, param: int, value: float):
        self.param = param
        self.value = value

    def __init__(self):
        self.param = 0
        self.value = 0

    def __int__(self) -> int:
        return 44

    def __str__(self) -> str:
        return f"SetParamF({self.param}, {self.value}),"


class SetParamPtr(GoddardCommand):
    def __init__(self, param: int, value: int):
        self.param = param
        self.value = value

    def __init__(self):
        self.param = 0
        self.value = 0

    def __int__(self) -> int:
        return 45

    def __str__(self) -> str:
        return f"SetParamPtr({self.param}, {self.value}),"


class MakeNetWithSubGroup(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 46

    def __str__(self) -> str:
        return f"MakeNetWithSubGroup({self.name}),"


class MakeAttachedJoint(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 47

    def __str__(self) -> str:
        return f"MakeAttachedJoint({self.name}),"


class EndNetWithSubGroup(GoddardCommand):
    def __init__(self, name: int):
        self.name = name

    def __init__(self):
        self.name = 0

    def __int__(self) -> int:
        return 48

    def __str__(self) -> str:
        return f"EndNetWithSubGroup({self.name}),"


class MakeVertex(GoddardCommand):
    def __init__(self, x: float, y: float, z: float):
        self.x, self.y, self.z = x, y, z

    def __init__(self):
        self.x, self.y, self.z = 0, 0, 0

    def __int__(self) -> int:
        return 49

    def __str__(self) -> str:
        return f"MakeVertex({self.x}, {self.y}, {self.z}),"


class MakeValPtr(GoddardCommand):
    def __init__(self, ptr_id: int, flags: int, ptr_type: int, offset: float):
        self.ptr_id = ptr_id
        self.flags = flags
        self.ptr_type = ptr_type
        self.offset = offset

    def __init__(self):
        self.ptr_id = 0
        self.flags = 0
        self.ptr_type = 0
        self.offset = 0.0

    def __int__(self) -> int:
        return 50

    def __str__(self) -> str:
        return f"MakeValPtr({self.ptr_id}, {self.flags}, {self.ptr_type}, {self.offset}),"


class UseTexture(GoddardCommand):
    def __init__(self, texture: int):
        self.texture = texture

    def __init__(self):
        self.texture = 0

    def __int__(self) -> int:
        return 52

    def __str__(self) -> str:
        return f"UseTexture({self.texture}),"


class SetTextureST(GoddardCommand):
    def __init__(self, s: float, t: float):
        self.s = s
        self.t = t

    def __init__(self):
        self.s, self.t = 0, 0

    def __int__(self) -> int:
        return 53

    def __str__(self) -> str:
        return f"SetTextureST({self.s}, {self.t}),"


class MakeNetFromShape(GoddardCommand):
    def __init__(self, shape: int):
        self.shape = shape

    def __init__(self):
        self.shape = 0

    def __int__(self) -> int:
        return 54

    def __str__(self) -> str:
        return f"MakeNetFromShape({self.shape}),"


class MakeNetFromShapePtrPtr(GoddardCommand):
    def __init__(self, ptr: int):
        self.ptr = ptr

    def __init__(self):
        self.ptr = 0

    def __int__(self) -> int:
        return 55

    def __str__(self) -> str:
        return f"MakeNetFromShapePtrPtr({self.ptr}),"
