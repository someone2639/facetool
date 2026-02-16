from .main import readStruct
import bpy
import bmesh
from .GMaterial import matGroups
from .utils import coord_space_correction


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


def readVerts(offset, count):
    print(f"Reading {count} vertices from {offset}")
    ret = []
    for i in range(count):
        v = readStruct(">hhh", offset)
        ret.append(v)
        offset += 6
    return ret


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


def readFaces(offset, count):
    retFaces = []
    retMats = []
    for i in range(count):
        v = readStruct(">hhhh", offset)
        retFaces.append([v[1], v[2], v[3]])
        retMats.append(v[0])
        offset += 8
    return (retFaces, retMats)


def constructShape(oId, shape):
    (v_count, flag, v_offset) = readStruct(">LLL", shape.verts)
    (f_count, flag, f_offset) = readStruct(">LLL", shape.faces)

    vertices = readVerts(v_offset, v_count)
    faces, matIndices = readFaces(f_offset, f_count)

    mesh = bpy.data.meshes[f"Shape_{oId}_mesh"]
    mesh.from_pydata(vertices, [], faces)
    registerMats(bpy.data.objects[f"Shape_{oId}"], shape.materials)
    for i, f in enumerate(mesh.polygons):
        f.material_index = matIndices[i]
        f.use_smooth = True
