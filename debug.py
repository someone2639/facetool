import bpy

def print_anim_info(bone_name: str):
    obj = bpy.context.active_object
    if obj is None or obj.type != 'ARMATURE':
        print("Error: Select an armature.")
        return

    bone = obj.pose.bones.get(bone_name)
    if bone is None:
        print(f"Error: Bone '{bone_name}' not found.")
        return

    scene = bpy.context.scene
    original_frame = scene.frame_current
    action = obj.animation_data.action if obj.animation_data else None

    if action is None:
        print("Error: Armature has no active action.")
        return

    start = int(action.frame_range[0])
    end = int(action.frame_range[1])

    print(f"Animation: {action.name}")
    print(f"Bone: {bone_name}")
    print(f"Frames: {start}-{end}")

    try:
        scene.frame_set(15)
        bpy.context.view_layer.update()

        # matrix = bone.matrix.copy()
        matrix = (obj.matrix_world @ bone.matrix).transposed()

        print(f"\nFrame {15}:")
        for row in matrix:
            print("    [" + ", ".join(f"{v:.6f}" for v in row) + ", ]")

    finally:
        scene.frame_set(original_frame)