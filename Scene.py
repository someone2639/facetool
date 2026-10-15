
from .blender_helpers import (
    editmode,
    objectmode,
    posemode,

    new_joint,
    set_joint_position,
    parent_joint,

    get_root_animator,

    new_object,
    set_object_position,
    set_object_parent,
    set_object_joint,
    clear_object_weights,
    make_object_vertex_group,
    # position_object_at_joint,
    # get_current_object_position,
    weight_mesh_to_joint,
)

class Scene():
    def __init__(self):
        self.end_frame = 0
        self.objects = {}
        self.shapes = {}
        self.joints = {}
        self.animations = {}
        self.nets = {}
        self.materials = {}
        self.dataGroups = {}

    def build(self):
        pass

