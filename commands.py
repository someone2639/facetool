class DLCmd:
    BeginList = 53716
    EndList = 58
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

CommandToDLCmd = {
    "BeginList": DLCmd.BeginList,
    "EndList": DLCmd.EndList,
    "UseIntegerNames": DLCmd.UseIntegerNames,
    "SetInitialPosition": DLCmd.SetInitialPosition,
    "SetRelativePosition": DLCmd.SetRelativePosition,
    "SetWorldPosition": DLCmd.SetWorldPosition,
    "SetNormal": DLCmd.SetNormal,
    "SetScale": DLCmd.SetScale,
    "SetRotation": DLCmd.SetRotation,
    "SetDrawFlag": DLCmd.SetDrawFlag,
    "SetFlag": DLCmd.SetFlag,
    "ClearFlag": DLCmd.ClearFlag,
    "SetFriction": DLCmd.SetFriction,
    "SetSpring": DLCmd.SetSpring,
    "CallList": DLCmd.CallList,
    "SetColourNum": DLCmd.SetColourNum,
    "MakeDynObj": DLCmd.MakeDynObj,
    "StartGroup": DLCmd.StartGroup,
    "EndGroup": DLCmd.EndGroup,
    "AddToGroup": DLCmd.AddToGroup,
    "SetType": DLCmd.SetType,
    "SetMaterialGroup": DLCmd.SetMaterialGroup,
    "SetNodeGroup": DLCmd.SetNodeGroup,
    "SetSkinShape": DLCmd.SetSkinShape,
    "SetPlaneGroup": DLCmd.SetPlaneGroup,
    "SetShapePtrPtr": DLCmd.SetShapePtrPtr,
    "SetShapePtr": DLCmd.SetShapePtr,
    "SetShapeOffset": DLCmd.SetShapeOffset,
    "SetCenterOfGravity": DLCmd.SetCenterOfGravity,
    "LinkWith": DLCmd.LinkWith,
    "LinkWithPtr": DLCmd.LinkWithPtr,
    "UseObj": DLCmd.UseObj,
    "SetControlType": DLCmd.SetControlType,
    "SetSkinWeight": DLCmd.SetSkinWeight,
    "SetAmbient": DLCmd.SetAmbient,
    "SetDiffuse": DLCmd.SetDiffuse,
    "SetId": DLCmd.SetId,
    "SetMaterial": DLCmd.SetMaterial,
    "MapMaterials": DLCmd.MapMaterials,
    "MapVertices": DLCmd.MapVertices,
    "Attach": DLCmd.Attach,
    "AttachTo": DLCmd.AttachTo,
    "SetAttachOffset": DLCmd.SetAttachOffset,
    "SetNameSuffix": DLCmd.SetNameSuffix,
    "SetParamF": DLCmd.SetParamF,
    "SetParamPtr": DLCmd.SetParamPtr,
    "MakeNetWithSubGroup": DLCmd.MakeNetWithSubGroup,
    "MakeAttachedJoint": DLCmd.MakeAttachedJoint,
    "EndNetWithSubGroup": DLCmd.EndNetWithSubGroup,
    "MakeVertex": DLCmd.MakeVertex,
    "MakeValPtr": DLCmd.MakeValPtr,
    "UseTexture": DLCmd.UseTexture,
    "SetTextureST": DLCmd.SetTextureST,
    "MakeNetFromShape": DLCmd.MakeNetFromShape,
    "MakeNetFromShapePtrPtr": DLCmd.MakeNetFromShapePtrPtr,
    "EndList": DLCmd.EndList,
}
