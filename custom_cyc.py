bl_info = {
    "name": "Cyclorama",
    "author":"Vaibhav",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Cyclorama",
    "description": "Adds a customizable Cyclorama Wall mesh with options for which walls are created, their sizes, and adds a bevel modifier for easy curve control.",
    "category": "Add Mesh",
}

import bpy
import os
from bpy.types import Operator
from bpy_extras.object_utils import AddObjectHelper
from bpy.props import FloatProperty, BoolProperty
import bpy.utils.previews

# Global variable to store icons
icons = None

import bmesh

class MESH_OT_cyc_wall(bpy.types.Operator):
    bl_idname = "mesh.cyc_wall"
    bl_label = "Cyclorama by Vaibhav"
    bl_description = "Creates a customizable cyclorama"
    bl_options = {'REGISTER', 'UNDO'}

    size_x: bpy.props.FloatProperty(
        name="Width",
        description="Size along the X axis",
        default=10.0,
    )

    size_y: bpy.props.FloatProperty(
        name="Depth",
        description="Size along the Y axis",
        default=8.0,
    )

    size_z: bpy.props.FloatProperty(
        name="Height",
        description="Height of the Wall along the Z axis",
        default=5.0,
    )

    left_wall: bpy.props.BoolProperty(
        name="Left Wall",
        description="Include the left wall",
        default=False,
    )

    right_wall: bpy.props.BoolProperty(
        name="Right Wall",
        description="Include the right wall",
        default=False,
    )

    ceiling: bpy.props.BoolProperty(
        name="Ceiling",
        description="Include the ceiling",
        default=False,
    )

    def execute(self, context):
        # Create a new mesh
        mesh = bpy.data.meshes.new(name="Cyc Wall")
        obj = bpy.data.objects.new("Cyc Wall", mesh)

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
            bm.faces.new([v5, v6, v8, v7])  # ceiling

        bm.to_mesh(mesh)
        bm.free()

        # Set shading to Shade Smooth
        bpy.ops.object.shade_smooth()

        # Add Bevel modifier
        bevel_mod = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel_mod.width = 2.0
        bevel_mod.segments = 24
        bevel_mod.limit_method = 'ANGLE'
        bevel_mod.angle_limit = 1.3962634  # 80 degrees in radians

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