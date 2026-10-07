import bpy
import bmesh
from .GMaterial import matGroups
from .utils import position_coord_space_correction


class Shape:
    def __init__(self, name, verts, faces, mats):
        self.name = name
        self.verts = verts
        self.faces = faces
        self.mats = mats


def add_mesh(m, verts, faces, col_name="Collection"):
    mesh = m
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections[col_name]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.from_pydata(verts, [], faces)

def registerMats(obj, matID):
    mats = matGroups[matID]

    for i, m in enumerate(mats):
        new_mat = bpy.data.materials.new(f"GDMaterial_Group{matID}_{i}")
        new_mat.use_nodes = True
        node_tree = new_mat.node_tree
        nodes = node_tree.nodes

        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = tuple(m.ambient)
        # TODO: where to put diffuse color? is it a normal?
        # bsdf.inputs['Base Color'].default_value = tuple(m.diffuse)

        obj.data.materials.append(new_mat)
        obj.active_material_index = len(obj.data.materials) - 1

def constructShape(face, oId, shape):
    mesh = bpy.data.meshes[f"Shape_{oId}_mesh"]
    print(f"before meshing {oId}")
    mesh.from_pydata(
        [position_coord_space_correction(v) for v in face.vtxdatas[face.vtxinfos[shape.verts][0]]],
        [],
        [i[1:4] for i in face.facedatas[face.faceinfos[shape.faces][0]]]
    )
    print(f"after meshing {oId}")
    registerMats(bpy.data.objects[f"Shape_{oId}"], shape.materials)
    matIndices = [i[0] for i in face.facedatas[face.faceinfos[shape.faces][0]]]
    for i, f in enumerate(mesh.polygons):
        f.material_index = matIndices[i]
        f.use_smooth = True
