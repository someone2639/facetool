import bpy
from .constants import DYNOBJ_MARIO_MAIN_NET, ROOT_ANIMATOR_NAME, DYNOBJ_MARIO_MAIN_SHAPES_GROUP

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
    set_object_weights,
    clear_object_weights,
    make_object_vertex_group,
    # position_object_at_joint,
    # get_current_object_position,
    weight_mesh_to_joint,
)

from .Animation import parseAnimation

from .Shape import Shape, constructShape

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

    def update(self, newscene):
        self.objects.update(newscene.objects)
        self.shapes.update(newscene.shapes)
        self.joints.update(newscene.joints)
        self.animations.update(newscene.animations)
        self.nets.update(newscene.nets)
        self.materials.update(newscene.materials)
        self.dataGroups.update(newscene.dataGroups)


    def build(self, face):
        for shape in self.shapes:
            s = self.shapes[shape]
            obj, mesh = new_object(shape)
            constructShape(face, s, s.materials, self.materials[s.materials])
            weight_mesh_to_joint(obj, mesh, f"Joint_{DYNOBJ_MARIO_MAIN_NET}", default_weight = 1.0)
            mod = obj.modifiers.new(f"Armature_{DYNOBJ_MARIO_MAIN_NET}", "ARMATURE")
            mod.object = get_root_animator()
            mod.vertex_group = f"Joint_{DYNOBJ_MARIO_MAIN_NET}"

        for joint in self.joints:
            j = self.joints[joint]
            bjoint = new_joint(f"Joint_{j.name}")
            # set_joint_position(j.name, j.position, j.rotation)
            set_joint_position(j.name, j.position, [0, 0, 0])

            if j.animation in face.animinfos:
                parseAnimation(face, j.rotation, joint, j.animation)
        for joint in self.joints:
            j = self.joints[joint]
            if j.parent != 0:
                parent_joint(j.name, j.parent)

        for net in self.nets:
            if self.nets[net].shape != 0:
                obj = bpy.data.objects[f"Shape_{self.nets[net].shape}"]
                mesh = obj.data
                if self.nets[net].joint:
                    print(f"WEIGHTING {self.nets[net].shape} TO {self.nets[net].joint}")
                    joint = self.joints[self.nets[net].joint]
                    weight_mesh_to_joint(obj, mesh, f"Joint_{self.nets[net].joint}")
                    set_object_weights(obj, f"Joint_{self.nets[net].joint}", joint.weights)
                    if self.nets[net].shape != 0:
                        mod = obj.modifiers.new(f"Armature_{self.nets[net].shape}", "ARMATURE")
                        mod.object = get_root_animator()
                        mod.vertex_group = f"Joint_{self.nets[net].joint}"

