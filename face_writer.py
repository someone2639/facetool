import bpy

outputfmts: dict[str, str] = {
    "animdata": "s16 animdata_%s[][%d] = {",
    "animinfo": "struct AnimDataInfo anim_%s[] = {",
    "vtxdata": "s16 verts_%s[][%d] = {",
    "vtxinfo": "struct GdVtxData %s = {",
    "facedata": "u16 facedata_%s[][%d] = {",
    "faceinfo": "struct GdFaceData %s = {",
    "dynlist": "struct DynList %s[] = {",
}

# def write_symbol_to_file(filename: str):

def export(self):
    # Get the active object
    obj = bpy.context.active_object

    if obj and obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        print(f"Action Name: {action.name}")
        
        # Loop through all F-curves (animation channels like location, rotation)
        for fcurve in action.fcurves:
            print(f"Channel: {fcurve.data_path} (Index: {fcurve.array_index})")
            # Print frame and value for each keyframe point
            for kp in fcurve.keyframe_points:
                print(f"  Frame: {kp.co[0]}, Value: {kp.co[1]}")
    else:
        raise PluginError("Select the Armature you want to export!")

