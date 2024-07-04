bl_info = {
    "name": "Cyclorama",
    "author": "Vaibhav",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Cyclorama",
    "description": "Creates a versatile Cyclorama Wall mesh with customizable wall options, adjustable dimensions, and an integrated bevel modifier for smooth curvature control.",
    "category": "Add Mesh",
}

import bpy
import os
from bpy.types import Operator
from bpy.props import FloatProperty, BoolProperty, EnumProperty, StringProperty, IntProperty
import bpy.utils.previews
import bmesh

# Global variable to store icons
icons = None

class MESH_OT_cyc_wall(bpy.types.Operator):
    bl_idname = "mesh.cyc_wall"
    bl_label = "Cyclorama"
    bl_description = "Construct a customizable cyclorama"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: FloatProperty(
        name="Width",
        description="Size along the X axis",
        default=10.0,
    )

    size_y: FloatProperty(
        name="Depth",
        description="Size along the Y axis",
        default=8.0,
    )

    size_z: FloatProperty(
        name="Height",
        description="Height of the Wall along the Z axis",
        default=5.0,
    )

    left_wall: BoolProperty(
        name="Left Wall",
        description="Include the left wall",
        default=False,
    )

    right_wall: BoolProperty(
        name="Right Wall",
        description="Include the right wall",
        default=False,
    )

    ceiling: BoolProperty(
        name="Ceiling",
        description="Include the ceiling",
        default=False,
    )

    bevel_width: FloatProperty(
        name="Bevel Width",
        description="Width of the bevel",
        default=2.0,
    )

    bevel_segments: IntProperty(
        name="Bevel Segments",
        description="Number of segments for the bevel",
        default=24,
    )

    material: EnumProperty(
        name="Material",
        description="Choose a material for the cyclorama wall",
        items=[
            ('DEFAULT', "Default", "Default material"),
            ('WHITE', "White", "White material"),
            ('CUSTOM', "Custom", "Custom material")
        ],
        default='DEFAULT'
    )

    texture_path: StringProperty(
        name="Texture Path",
        description="Path to a custom texture image",
        default="",
        subtype='FILE_PATH'
    )

    def execute(self, context):
        # Create a new mesh
        mesh = bpy.data.meshes.new(name="Cyclorama")
        obj = bpy.data.objects.new("Cyclorama", mesh)

        # Link it to scene
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Construct the planes using bmesh
        bm = bmesh.new()

        # Base vertices for Floor and Back Wall
        v1 = bm.verts.new((-self.size_x/2, -self.size_y/2, 0))
        v2 = bm.verts.new((self.size_x/2, -self.size_y/2, 0))
        v3 = bm.verts.new((self.size_x/2, self.size_y/2, 0))
        v4 = bm.verts.new((-self.size_x/2, self.size_y/2, 0))
        v5 = bm.verts.new((-self.size_x/2, self.size_y/2, self.size_z))
        v6 = bm.verts.new((self.size_x/2, self.size_y/2, self.size_z))

        # Create Floor and Back Wall
        bm.faces.new([v1, v2, v3, v4])  # Floor
        bm.faces.new([v4, v3, v6, v5])  # Back Wall

        if self.left_wall:
            # Left Wall vertices
            v7 = bm.verts.new((-self.size_x/2, -self.size_y/2, self.size_z))
            bm.faces.new([v1, v4, v5, v7])  # Left Wall

        if self.right_wall:
            # Right Wall vertices
            v8 = bm.verts.new((self.size_x/2, -self.size_y/2, self.size_z))
            bm.faces.new([v8, v6, v3, v2])  # Right Wall

        if self.ceiling:
            # Use previously created vertices if walls were added
            v7 = v7 if self.left_wall else bm.verts.new((-self.size_x/2, -self.size_y/2, self.size_z))
            v8 = v8 if self.right_wall else bm.verts.new((self.size_x/2, -self.size_y/2, self.size_z))
            bm.faces.new([v5, v6, v8, v7])  # Ceiling

        bm.to_mesh(mesh)
        bm.free()

        # Set shading to Shade Smooth
        bpy.ops.object.shade_smooth()

        # Add Bevel modifier
        bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = self.bevel_width
        bevel_mod.segments = self.bevel_segments
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = 1.3962634  # 80 degrees in radians

        # Apply Material
        if self.material == 'WHITE':
            mat = bpy.data.materials.new(name="White Material")
            mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)
            obj.data.materials.append(mat)
        elif self.material == 'CUSTOM' and self.texture_path:
            if not os.path.exists(self.texture_path):
                self.report({'ERROR'}, "Texture file not found: " + self.texture_path)
                return {'CANCELLED'}
            try:
                mat = bpy.data.materials.new(name="Custom Material")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
                tex_image.image = bpy.data.images.load(self.texture_path)
                mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
                obj.data.materials.append(mat)
            except Exception as e:
                self.report({'ERROR'}, "Failed to load texture: " + str(e))
                return {'CANCELLED'}

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(MESH_OT_cyc_wall.bl_idname, icon_value=icons["custom_icon"].icon_id)

def register():
    global icons
    icons = bpy.utils.previews.new()
    
    script_path = os.path.dirname(os.path.realpath(__file__))
    icon_path = os.path.join(script_path, "cyc_wall_icon.png")  
    
    # This will print the path to the console.
    print("Loading icon from:", icon_path)
    
    icons.load("custom_icon", icon_path, 'IMAGE')
    
    bpy.utils.register_class(MESH_OT_cyc_wall)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    global icons
    bpy.utils.previews.remove(icons)
    icons = None

    bpy.utils.unregister_class(MESH_OT_cyc_wall)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
