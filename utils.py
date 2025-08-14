import bpy
import math

def editmode(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bpy.context.mode != "EDIT":
        bpy.ops.object.mode_set(mode="EDIT")

def posemode(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bpy.context.mode != "POSE":
        bpy.ops.object.mode_set(mode="POSE")

def objectmode():
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode='OBJECT')

def to_xzy(xyz):
    return [xyz[0], xyz[2], xyz[1]]

def vec_deg2rad(rot):
    return [math.radians(angle) for angle in to_xzy(rot)]
