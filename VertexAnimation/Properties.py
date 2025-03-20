# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy

from bpy.props import PointerProperty, BoolProperty, FloatProperty, EnumProperty, StringProperty, IntProperty, CollectionProperty, FloatVectorProperty
from bpy.types import PropertyGroup

#############################################################################################
###################################### PROPERTY GROUPS ######################################
#############################################################################################
class VATBAKER_PG_SettingsPropertyGroup(PropertyGroup):
    """ """

    bake_modes = [
        ("ANIMATION", "Animation", "Bake vertex animation data based on the selected objects vertices movement inherited from armatures, shapekeys, transforms or any other animation methods. Vertex count AND order must be maintained during the animation"),
        ("MESHSEQUENCE", "Mesh Sequence", "Bake vertex animation data based on the selected mesh sequence. Frame order must be deducible from the objects names (.000, .001 etc). Vertex count AND order must be maintained during the animation")
    ]
    bake_mode: EnumProperty(name="Mode", items=bake_modes, default=0, description="Select how the vertex animation data is baked")

    # preset
    preset_name: StringProperty(name="Name", default="", description="")
    preset_override: BoolProperty(name="Override", default=True, description="")

    # scene
    scale: FloatProperty(name="Scale", min=0.001, default=100.0, description="Scaling factor. Defaults to 100 to go from 1 Blender unit (meter) to 1 UE unit (centimeter)")
    invert_x: BoolProperty(name="Invert X", default=False, description="Invert world X axis (must be False for UE)")
    invert_y: BoolProperty(name="Invert Y", default=True, description="Invert world Y axis (must be True for UE)")
    invert_z: BoolProperty(name="Invert Z", default=False, description="Invert world Z axis (must be False for UE)")

    # uv
    uvmap_name: StringProperty(name="UVMap Name", default="UVMap.BakedData.VAT", description="UVMap to get or create for setting up the mesh UVs")
    invert_v: BoolProperty(name="Invert V", default=True, description="Invert UVMap's V axis & flip VAT texture(s) upside down (typically True for exporting to UE or DirectX apps in general, False for Unity or OpenGL apps in general)")

    # mesh
    mesh_name: StringProperty(name="Name", default="BakedMesh.VAT", description="Baked object's name")
    mesh_target_prop: StringProperty(name="Property", default="BakeTarget", description="Name of the custom property an object may uses to utilize the retargeting feature (aka, bake a hires animated mesh to a lowres mesh)")
    export_mesh: BoolProperty(name="Export", default=True, description="True to export the mesh to FBX upon bake completion")
    export_mesh_file_name: StringProperty(name="Name", default="SM_<ObjectName>", description="FBX file name, without extension")
    export_mesh_file_path: StringProperty(name="Path", default="//", description="FBX file path, not including file name", subtype='FILE_PATH')
    export_mesh_file_override: BoolProperty(name="Override", default=True, description="True to override any existing .fbx file")
    require_triangulation: BoolProperty(name="Require Triangulation", default=False, description="True to create a constraint on mesh triangulation which *may* lead to better remapping stability")
    previz_result: BoolProperty(name="Previz", default=True, description="True to add a geometry node modifier to the baked mesh and be able to previz the baked offsets and normals after bake completion")

    # xml
    export_xml: BoolProperty(name="Export", default=True, description="True to export an XML file containing informations relative to the bake (recommended)")
    export_xml_modes = [
        ("MESHPATH", "Mesh Path", "Use the same fbx file name & path. Defaults to 'Custom' if mesh is *not* exported"),
        ("CUSTOMPATH", "Custom Path", "Specify a custom xml file name & path")
    ]
    export_xml_mode: EnumProperty(name="Mode", items=export_xml_modes, default=0, description="Select how the xml file name & path is computed")
    export_xml_file_name: StringProperty(name="Name", default="SM_<ObjectName>", description="XML file name, without extension")
    export_xml_file_path: StringProperty(name="Path", default="//", description="XML file path, not including file name", subtype='FILE_PATH')
    export_xml_override: BoolProperty(name="Override", default=True, description="True to override any existing .xml file")

    # frames
    frame_range_modes = [
            ("NLA", "NLA", "Derive frame range from the anims in the NLA track. This only works if the mesh to bake has an NLA track OR if it's parented to an armature that has one. Deriving frame range from NLA will also apply the frame step setting per animation, ensure that the first frame is always included"),
            ("SCENE", "Scene", "Use the scene's frame range. Start & End are inclusives"),
            ("CUSTOM", "Custom", "Use a custom frame range. Start & End are inclusives"),
        ]
    frame_range_mode: EnumProperty(name="Mode", items=frame_range_modes, default=0, description="Select how the frame range is derived")
    frame_range_custom_start: IntProperty(name="Start", min=1, default=1, description="Inclusive")
    frame_range_custom_end: IntProperty(name="End", min=2, default=25, description="Inclusive")
    frame_range_custom_step: IntProperty(name="Step", min=1, default=1, description="How many frames to skip 'each frame'. When using 'NLA' mode, this isn't a global skip but a per anim skip, as to ensure that the first frame of each animation clip is included. This however may create issues when baking multiple objects that do not share the same NLA strips")
    frame_padding_modes = [
        ('PREFIX', 'Prefix', 'Add last frame before first frame'),
        ('SUFFIX', 'Suffix', 'Add first frame after last frame'),
        ('PREFIX_SUFFIX', 'Prefix & Suffix', 'Add both last frame before first frame AND first frame after last frame (in doubt, use this)')
    ]
    frame_padding_mode: EnumProperty(name="Mode", items=frame_padding_modes, default=1, description="Select how the padding is applied")
    frame_padding: IntProperty(name="Padding", min=0, default=0, description="In case baked animations can be simply played back by scrolling the UVs in the V axis (aka when you're able to bake one entire frame in one single line of pixels), pixel interpolation can be leveraged to get frame interpolation for free. However that can be troublesome in case of baking multiple animations and using a state machine of some kind to play a single animation on repeat: last frame will blend with the start frame of the next animation. A potential fix is to add padding and insert each animation's end frame before the start frame and vice versa. One frame of padding is usually enough. This WILL bring issues in case of baking multiple objects at the same time and if their NLA tracks differ.")

    # textures
    offset_tex: BoolProperty(name="Offset", default=True, description="True to bake the vertex offset texture")
    offset_tex_remap: BoolProperty(name="Remap", default=False, description="Remap offsets in a [0:1] range? This requires the use of a multiplier value and a constant-bias to remap offsets to their initial range in your shader/game engine. This is NOT recommended unless you want to experiment with storing offsets in 8bits RGBA textures which will most certainly lead to a LOT of precision loss and visible deformation, which might not be too big of an issue for very-distant props? Use at your own risk.")
    offset_tex_file_name: StringProperty(name="Filename", default="T_<ObjectName>_Offset", description="Vertex Offset image file name, without extension")
    normal_tex: BoolProperty(name="Normal", default=True, description="True to bake the vertex normal texture")
    normal_tex_remap: BoolProperty(name="Remap", default=True, description="Remap normals in a [0:1] range?")
    normal_tex_file_name: StringProperty(name="Filename", default="T_<ObjectName>_Normal", description="Vertex Normal image file name, without extension")
    export_tex: BoolProperty(name="Export", default=True, description="True to export textures to EXR upon bake completion")
    export_tex_file_path: StringProperty(name="Filepath", default="//", description="Image file path, not including file name", subtype='FILE_PATH')
    export_tex_override: BoolProperty(name="Override", default=True, description="Overrides any existing image file")
    export_tex_max_width: IntProperty(name="Max Width", min=2, max=8192, default=4096, description="Maximum allowed image width. Total image size must at least equal num_vertices*num_frames to bake. tex_width may have an effect on how the animation is stored in the images depending on the selected maximum width vs amount of vertices to bake and the use of 'Power of Two' setting.")
    export_tex_max_height: IntProperty(name="Max Height", min=2, max=8192, default=4096, description="Maximum allowed image height. Total image size must at least equal num_vertices*num_frames to bake.")

    tex_force_power_of_two: BoolProperty(name="Power of Two", default=False, description="Forces images to be of power of two. Image width and height may still differ, see 'Square' option if that's an issue. This isn't recommended as non-power-of-two textures ensure tight data packing, are supported by most game engines nowadays and aren't supposed be mipmapped anyway. In case there are more vertices to bake each frame than the maximum allowed image width, vertex data will have to 'overflow' and be stored on multiple lines.")
    tex_force_power_of_two_square: BoolProperty(name="Square", default=False, description="Forces images width and height to be equal in case 'Power of Two' is enabled. I don't see any reason why you would want to this but it is an option. You can choose how the extra texture space is handled with the 'Fill' option.")
    tex_packing_modes = [
        ('CONTINUOUS', 'Continuous', "Next frame data will start right away on the remaining pixels, ensuring tight data packing but requiring a more complex algorithm to play back the animation (frame data will end up starting at arbitrary locations on the texture and may be stored on multiple lines"),
        ('SKIP', 'Skip', 'Remaining pixels will be skipped and the next frame will simply start on the line above, simplifying the algorithm to play back the animation (add an X texels offset along the V axis to read next frame) but resulting in less tightly packed data and thus reducing the theoritical amount of vertex data that can be stored in the texture.'),
    ]
    tex_packing_mode: EnumProperty(name="Stack Mode", items=tex_packing_modes, default=1, description="Controls how frames are 'stacked' in the texture in case of underflow or overflow. \n\nFirst case is if 'Power of Two' is enabled while the amount of vertices to bake for each frame IS LESS than the maximum allowed image width AND non-power-of-two: image will be 'stretched' in width, resulting in 'underflow' and leaving gaps at the end of the line. \n\nSecond case is if the amount of vertices to bake for each frame IS GREATER than the maximum allowed image width, resulting in 'overflow'. Vertex data for one single frame will have to be stored on multiple lines, possibly leaving gaps at the end of the last line. \n\nIn both cases, we must decide what to do with the remaining pixels")
    # Underflow - CONTINUOUS
    # f5 f5 f5 00
    # f3 f4 f4 f4
    # f2 f2 f3 f3
    # f1 f1 f1 f2
    # Underflow - SKIP
    # f4 f4 f4 00
    # f3 f3 f3 00
    # f2 f2 f2 00
    # f1 f1 f1 00
    # Overflow - CONTINUOUS
    # f3 f3 f3 00
    # f2 f2 f3 f3
    # f1 f2 f2 f2
    # f1 f1 f1 f1
    # Overflow - SKIP
    # f2 00 00 00
    # f2 f2 f2 f2
    # f1 00 00 00
    # f1 f1 f1 f1

class VATBAKER_PG_ReportAnimObjPropertyGroup(PropertyGroup):
    """ """
    obj: PointerProperty(type=bpy.types.Object)
    target_obj: PointerProperty(type=bpy.types.Object)

class VATBAKER_PG_ReportAnimPropertyGroup(PropertyGroup):
    """ """
    objs: CollectionProperty(type=VATBAKER_PG_ReportAnimObjPropertyGroup)
    selected_obj: IntProperty(name="Selected Obj", default=0, description="")
    name: StringProperty(name="Name", default="", description="")
    start_frame: IntProperty(name="Start", default=0, description="")
    start_time: FloatProperty(name="Start", default=0.0)
    end_frame: IntProperty(name="End", default=0, description="")
    end_time: FloatProperty(name="End", default=0.0)

class VATBAKER_PG_ReportPropertyGroup(PropertyGroup):
    """ """
    baked: BoolProperty(name="Baked", default=False, description="")
    success: BoolProperty(name="Success", default=False, description="")
    msg: StringProperty(name="Message", default="", description="")
    name: StringProperty(name="Name", default="//", description="")
    ID: StringProperty(name="ID", default="", description="")

    unit_system: StringProperty(name="System", default="", description="")
    unit_unit: StringProperty(name="Unit", default="", description="")
    unit_length: FloatProperty(name="Length", default=0.0, description="")
    unit_scale: FloatProperty(name="Scale", default=0.0, description="")
    unit_invert_x: BoolProperty(name="Invert X", default=False, description="")
    unit_invert_y: BoolProperty(name="Invert Y", default=False, description="")
    unit_invert_z: BoolProperty(name="Invert Z", default=False, description="")

    padded: BoolProperty(name="Padded", default=False, description="")
    padding: IntProperty(name="Padding", default=0, description="")
    padding_modes = [
        ('PREFIX', 'Prefix', 'Last frame was added before first frame'),
        ('SUFFIX', 'Suffix', 'First frame was added after last frame'),
        ('PREFIX_SUFFIX', 'Prefix & Suffix', 'Last frame was added before first frame AND first frame was added after last frame')
    ]
    padding_mode: EnumProperty(name="Sampling", items=padding_modes, default=0, description="")
    anims: CollectionProperty(type=VATBAKER_PG_ReportAnimPropertyGroup)
    selected_anim: IntProperty(name="Selected Anim", default=0, description="")

    start_frame: IntProperty(name="Start", default=0, description="")
    end_frame: IntProperty(name="End", default=0, description="")
    num_frames: IntProperty(name="Count", default=0, description="")
    num_frames_padded: IntProperty(name="Padded", default=0, description="")
    frame_step: IntProperty(name="Frame Step", default=0, description="")
    frame_width: FloatProperty(name="Frame Width", default=0.0, description="")
    frame_height: FloatProperty(name="Frame Height", default=0.0, description="")
    frame_rate: FloatProperty(name="FPS", default=24.0, description="")

    num_verts: IntProperty(name="Vertices", default=0, description="")

    mesh: PointerProperty(type=bpy.types.Object)
    mesh_export: BoolProperty(name="Export", default=False, description="")
    mesh_path: StringProperty(name="Filepath", default="//", description="", subtype='FILE_PATH')
    mesh_uvmap_index: IntProperty(name="UV Index", default=0, description="")
    mesh_uvmap_invert_v: BoolProperty(name="Invert V", default=False, description="")
    mesh_min_bounds_offset: FloatVectorProperty(name="Min Bounds Offset")
    mesh_max_bounds_offset: FloatVectorProperty(name="Max Bounds Offset")

    tex_width: IntProperty(name="Width", default=0, description="")
    tex_height: IntProperty(name="Height", default=0, description="")
    tex_underflow: BoolProperty(name="Underflow", default=False, description="")
    tex_overflow: BoolProperty(name="Overflow", default=False, description="")
    tex_offset: PointerProperty(type=bpy.types.Image)
    tex_offset_export: BoolProperty(name="Offset", default=False, description="")
    tex_offset_path: StringProperty(name="Path", default="//", description="", subtype='FILE_PATH')
    tex_offset_remapped: BoolProperty(name="Remapped", default=False, description="")
    tex_offset_remapping: FloatVectorProperty(name="Remapping")
    tex_normal: PointerProperty(type=bpy.types.Image)
    tex_normal_export: BoolProperty(name="Normal", default=False, description="")
    tex_normal_path: StringProperty(name="Filepath", default="//", description="", subtype='FILE_PATH')
    tex_normal_remapped: BoolProperty(name="Remapped", default=False, description="")
    tex_sampling_modes = [
        ('STACK_SINGLE', 'Stack - Single', "VAT texture(s) can be sampled using the most simple 'stack' method. Each frame is stacked on top of another in the vertical axis, allowing a simple 'V' offset method to play back the animation. Pixel interpolation may thus be used to get frame interpolation for free but beware: padding may be required in case of baking multiple animations and needing to loop a specific anim. This comes with extra constraints for the baking process: see the 'Padding' tooltip"),
        ('STACK_MULT', 'Stack - Multiples', "VAT texture(s) can be sampled using the most simple 'stack' method. Each frame is stored in more than one line of pixels but each frame is still stacked on top of another in the vertical axis, allowing a simple 'V' offset method to play back the animation. Pixel interpolation cannot be used to get frame interpolation and padding is therefore unecessary. The 'Frame Height' value becomes a requirement for play back"),
        ('CONTINUOUS', 'Continuous', "VAT texture(s) have to be sampled using the most complex 'continuous' method. Each frame is stored in fewer or more than one line of pixels and the next frame is immediatly following after, preveting a simple 'V' offset method to play back the animation. Pixel interpolation cannot be used to get frame interpolation and padding is therefore unecessary. The 'Frame Height' and 'Frame Width' values become a requirement for play back")
    ]
    tex_sampling_mode: EnumProperty(name="Sampling", items=tex_sampling_modes, default=0, description="Defines how VAT texture(s) are meant to be sampled in your shader/game engine. Please read the tooltips carefully")

    xml: BoolProperty(name="XML", default=False, description="")
    xml_path: StringProperty(name="Filepath", default="//", description="", subtype='FILE_PATH')

def register():
    bpy.types.Scene.VATBakerSettings = PointerProperty(type=VATBAKER_PG_SettingsPropertyGroup)
    bpy.types.Scene.VATBakerReport = PointerProperty(type=VATBAKER_PG_ReportPropertyGroup)

def unregister():
    del bpy.types.Scene.VATBakerSettings
    del bpy.types.Scene.VATBakerReport
