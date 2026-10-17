import bpy

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

        for net in self.nets:
            if self.nets[net].shape != 0:
                obj = bpy.data.objects[f"Shape_{self.nets[net].shape}"]
                mesh = obj.data
                if self.nets[net].joint:
                    weight_mesh_to_joint(obj, mesh, f"Joint_{self.nets[net].joint}")

        for joint in self.joints:
            j = self.joints[joint]
            bjoint = new_joint(f"Joint_{j.name}")
            set_joint_position(j.name, j.position, j.rotation)
            if j.animation in face.animinfos:
                print(f"animparse {joint} {j.animation}")
                parseAnimation(face, [0, 0, 0], joint, j.animation)

