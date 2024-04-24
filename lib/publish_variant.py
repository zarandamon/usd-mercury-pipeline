import maya.cmds as cmds
from pxr import Usd, UsdGeom, Vt, Sdf

class UsdMeshExporter:
    def __init__(self):
        self.root_group = "root"

    def create_hierarchy(self, stage):
        # Create root prim and set it as the default prim
        root_prim = stage.DefinePrim("/" + self.root_group, "Xform")
        Usd.ModelAPI(root_prim).SetKind("component")

        stage.SetDefaultPrim(root_prim)

        # Create geo scope under root
        geo_prim = stage.DefinePrim("/" + self.root_group + "/geo", "Xform")

        # Create render and proxy scopes under geo with their respective purposes
        render_prim = stage.DefinePrim("/" + self.root_group + "/geo/render", "Scope")
        render_prim.GetAttribute("purpose").Set("render")
        proxy_prim = stage.DefinePrim("/" + self.root_group + "/geo/proxy", "Scope")
        proxy_prim.GetAttribute("purpose").Set("proxy")

        # Correctly define __class__ scope and root class
        class_path = "__class__"
        class_root_path = "/__class__/root"
        class_prim = stage.DefinePrim(class_root_path, '')

        class_prim_spec = stage.GetRootLayer().GetPrimAtPath(class_path)
        class_prim_spec.specifier = Sdf.SpecifierClass

        root_prim_spec = stage.GetRootLayer().GetPrimAtPath(class_root_path)
        root_prim_spec.specifier = Sdf.SpecifierClass
        

        # Switch from using reference to using inheritance for the root prim
        root_inherits = root_prim.GetInherits()
        # Add an inherit path to the class_root
        root_inherits.AddInherit("/__class__/root")

        return root_prim, render_prim, proxy_prim, class_prim

    def find_meshes_in_group(self, group_name):
        # Find all meshes under a specified group
        meshes = cmds.listRelatives(group_name, allDescendents=True, type='mesh')
        return meshes

    def get_extent(self, mesh_name):
        bbox = cmds.exactWorldBoundingBox(mesh_name)
        return [(bbox[0], bbox[2], bbox[4]), (bbox[3], bbox[5], bbox[1])]

    def get_face_vertex_counts(self, mesh_name):
        num_faces = cmds.polyEvaluate(mesh_name, face=True)
        face_vertex_counts = [len(cmds.polyInfo(f'{mesh_name}.f[{i}]', faceToVertex=True)[0].split()[2:]) for i in range(num_faces)]
        return face_vertex_counts

    def get_face_vertex_indices(self, mesh_name):
        face_vertex_indices = []
        num_faces = cmds.polyEvaluate(mesh_name, face=True)
        for i in range(num_faces):
            face_info = cmds.polyInfo(f"{mesh_name}.f[{i}]", faceToVertex=True)
            if face_info:
                indices = [int(idx) for idx in face_info[0].split()[2:]]
                face_vertex_indices.extend(indices)
        return face_vertex_indices

    def get_normals(self, mesh_name):
        all_faces = cmds.ls(mesh_name + ".f[*]", flatten=True)
        face_varying_normals = []
        for face in all_faces:
            face_vertices_info = cmds.polyInfo(face, fv=True)
            vertex_indices = [int(v) for v in face_vertices_info[0].split()[2:]]
            for v_idx in vertex_indices:
                normals = cmds.polyNormalPerVertex(f"{mesh_name}.vtxFace[{v_idx}][{all_faces.index(face)}]", query=True, xyz=True)
                face_varying_normals.append(tuple(normals))
        return face_varying_normals

    def get_points(self, mesh_name):
        all_vertices = cmds.ls(mesh_name + ".vtx[*]", flatten=True)
        points = [tuple(cmds.pointPosition(vertex, world=True)) for vertex in all_vertices]
        return points

    def get_uv_coords_and_indices(self, mesh_name):
        uv_coords = []
        uv_indices = []
        if cmds.polyEvaluate(mesh_name, uvcoord=True) > 0:
            all_uvs = cmds.polyListComponentConversion(mesh_name, toUV=True)
            all_uvs = cmds.ls(all_uvs, flatten=True)
            for uv in all_uvs:
                u, v = cmds.polyEditUV(uv, query=True, u=True, v=True)
                uv_coords.append((u, v))
                uv_indices.append(int(uv.split("[")[-1].rstrip("]")))
        return uv_coords, uv_indices

    def get_diffuse_color(self, mesh_name):
        shading_groups = cmds.listConnections(mesh_name, type='shadingEngine')
        if not shading_groups:
            return None

        # Find the shader connected to the shading group
        shaders = cmds.ls(cmds.listConnections(shading_groups[0]), materials=1)
        if not shaders:
            return None

        # Get the diffuse color connected to the shader
        color = cmds.getAttr(f"{shaders[0]}.baseColor")[0]  # This will get the first item from the returned tuple
        
        # Get the number of vertices to replicate the color
        all_vertices = cmds.ls(mesh_name + ".vtx[*]", flatten=True)
        num_vertices = len(all_vertices)

        # Replicate the color for each vertex
        replicated_colors = [color for _ in range(num_vertices)]

        return replicated_colors
    
    def convert_mesh_to_usd(self, mesh_name, parent, stage):

        mesh = UsdGeom.Mesh.Define(stage, f'{parent}/{mesh_name}')

        # Set mesh attributes

        # Points (vertices)
        points = self.get_points(mesh_name)
        mesh.GetOrientationAttr().Set("rightHanded")
        mesh.CreatePointsAttr().Set(Vt.Vec3fArray(points))

        # Face Vertex Counts
        face_vertex_counts = self.get_face_vertex_counts(mesh_name)
        mesh.CreateFaceVertexCountsAttr().Set(Vt.IntArray(face_vertex_counts))

        # Face Vertex Indices
        face_vertex_indices = self.get_face_vertex_indices(mesh_name)
        mesh.CreateFaceVertexIndicesAttr().Set(Vt.IntArray(face_vertex_indices))

        # Normals
        normals = self.get_normals(mesh_name)
        mesh.CreateNormalsAttr().Set(Vt.Vec3fArray(normals))
        mesh.SetNormalsInterpolation("faceVarying")
       

        # UVs
        uv_coords, uv_indices = self.get_uv_coords_and_indices(mesh_name)
        if uv_coords:
            # Access the Primvars API for the mesh and create a Primvar for the UVs
            uv_set_name = 'st'  # Standard name for primary UV set
            uv_primvar = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(uv_set_name,
                                                                 Sdf.ValueTypeNames.TexCoord2fArray,
                                                                 UsdGeom.Tokens.faceVarying)
            uv_primvar.Set(Vt.Vec2fArray(uv_coords))
        
            uv_primvar.SetIndices(Vt.IntArray(uv_indices))

        # Extent
        extent = self.get_extent(mesh_name)
        mesh.CreateExtentAttr().Set(Vt.Vec3fArray(extent))

        # Set mesh interpolation
        subdivisionSchemeAttr = mesh.GetPrim().GetAttribute('subdivisionScheme')
        subdivisionSchemeAttr.Set(UsdGeom.Tokens.none)

        # Get the shader color
        shader_colors = self.get_diffuse_color(mesh_name)
        if shader_colors:
            mesh_prim = UsdGeom.Mesh.Get(stage, f'{parent}/{mesh_name}')
            display_color_attr = mesh_prim.CreateDisplayColorPrimvar(UsdGeom.Tokens.vertex)
            display_color_attr.Set(shader_colors)

        return mesh
        
    def export_to_usd(self, filepath):
        # Create a new USD stage
        stage = Usd.Stage.CreateNew(filepath)
        
        # Set up the hierarchy
        self.create_hierarchy(stage)
        
        # Export meshes under 'render'
        render_meshes = self.find_meshes_in_group("render")
        for mesh_name in render_meshes:
            self.convert_mesh_to_usd(mesh_name, "/root/geo/render", stage)

        # Export meshes under 'proxy'
        proxy_meshes = self.find_meshes_in_group("proxy")
        for mesh_name in proxy_meshes:
            self.convert_mesh_to_usd(mesh_name, "/root/geo/proxy", stage)

        # Save the stage
        stage.GetRootLayer().Export(filepath)
