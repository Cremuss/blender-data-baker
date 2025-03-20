![image info](Documentation/Images/gray.jpg)
# blender-data-baker
This addon packs several professional-grade techniques commonly used in the video game industry: Vertex Animation Textures, Bone Animation Textures, Object Animation Textures, Pivot Painter 2.0, UV Pivots and more.

## Summary
[Installation](#i.-installation)
[Documentation](#ii.-documentation)
  [I VAT - Vertex Animation Textures Baker](#i-vat---vertex-animation-textures-baker)
    [I.I VAT - Intro](#i.i-vat---intro)
    [I.I VAT - Animation](#i.i-vat---animation)
    [I.I VAT - Mesh Sequence](#i.i-vat---mesh-sequence)
  [II Data - UV VCol Data Baker](#ii-data---uv-vcol-data-baker)
    [II.I Data - Intro](#ii.i-data---intro)

## Installation
This addon is available as an **official** [Blender extension](https://extensions.blender.org/about/). ![](Documentation/Images/doc_install_03.jpg)

If this isn't an option, you could still first download a **ZIP** of this git repo.
![](Documentation/Images/doc_install_01.jpg)

Then, open the **Edit>Preferences** window, go to the **Get Extensions** tab and search for **Install from Disk** in the dropdown menu located at the very top-right.
![](Documentation/Images/doc_install_04.jpg)

## Documentation

## I VAT - Vertex Animation Textures Baker

### I.I VAT - Intro

**Vertex Animation Texture** is one of the simplest technique for **baking skeletal animation(s)** (or any animation) **into textures**. These textures are then sampled in a **vertex shader** to **play the animation** on a **static mesh**. This can lead to significant performance gains, as rendering skeletal meshes is typically the most expensive way to render animated meshes. By using static meshes, you can leverage instancing and particles to efficiently render crowds, etc. However, this technique also has its own pros and cons, which we'll discuss in the following sections.

### I.II VAT - Principles

For each frame and vertex, the XYZ vertex offset is stored in the RGB channels of a unique texture pixel. This offset indicates how much the vertex has moved from the rest pose at that frame, though you can store the vertex local position instead, depending on your needs. Working with offsets is typically simpler, especially in Unreal Engine.

However, offsetting vertices in a vertex shader doesn't update the normals because it's not feasible in real-time applications. Normals may be computed in your DCC software, like Blender, in may different ways (e.g. smooth/flat/weighted normals) and re-evaluated each frame. Some expensive-ish methods require averaging nearby triangle normals, which a vertex shader cannot do.

Thus, for each frame and vertex, it's also common to bake the XYZ vertex normal into a second texture, just like with offsets. This step can be skipped if the animations are minimal, with little movement, or if you don't mind the resulting lighting/shadow issues (e.g., for distant props).

Finally, to sample the vertex animation offset and normal textures, a special UVMap is created to assign a unique texel to each vertex. Playing the animation in the vertex shader involves manipulating the UV coordinates to sample the texels for a specific frame, typically by scrolling the V component assuming a vertex-width frames-height packing scheme was used.

## II Data - UV VCol Data Baker

### II.I Data - Intro


