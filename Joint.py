import bpy
import math
import mathutils
from .constants import ROOT_ANIMATOR_NAME

from .blender_helpers import editmode, objectmode


class Joint:
    def __init__(self, name):
        self.name = name
        self.shape = 0
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.parent = 0  # 0 means root
        self.child = 0  # 0 maens leaf
        self.weights = {}
        self.bone = None
        self.vtxGroup = None
        self.animation = None

