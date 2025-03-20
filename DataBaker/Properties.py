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
class DATABAKER_PG_SettingsPropertyGroup(PropertyGroup):  
    """ """

    modes = [
        ("UV", "UV", "UV"),
        ("VCOL", "VCOL", "VCOL")
    ]

    axis_xyz = [
        ("X", "X", "X"),
        ("Y", "Y", "Y"),
        ("Z", "Z", "Z")
    ]

    uv = [
        ("U", "U", "U"),
        ("V", "V", "V")
    ]

    rgba = [
        ("R", "R", "R"),
        ("G", "G", "G"),
        ("B", "B", "B"),
        ("A", "A", "A")
    ]

    pos_channels = [
        ("INDIVIDUAL" , "Individual ", "Pick which X/Y/Z component to bake. Each component is stored in a UVMap channel (U or V)" ),
        ("AB_PACKED", "AB Packed", "Pick two components (X/Y, X/Z, Y/Z) to pack into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *moderate* precision loss still! The same mulitplier value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
        ("XYZ_PACKED", "XYZ Packed", "XYZ components are all packed into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *severe* precision loss still! The same value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)")
    ]

    axis_modes = [
        ("INDIVIDUAL" , "Individual ", "Pick which X/Y/Z component to bake. Each component is stored in a UVMap channel (U or V)" ),
        ("AB_PACKED", "AB Packed", "Pick two components (X/Y, X/Z, Y/Z) to pack into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *moderate* precision loss still! The same mulitplier value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
        ("XYZ_PACKED", "XYZ Packed", "XYZ components are all packed into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *severe* precision loss still! The same value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
        ("POSITION_PACKED", "Packed with Position", "XYZ axis components are packed into the fractional part of the position XYZ components which are thus rounded to integers which *MAY* be an issue depending on the scene scale/exported scale. If positions are stored in centimeters, then precision loss is <1cm which is normally no big deal in-engine. There's very little to no reason NOT to choose this option in case you do bake position's XYZ component *individually* because axis is packed and unpacked in the position data with pretty much no side-effect, besides rounding")
    ]

    # transform
    transform_obj: PointerProperty(type=bpy.types.Object, name="Object", description="Defaults to 'self'. Use this in the rare occasion that you want to bake the position/axis of a specific object into another object. Usually using 'self' is what you want (meaning, leave this empty)")

    # position
    position: BoolProperty(name="Position", default=False, description="Bake position? This option alone doesn't necessarily guarantee that the position is baked. Further actions are likely required depending on the selected mode")
    position_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="Select how position is baked")

    position_x: BoolProperty(name="X", default=True, description="Bake the position's X component")
    position_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    position_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    position_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    position_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")

    position_y: BoolProperty(name="Y", default=True, description="Bake the position's Y component")
    position_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    position_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    position_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    position_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="Target RGBA channel")

    position_z: BoolProperty(name="Z", default=True, description="Bake the position's Z component")
    position_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    position_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    position_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    position_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="Target RGBA channel")

    position_packed_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    position_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")

    position_pack_only_if_non_null: BoolProperty(name="Pack only if not zero", default=True, description="You likely want to pack position only *if* position is *not* (0,0,0) and write a 0 value if it is. Else the (0,0,0) vector might be scrambled a bit during bit packing and you could have issue checking against zero to test if a position is valid once unpacked in your shader/game engine. Not that may lead to a false positive if the position to pack actually happens to be close to enough to (0,0,0)")

    position_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="First position component to encode")
    position_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Second position component to encode")

    # axis
    axis: BoolProperty(name="Axis", default=False, description="Bake axis? This option alone doesn't necessarily guarantee that the axis is baked. Further actions are likely required depending on the selected mode")
    axis_component: EnumProperty(name="Axis", items=axis_xyz, default=1, description="Axis to bake. There's no right or wrong choice here, it depends on what you want to do with that axis data in your shader/game engine and the difference in coordinates system in Blender and your game engine. Recommended workflow is to make all objects point towards positive Z by default in Blender and bake the Z axis to bake the objects 'forward vector'")
    axis_channel_mode: EnumProperty(name="Mode", items=axis_modes, default=0, description="Select how the axis is baked")
    
    axis_x: BoolProperty(name="X Component", default=True, description="Bake the axis's X component")
    axis_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    axis_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    axis_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    axis_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    
    axis_y: BoolProperty(name="Y Component", default=True, description="Bake the position's Y component")
    axis_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    axis_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    axis_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    axis_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="Target RGBA channel")
    
    axis_z: BoolProperty(name="Z Component", default=True, description="Bake the position's Z component")
    axis_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    axis_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    axis_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    axis_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="Target RGBA channel")
    
    axis_packed_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    axis_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    
    axis_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="First axis component to encode")
    axis_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Second axis component to encode")
    
    # shapekey
    shapekey_name: StringProperty(name="Shapekey", default="Key 1", description="Shapekey to bake (name)")
    shapekey_rest_name: StringProperty(name="Rest Shapekey", default="Basis", description="Rest shapekey (name)")
    
    # shapekey offset
    shapekey_offset: BoolProperty(name="Shapekey Offset", default=False, description="Bake shapekey offset? This option alone doesn't necessarily guarantee that the offset is baked. Further actions are likely required depending on the selected mode")
    shapekey_offset_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="Select how the offset is baked")

    shapekey_offset_x: BoolProperty(name="X", default=True, description="Bake the shapekey's offset X component")
    shapekey_offset_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    shapekey_offset_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    shapekey_offset_x_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    shapekey_offset_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")

    shapekey_offset_y: BoolProperty(name="Y", default=True, description="Bake the shapekey's offset Y component")
    shapekey_offset_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    shapekey_offset_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=3, description="Target UVMap index")
    shapekey_offset_y_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    shapekey_offset_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="Target RGBA channel")

    shapekey_offset_z: BoolProperty(name="Z", default=True, description="Bake the shapekey's offset Z component")
    shapekey_offset_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    shapekey_offset_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=3, description="Target UVMap index")
    shapekey_offset_z_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    shapekey_offset_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="Target RGBA channel")

    shapekey_offset_packed_uv_index: IntProperty(name="UV Map", min=0, max=7, default=3, description="Target UVMap index")
    shapekey_offset_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")

    shapekey_offset_pack_only_if_non_null: BoolProperty(name="Pack only if not zero", default=True, description="You likely want to pack position only *if* position is *not* (0,0,0) and write a 0 value if it is. Else the (0,0,0) vector might be scrambled a bit during bit packing and you could have issue checking against zero to test if a position is valid once unpacked in your shader/game engine. Not that may lead to a false positive if the position to pack actually happens to be close to enough to (0,0,0)")
    
    shapekey_offset_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="First offset component to encode")
    shapekey_offset_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Second offset component to encode")

    # shapekey normal
    shapekey_normal: BoolProperty(name="Shapekey Normal", default=False, description="Bake shapekey normal? This option alone doesn't necessarily guarantee that the normal is baked. Further actions are likely required depending on the selected mode")
    shapekey_normal_channels = [
        ("INDIVIDUAL" , "Individual ", "Pick which X/Y/Z component to bake. Each component is stored in a UVMap channel (U or V)" ),
        ("AB_PACKED", "AB Packed", "Pick two components (X/Y, X/Z, Y/Z) to pack into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *moderate* precision loss still! The same mulitplier value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
        ("XYZ_PACKED", "XYZ Packed", "XYZ components are all packed into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *severe* precision loss still! The same value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
        ("OFFSET_PACKED", "Packed with Offset", "XYZ axis components are packed into the fractional part of the position XYZ components which are thus rounded to integers which *MAY* be an issue depending on the scene scale/exported scale. If positions are stored in centimeters, then precision loss is <1cm which is normally no big deal in-engine. There's very little to no reason NOT to choose this option in case you do bake position's XYZ component *individually* because axis is packed and unpacked in the position data with pretty much no side-effect, besides rounding")
    ]
    shapekey_normal_channel_mode: EnumProperty(name="Mode", items=shapekey_normal_channels, default=0, description="Select how the normal is baked")

    shapekey_normal_x: BoolProperty(name="X", default=True, description="Bake the shapekey's offset X component")
    shapekey_normal_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    shapekey_normal_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    shapekey_normal_x_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    shapekey_normal_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    
    shapekey_normal_y: BoolProperty(name="Y", default=True, description="Bake the shapekey's offset Y component")
    shapekey_normal_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    shapekey_normal_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    shapekey_normal_y_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    shapekey_normal_y_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    
    shapekey_normal_z: BoolProperty(name="Z", default=True, description="Bake the shapekey's offset Z component")
    shapekey_normal_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    shapekey_normal_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=3, description="Target UVMap index")
    shapekey_normal_z_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    shapekey_normal_z_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")

    shapekey_normal_xyz_uv_index: IntProperty(name="UV Map", min=0, max=7, default=3, description="Target UVMap index")
    shapekey_normal_xyz_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    
    shapekey_normal_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="First normal component to encode")
    shapekey_normal_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Second normal component to encode")

    # sphere mask
    sphere_mask: BoolProperty(name="Sphere Mask", default=False, description="Bake a spherical 3D gradient?")
    sphere_mask_normalize: BoolProperty(name="Normalize", default=True, description="False to store the spherical distance as-is (only available when stored in UVs). True to remap the distance in a [0:1] range based on the max distance")
    sphere_mask_clamp: BoolProperty(name="Clamp", default=False, description="Don't allow values to go beyond the [0:1] range")
    sphere_mask_origin_modes = [
        ("ORIGIN" , "Origin", "Spherical gradient is computed from the world origin, or the specified 'Origin' object" ),
        ("SELF" , "Self", "Spherical gradient is computed from each object's own origin" ),
        ("OBJECT" , "Object ", "Spherical gradient is computed from a specified object's origin" ),
        ("SELECTION" , "Selection Center", "Spherical is computed from the selected object's center point" ),
        ("PARENT" , "Parent Object", "Spherical gradient is computed from each object's parent origin, if any, else from each object's own origin" )
    ]
    sphere_mask_origin_mode: EnumProperty(name="Origin", items=sphere_mask_origin_modes, default=1, description="Select the spherical mask origin")
    sphere_mask_origin: PointerProperty(type=bpy.types.Object, name="Object", description="Optional object used to compute the sphere mask origin/center")
    sphere_mask_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the spherical gradient is baked")

    sphere_mask_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    sphere_mask_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    sphere_mask_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    sphere_mask_falloff: FloatProperty(name="Falloff", min=0.0, default=1.0, description="Power curve. 1 - linear falloff, 2 - cubic falloff...")

    # linear mask
    linear_mask: BoolProperty(name="Linear Mask", default=False, description="Bake a linear 2D gradient along a given axis?")
    linear_mask_normalize: BoolProperty(name="Normalize", default=True, description="False to store the linear distance as-is (only available when stored in UVs). True to remap the distance in a [0:1] range based on the max distance")
    linear_mask_clamp: BoolProperty(name="Clamp", default=False, description="Don't allow values to go beyond the [0:1] range which might happen with normalization because of user-set bounds. You might want allow that though, it's up to you")
    linear_mask_obj_modes = [
        ("SELECTION" , "Selection bounds", "Linear gradient is computed based on the overall bounds of your selection in world space along the specified axis in world space"),
        ("SELF_LOCAL" , "Self in Local Space", "Linear gradient is computed along each objects specified axis in local space"),
        ("SELF_WORLD" , "Self in World Space", "Linear gradient is computed for object along the specified axis in world space"),
        ("OBJECT" , "Object", "Linear gradient is computed based on a given object's bounds in world space"),
        ("PARENT_LOCAL" , "Parent Object in Local Space", "Linear gradient is computed based on each object's parent along the specified parent's axis in local space"),
        ("PARENT_WORLD" , "Parent Object in World Space", "Linear gradient is computed based on each object's parent along the specified axis in world space")
    ]
    linear_mask_obj_mode: EnumProperty(name="Mode", items=linear_mask_obj_modes, default=1)
    linear_mask_obj: PointerProperty(type=bpy.types.Object, name="Object", description="Optional mesh object that can be used to specify custom bounds for computing the linear mask. Defaults to self if none is specified")
    linear_mask_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the linear gradient is baked")
    linear_mask_axis: EnumProperty(name="Axis", items=axis_xyz, default=2, description="Select which axis to use to bake the 2D gradient")

    linear_mask_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    linear_mask_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    linear_mask_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    linear_mask_falloff: FloatProperty(name="Falloff", min=0.0, default=1.0, description="Power curve, only available IF normalized. Clamping is suggested to ensure values don't skyrocket with high falloff exponents & custom bounds. 1 - linear falloff, 2 - cubic falloff...")
    
    # random per collection
    random_per_collection: BoolProperty(name="Random Per Collection", default=False, description="Bake a random value per collection?")
    random_per_collection_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the random value is baked")
    
    random_per_collection_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    random_per_collection_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    random_per_collection_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    random_per_collection_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="False for total randomness. True to ensure the whole [0:1] range is evenly used & distributed amongst selection (11 collections > random values: 0.0, 0.1, 0.2, ..., 1.0)")
    
    # random per object
    random_per_object: BoolProperty(name="Random Per Object", default=False, description="Bake a random value per selected object?")
    random_per_object_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the random value is baked")
    
    random_per_object_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    random_per_object_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    random_per_object_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    random_per_object_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="False for total randomness. True to ensure the whole [0:1] range is evenly used & distributed amongst selection (11 objects > random values: 0.0, 0.1, 0.2, ..., 1.0)")
    
    # random per poly
    random_per_poly: BoolProperty(name="Random Per Poly", default=False, description="Bake a random value per polygon?")
    random_per_poly_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the random value is baked")
    
    random_per_poly_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    random_per_poly_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    random_per_poly_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    random_per_poly_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="False for total randomness. True to ensure the whole [0:1] range is evenly used & distributed amongst selection (101 polygons > random values: 0.00, 0.01, 0.02, ..., 1.0). This DUPLICATES ALL VERTICES!")

    # parent
    parent_modes = [
        ("AUTOMATIC" , "Automatic", "Traverses the entire parent tree (up to a specified depth) and generates all uvmaps required, starting from the specified UVMap index & channel. Please take note on how many uvmaps are created in the info panel" ),
        ("MANUAL", "Manual", "Requires several successive bakes. For instance, set the max depth to 3 and current depth to 1, configure the data to bake (UV index etc), make sure to enable the duplicate option but *disable* the merge option and press bake. Set the current depth to 2, *disable* the duplicate option, update the data to bake (UV index etc) and bake again. Set the current to depth to 3, update the data to bake one last time, *enable* the merge option and bake.")
    ]
    parent_mode: EnumProperty(name="Mode", items=parent_modes, default=0, description="Select the parent baking global mode. Automatic mode is likely preferred. Beware, hierarchy baking requires many uvmaps and baking more than one parent isn't practical. Be sure to take a look at the info panel to ensure things to do go out of hand")

    parent_depth: IntProperty(name="Current", default=1, min=1, description="Hierarchy depth to bake. Mustn't be greater than Depth. See the parent mode tooltip for more info")
    parent_max_depth: IntProperty(name="Depth", default=2, min=1, max=7, description="Hierarchy depth to bake. Needs to be carefully thought of, the greater the depth, the greater the amount of data, and thus uvmaps (8 max), required. Baking a single parent is recommended. This is only the parent's data and doesn't include data about 'self'. Let's take the following hierarchy: Trunk>Branch>Smaller Branches>Leaves. First, the 'Trunk' doesn't need to be included assuming its pivot is the object's origin, thus the hierarchy only needs to be Branch>Smaller Branches>Leaves. You can then find out if vertices belong to the 'Trunk' by checking if the baked parent data is (0,0). Second, the 'Smaller Branches' need to have *one* parent and 'Leaves' have *two* in order to respect the hierarchy depth. You can however cheat and 'parent' a leaf directly to a 'Branch' by parenting the leaf to an empty located at its own position, essentially shifting its hierarchy depth by one. Again, baking more than one single parent isn't recommended, Pivot Painter is likely a better option")

    parent_automatic_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index. Caution, this will serve as the 'first' index to use and the automatic process may need to generate more uvmaps.")
    parent_automatic_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel. Caution, this will serve as the 'first' channel to use, aka the starting point, and the automatic process may need to generate more uvmaps.")

    # parent position
    parent_position: BoolProperty(name="Position", default=False, description="Bake parent position? This option alone doesn't necessarily guarantee that the position is baked. Further actions are likely required depending on the selected mode")
    parent_position_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="Select how the parent position is baked")

    parent_position_x: BoolProperty(name="X", description="Bake the parent position's X component")
    parent_position_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    parent_position_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    parent_position_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    parent_position_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")

    parent_position_y: BoolProperty(name="Y", description="Bake the parent position's Y component")
    parent_position_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    parent_position_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    parent_position_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    parent_position_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="Target RGBA channel")

    parent_position_z: BoolProperty(name="Z", description="Bake the parent position's Z component")
    parent_position_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    parent_position_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    parent_position_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    parent_position_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="Target RGBA channel")

    parent_position_packed_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    parent_position_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")

    parent_position_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="Parent position first component to encode")
    parent_position_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Parent position second component to encode")
    
    # parent axis
    parent_axis: BoolProperty(name="Axis", default=False, description="Bake parent axis? This option alone doesn't necessarily guarantee that the axis is baked. Further actions are likely required depending on the selected mode")
    parent_axis_component: EnumProperty(name="Axis", items=axis_xyz, default=1, description="Select which axis to bake.  will depend on what you want to do with that axis data in engine and how your objects are oriented in Blender so there is no right or wrong choice here. I'd recommended making your objects all point upwards by default and use the Z axis so the baked axis is each object's 'forward vector', but again it depends on what you're trying to do")
    
    parent_axis_channel_mode: EnumProperty(name="Mode", items=axis_modes, default=0, description="Select how the parent axis is baked")

    parent_axis_x: BoolProperty(name="X Component", description="Bake the parent axis X component")
    parent_axis_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the X component baked?")
    parent_axis_x_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    parent_axis_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    parent_axis_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel")
    
    parent_axis_y: BoolProperty(name="Y Component", description="Bake the parent axis Y component")
    parent_axis_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Y component baked?")
    parent_axis_y_uv_index: IntProperty(name="UV Map", min=0, max=7, default=1, description="Target UVMap index")
    parent_axis_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="Target UVMap channel")
    parent_axis_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="Target RGBA channel")
    
    parent_axis_z: BoolProperty(name="Z Component", description="Bake the parent axis Z component")
    parent_axis_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="How is the Z component baked?")
    parent_axis_z_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    parent_axis_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    parent_axis_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="Target RGBA channel. Caution, only one hierarchy parent may be used ")
    
    parent_axis_packed_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    parent_axis_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    
    parent_axis_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="Parent axis first component to encode")
    parent_axis_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="Parent axis second component to encode")

    # fixed value
    fixed_value: BoolProperty(name="Fixed Value", default=False, description="Bake a given value?")
    fixed_value_data: FloatProperty(name="Value", default=0.0, description="Float value to bake")
    fixed_value_mode: EnumProperty(name="Mode", items=modes, default=0, description="Select how the value is baked")
    
    fixed_value_uv_index: IntProperty(name="UV Map", min=0, max=7, default=2, description="Target UVMap index")
    fixed_value_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="Target UVMap channel")
    fixed_value_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="Target RGBA channel. Caution, value has to be in a [0:1] range when using Vertex Color!")

    # direction
    direction: BoolProperty(name="Direction", default=False, description="Bake a given vector?")
    direction_modes = [
        ("3DRAND" , "Random 3D", "Generates a random 3D unit vector in [-1:1] range" ),
        ("2DRAND" , "Random 2D", "Generates a random 2D unit vector in [-1:1] range. Z will be 0" ),
        ("3DVECTOR" , "3D Vector", "User-set 3D direction" ),
        ("2DVECTOR", "2D Vector", "User-set 2D direction"),
    ]
    direction_mode: EnumProperty(name="Vector", items=direction_modes, default=0, description="Select how the direction is generated")
    direction_vector_x: FloatProperty(name="X", default=0.0, description="3D Vector to set. Vector will be normalized.")
    direction_vector_y: FloatProperty(name="Y", default=0.0, description="3D Vector to set. Vector will be normalized.")
    direction_vector_z: FloatProperty(name="Z", default=1.0, description="3D Vector to set. Vector will be normalized.")
    
    direction_pack_modes = [
        ("NORMALS", "Normals", "Use normal to store the unit vector. Vector will be normalized and normals will be overriden." ),
        ("VCOL" , "VCol", "Use vertex color to store the unit vector. Vector will be normalized and remapped from [-1:1] to [0:1] range." )
    ]
    direction_pack_mode: EnumProperty(name="Mode", items=direction_pack_modes, default=0, description="Select how the direction is baked")

    # mesh
    duplicate_mesh: BoolProperty(name="Duplicate", default=True, description="Duplicate selected meshes for baking and ensure original object(s) aren't modified. Disable at your own risk")
    make_single_user: BoolProperty(name="Make Single-User", default=True, description="Bake might *not* proceed as expected if this option is False but the choice is yours. Linked meshes might lead to issues: UVs might be shared across objects yet bake might requires unique UVs per object. Disable at your own risk")
    merge_mesh: BoolProperty(name="Merge", default=True, description="Merge baked meshes. Safe to enable IF 'Duplicate' option is True, else use at your own risk")
    clean_bake: BoolProperty(name="Clean", default=True, description="Clean empties that were part of the bake process and duplicated (child/parent hierarchy, axis etc.). Only relevant IF 'Duplicate' option is True")
    mesh_name: StringProperty(name="Name", default="BakedMesh.DATA", description="Merged object's name")
    scale: FloatProperty(name="Scale", min=0.001, default=100.0, description="Scaling factor. Defaults to 100 to go from 1 Blender unit (meter) to 1 UE unit (centimeter)")
    invert_x: BoolProperty(name="Invert X", default=False, description="Invert world X axis (must be False for UE)")
    invert_y: BoolProperty(name="Invert Y", default=True, description="Invert world Y axis (must be True for UE)")
    invert_z: BoolProperty(name="Invert Z", default=False, description="Invert world Z axis (must be False for UE)")
    origin: PointerProperty(type=bpy.types.Object, name="Origin", description="Optional. Defaults to the world origin. This is most likely an advanced use case and you'll probably want to leave it empty if you don't know what to do with this")
    precision_offset: FloatProperty(name="Precision Offset", min=1.0, default=1.0, description="Precision offset used to fix some packing issues. Best don't change it if you don't know what you're doing, its default 1.0 value seems to work well enough")

    export_mesh: BoolProperty(name="Export", default=True, description="True to export the mesh to FBX upon bake completion")
    export_mesh_file_name: StringProperty(name="Name", default="SM_<ObjectName>", description="FBX file name, without extension")
    export_mesh_file_path: StringProperty(name="Path", default="//", description="FBX file path, not including file name", subtype='FILE_PATH')
    export_mesh_file_override: BoolProperty(name="Override", default=True, description="True to override any existing .fbx file")

    # uv
    uvmap_name: StringProperty(name="UVMap Name", default="UVMap.BakedData", description="UVMap to get or create for setting up the mesh UVs")
    invert_v: BoolProperty(name="Invert V", default=True, description="Invert UVMap's V axis & flip VAT texture(s) upside down (typically True for exporting to UE or DirectX apps in general, False for Unity or OpenGL apps in general)")

    # xml
    export_xml: BoolProperty(name="Export", default=True, description="True to export an XML file containing informations relative to the bake (recommended)")
    export_xml_modes = [
        ("MESHPATH", "Mesh Path", "Use the same mesh fbx file name & path. Defaults to 'Custom' if mesh is *not* exported"),
        ("CUSTOMPATH", "Custom Path", "Specify a custom xml file name & path")
    ]
    export_xml_mode: EnumProperty(name="Mode", items=export_xml_modes, default=0, description="Select how the xml file name & path is computed")
    export_xml_file_name: StringProperty(name="Name", default="SM_<ObjectName>", description="XML file name, without extension")
    export_xml_file_path: StringProperty(name="Path", default="//", description="XML file path, not including file name", subtype='FILE_PATH')
    export_xml_override: BoolProperty(name="Override", default=True, description="True to override any existing .xml file")

class DATABAKER_PG_ReportAnimPropertyGroup(PropertyGroup):
    """ """
    ID: StringProperty(name="ID", default="", description="")
    name: StringProperty(name="Name", default="", description="")

class DATABAKER_PG_ReportPropertyGroup(PropertyGroup):
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

    position_multiplier: FloatProperty(name="Remapping")
    parent_position_multiplier: FloatProperty(name="Remapping")
    shapekey_offset_multiplier: FloatProperty(name="Remapping")

    mesh: PointerProperty(type=bpy.types.Object)
    mesh_export: BoolProperty(name="Export", default=False, description="")
    mesh_path: StringProperty(name="Filepath", default="//", description="", subtype='FILE_PATH')
    mesh_uvmaps: CollectionProperty(type=DATABAKER_PG_ReportAnimPropertyGroup)
    select_mesh_uvmap: IntProperty(name="UVMap", default=0, description="")
    mesh_uvmap_invert_v: BoolProperty(name="Invert V", default=False, description="")
    mesh_uvmap_count: IntProperty(name="UVMaps", default=0, description="")

    meshes_count: IntProperty(name="Meshes", default=0, description="")
    empties_count: IntProperty(name="Empties", default=0, description="")


    # transform_obj: PointerProperty(type=bpy.types.Object, name="Object", description="")

    # # position
    # position: BoolProperty(name="Position", default=False, description="")
    # position_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="")

    # position_x: BoolProperty(name="X", default=True, description="")
    # position_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # position_x_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # position_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # position_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")

    # position_y: BoolProperty(name="Y", default=True, description="")
    # position_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # position_y_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # position_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # position_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="")

    # position_z: BoolProperty(name="Z", default=True, description="")
    # position_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # position_z_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # position_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # position_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="")

    # position_packed_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # position_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")

    # position_pack_only_if_non_null: BoolProperty(name="Pack only if not zero", default=True, description="")

    # position_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # position_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")

    # # axis
    # axis: BoolProperty(name="Axis", default=False, description="")
    # axis_component: EnumProperty(name="Axis", items=axis_xyz, default=1, description="")
    # axis_channel_mode: EnumProperty(name="Mode", items=axis_modes, default=0, description="")
    
    # axis_x: BoolProperty(name="X Component", default=True, description="")
    # axis_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # axis_x_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # axis_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # axis_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    
    # axis_y: BoolProperty(name="Y Component", default=True, description="")
    # axis_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # axis_y_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # axis_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # axis_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="")
    
    # axis_z: BoolProperty(name="Z Component", default=True, description="")
    # axis_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # axis_z_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # axis_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # axis_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="")
    
    # axis_packed_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # axis_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    
    # axis_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # axis_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")
    
    # # shapekey
    # shapekey_name: StringProperty(name="Shapekey", default="Key 1", description="")
    # shapekey_rest_name: StringProperty(name="Rest Shapekey", default="Basis", description="")
    
    # # shapekey offset
    # shapekey_offset: BoolProperty(name="Shapekey Offset", default=False, description="")
    # shapekey_offset_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="")

    # shapekey_offset_x: BoolProperty(name="X", default=True, description="")
    # shapekey_offset_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_offset_x_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # shapekey_offset_x_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # shapekey_offset_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")

    # shapekey_offset_y: BoolProperty(name="Y", default=True, description="")
    # shapekey_offset_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_offset_y_uv_index: IntProperty(name="UV Map", min=0, default=3, description="")
    # shapekey_offset_y_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # shapekey_offset_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="")

    # shapekey_offset_z: BoolProperty(name="Z", default=True, description="")
    # shapekey_offset_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_offset_z_uv_index: IntProperty(name="UV Map", min=0, default=3, description="")
    # shapekey_offset_z_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # shapekey_offset_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="")

    # shapekey_offset_packed_uv_index: IntProperty(name="UV Map", min=0, default=3, description="")
    # shapekey_offset_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")

    # shapekey_offset_pack_only_if_non_null: BoolProperty(name="Pack only if not zero", default=True, description="")
    
    # shapekey_offset_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # shapekey_offset_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")

    # # shapekey normal
    # shapekey_normal: BoolProperty(name="Shapekey Normal", default=False, description="")
    # shapekey_normal_channels = [
    #     ("INDIVIDUAL" , "Individual ", "Pick which X/Y/Z component to bake. Each component is stored in a UVMap channel (U or V)" ),
    #     ("AB_PACKED", "AB Packed", "Pick two components (X/Y, X/Z, Y/Z) to pack into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *moderate* precision loss still! The same mulitplier value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
    #     ("XYZ_PACKED", "XYZ Packed", "XYZ components are all packed into a single float. The addon will compute the best multiplier value to use to pack the data and minimize precision loss but expect *severe* precision loss still! The same value must be used during unpack in the shader/game engine and UVs in-engine must be 32bits (check full precision UVs in UE). Use the info panel to see what that value is, once the bake is done (or press 'Compute Multiplier' pre-bake, or check the exported XML file post-bake if one was exported)"),
    #     ("OFFSET_PACKED", "Packed with Offset", "XYZ axis components are packed into the fractional part of the position XYZ components which are thus rounded to integers which *MAY* be an issue depending on the scene scale/exported scale. If positions are stored in centimeters, then precision loss is <1cm which is normally no big deal in-engine. There's very little to no reason NOT to choose this option in case you do bake position's XYZ component *individually* because axis is packed and unpacked in the position data with pretty much no side-effect, besides rounding")
    # ]
    # shapekey_normal_channel_mode: EnumProperty(name="Mode", items=shapekey_normal_channels, default=0, description="")

    # shapekey_normal_x: BoolProperty(name="X", default=True, description="")
    # shapekey_normal_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_normal_x_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # shapekey_normal_x_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # shapekey_normal_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    
    # shapekey_normal_y: BoolProperty(name="Y", default=True, description="")
    # shapekey_normal_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_normal_y_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # shapekey_normal_y_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # shapekey_normal_y_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    
    # shapekey_normal_z: BoolProperty(name="Z", default=True, description="")
    # shapekey_normal_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # shapekey_normal_z_uv_index: IntProperty(name="UV Map", min=0, default=3, description="")
    # shapekey_normal_z_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # shapekey_normal_z_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")

    # shapekey_normal_xyz_uv_index: IntProperty(name="UV Map", min=0, default=3, description="")
    # shapekey_normal_xyz_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    
    # shapekey_normal_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # shapekey_normal_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")

    # # sphere mask
    # sphere_mask: BoolProperty(name="Sphere Mask", default=False, description="")
    # sphere_mask_normalize: BoolProperty(name="Normalize", default=True, description="")
    # sphere_mask_clamp: BoolProperty(name="Clamp", default=False, description="")
    # sphere_mask_origin_modes = [
    #     ("ORIGIN" , "Origin", "Spherical gradient is computed from the world origin, or the specified 'Origin' object" ),
    #     ("SELF" , "Self", "Spherical gradient is computed from each object's own origin" ),
    #     ("OBJECT" , "Object ", "Spherical gradient is computed from a specified object's origin" ),
    #     ("SELECTION" , "Selection Center", "Spherical is computed from the selected object's center point" ),
    #     ("PARENT" , "Parent Object", "Spherical gradient is computed from each object's parent origin, if any, else from each object's own origin" )
    # ]
    # sphere_mask_origin_mode: EnumProperty(name="Origin", items=sphere_mask_origin_modes, default=1, description="")
    # sphere_mask_origin: PointerProperty(type=bpy.types.Object, name="Object", description="")
    # sphere_mask_mode: EnumProperty(name="Mode", items=modes, default=0, description="")

    # sphere_mask_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # sphere_mask_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # sphere_mask_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    # sphere_mask_falloff: FloatProperty(name="Falloff", min=0.0, default=1.0, description="")

    # # linear mask
    # linear_mask: BoolProperty(name="Linear Mask", default=False, description="")
    # linear_mask_normalize: BoolProperty(name="Normalize", default=True, description="")
    # linear_mask_clamp: BoolProperty(name="Clamp", default=False, description="")
    # linear_mask_obj_modes = [
    #     ("SELECTION" , "Selection bounds", "Linear gradient is computed based on the overall bounds of your selection in world space along the specified axis in world space"),
    #     ("SELF_LOCAL" , "Self in Local Space", "Linear gradient is computed along each objects specified axis in local space"),
    #     ("SELF_WORLD" , "Self in World Space", "Linear gradient is computed for object along the specified axis in world space"),
    #     ("OBJECT" , "Object", "Linear gradient is computed based on a given object's bounds in world space"),
    #     ("PARENT_LOCAL" , "Parent Object in Local Space", "Linear gradient is computed based on each object's parent along the specified parent's axis in local space"),
    #     ("PARENT_WORLD" , "Parent Object in World Space", "Linear gradient is computed based on each object's parent along the specified axis in world space")
    # ]
    # linear_mask_obj_mode: EnumProperty(name="Mode", items=linear_mask_obj_modes, default=1)
    # linear_mask_obj: PointerProperty(type=bpy.types.Object, name="Object", description="")
    # linear_mask_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # linear_mask_axis: EnumProperty(name="Axis", items=axis_xyz, default=2, description="")

    # linear_mask_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # linear_mask_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # linear_mask_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    # linear_mask_falloff: FloatProperty(name="Falloff", min=0.0, default=1.0, description="")
    
    # # random per collection
    # random_per_collection: BoolProperty(name="Random Per Collection", default=False, description="")
    # random_per_collection_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    
    # random_per_collection_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # random_per_collection_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # random_per_collection_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    # random_per_collection_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="")
    
    # # random per object
    # random_per_object: BoolProperty(name="Random Per Object", default=False, description="")
    # random_per_object_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    
    # random_per_object_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # random_per_object_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # random_per_object_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    # random_per_object_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="")
    
    # # random per poly
    # random_per_poly: BoolProperty(name="Random Per Poly", default=False, description="")
    # random_per_poly_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    
    # random_per_poly_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # random_per_poly_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # random_per_poly_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    # random_per_poly_uniform: FloatProperty(name="Uniform", min=0.0, max=1.0, default=1.0, description="")

    # # parent
    # parent_modes = [
    #     ("AUTOMATIC" , "Automatic", "Traverses the entire parent tree (up to a specified depth) and generates all uvmaps required, starting from the specified UVMap index & channel. Please take note on how many uvmaps are created in the info panel" ),
    #     ("MANUAL", "Manual", "Requires several successive bakes. For instance, set the max depth to 3 and current depth to 1, configure the data to bake (UV index etc), make sure to enable the duplicate option but *disable* the merge option and press bake. Set the current depth to 2, *disable* the duplicate option, update the data to bake (UV index etc) and bake again. Set the current to depth to 3, update the data to bake one last time, *enable* the merge option and bake.")
    # ]
    # parent_mode: EnumProperty(name="Mode", items=parent_modes, default=0, description="")

    # parent_depth: IntProperty(name="Current", default=1, min=1, description="")
    # parent_max_depth: IntProperty(name="Depth", default=2, min=1, max=7, description="")

    # parent_automatic_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # parent_automatic_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")

    # # parent position
    # parent_position: BoolProperty(name="Position", default=False, description="")
    # parent_position_channel_mode: EnumProperty(name="Mode", items=pos_channels, default=0, description="")

    # parent_position_x: BoolProperty(name="X", description="")
    # parent_position_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_position_x_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # parent_position_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # parent_position_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")

    # parent_position_y: BoolProperty(name="Y", description="")
    # parent_position_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_position_y_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # parent_position_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # parent_position_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="")

    # parent_position_z: BoolProperty(name="Z", description="")
    # parent_position_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_position_z_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # parent_position_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # parent_position_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="")

    # parent_position_packed_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # parent_position_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")

    # parent_position_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # parent_position_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")
    
    # # parent axis
    # parent_axis: BoolProperty(name="Axis", default=False, description="")
    # parent_axis_component: EnumProperty(name="Axis", items=axis_xyz, default=1, description="")
    
    # parent_axis_channel_mode: EnumProperty(name="Mode", items=axis_modes, default=0, description="")

    # parent_axis_x: BoolProperty(name="X Component", description="")
    # parent_axis_x_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_axis_x_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # parent_axis_x_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # parent_axis_x_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")
    
    # parent_axis_y: BoolProperty(name="Y Component", description="")
    # parent_axis_y_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_axis_y_uv_index: IntProperty(name="UV Map", min=0, default=1, description="")
    # parent_axis_y_uv_channel: EnumProperty(name="Channel", items=uv, default=1, description="")
    # parent_axis_y_rgba: EnumProperty(name="Channel", items=rgba, default=1, description="")
    
    # parent_axis_z: BoolProperty(name="Z Component", description="")
    # parent_axis_z_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    # parent_axis_z_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # parent_axis_z_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # parent_axis_z_rgba: EnumProperty(name="Channel", items=rgba, default=2, description="")
    
    # parent_axis_packed_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # parent_axis_packed_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    
    # parent_axis_ab_packed_a_comp: EnumProperty(name="A Component", items=axis_xyz, default=0, description="")
    # parent_axis_ab_packed_b_comp: EnumProperty(name="B Component", items=axis_xyz, default=1, description="")

    # # fixed value
    # fixed_value: BoolProperty(name="Fixed Value", default=False, description="")
    # fixed_value_data: FloatProperty(name="Value", default=0.0, description="")
    # fixed_value_mode: EnumProperty(name="Mode", items=modes, default=0, description="")
    
    # fixed_value_uv_index: IntProperty(name="UV Map", min=0, default=2, description="")
    # fixed_value_uv_channel: EnumProperty(name="Channel", items=uv, default=0, description="")
    # fixed_value_rgba: EnumProperty(name="Channel", items=rgba, default=0, description="")

    # # direction
    # direction: BoolProperty(name="Direction", default=False, description="")
    # direction_modes = [
    #     ("3DRAND" , "Random 3D", "Generates a random 3D unit vector in [-1:1] range" ),
    #     ("2DRAND" , "Random 2D", "Generates a random 2D unit vector in [-1:1] range. Z will be 0" ),
    #     ("3DVECTOR" , "3D Vector", "User-set 3D direction" ),
    #     ("2DVECTOR", "2D Vector", "User-set 2D direction"),
    # ]
    # direction_mode: EnumProperty(name="Vector", items=direction_modes, default=0, description="")
    # direction_vector_x: FloatProperty(name="X", default=0.0, description="")
    # direction_vector_y: FloatProperty(name="Y", default=0.0, description="")
    # direction_vector_z: FloatProperty(name="Z", default=1.0, description="")
    
    # direction_pack_modes = [
    #     ("NORMALS", "Normals", "Use normal to store the unit vector. Vector will be normalized and normals will be overriden." ),
    #     ("VCOL" , "VCol", "Use vertex color to store the unit vector. Vector will be normalized and remapped from [-1:1] to [0:1] range." )
    # ]
    # direction_pack_mode: EnumProperty(name="Mode", items=direction_pack_modes, default=0, description="")

    # # mesh
    # duplicate_mesh: BoolProperty(name="Duplicate", default=True, description="")
    # make_single_user: BoolProperty(name="Make Single-User", default=True, description="")
    # merge_mesh: BoolProperty(name="Merge & Clean", default=True, description="")
    # mesh_name: StringProperty(name="Name", default="BakedMesh.DATA", description="")
    # scale: FloatProperty(name="Scale", min=0.001, default=100.0, description="")
    # invert_x: BoolProperty(name="Invert X", default=False, description="")
    # invert_y: BoolProperty(name="Invert Y", default=True, description="")
    # invert_z: BoolProperty(name="Invert Z", default=False, description="")
    # origin: PointerProperty(type=bpy.types.Object, name="Origin", description="")
    # precision_offset: FloatProperty(name="Precision Offset", min=1.0, default=1.0, description="")

    # export_mesh: BoolProperty(name="Export", default=True, description="")
    # export_mesh_file_name: StringProperty(name="Name", default="SM_<ObjectName>", description="")
    # export_mesh_file_path: StringProperty(name="Path", default="//", description="")
    # export_mesh_file_override: BoolProperty(name="Override", default=True, description="")

    xml: BoolProperty(name="XML", default=False, description="")
    xml_path: StringProperty(name="Filepath", default="//", description="", subtype='FILE_PATH')


def register():
    bpy.types.Scene.DataBakerSettings = PointerProperty(type=DATABAKER_PG_SettingsPropertyGroup)
    bpy.types.Scene.DataBakerReport = PointerProperty(type=DATABAKER_PG_ReportPropertyGroup)

def unregister():
    del bpy.types.Scene.DataBakerSettings
    del bpy.types.Scene.DataBakerReport
    