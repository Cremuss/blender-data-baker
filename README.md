![image info](Documentation/Images/gray.jpg)
# blender-data-baker
This addon packs several professional-grade techniques commonly used in the video game industry: Vertex Animation Textures, Bone Animation Textures, Object Animation Textures, Pivot Painter 2.0, UV Pivots and more.

[Installation](#i.-installation)
[Documentation](#ii.-documentation)
  [I VAT - Vertex Animation Textures Baker](#i.-vat---vertex-animation-textures-baker)
    [I.I VAT - Intro](#i.1.-vat---intro)
    [I.I VAT - Animation](#i.2.-vat---animation)
    [I.I VAT - Mesh Sequence](#i.3.-vat---mesh-sequence)
  [II Data - UV VCol Data Baker](#ii.-data---uv-vcol-data-baker)
    [II.I Data - Intro](#ii.i.-data---intro)
    
## Installation
This addon is available as an **official** [Blender extension](https://extensions.blender.org/about/). ![](Documentation/Images/doc_install_03.jpg)

If this isn't an option, you could still first download a **ZIP** of this git repo.
![](Documentation/Images/doc_install_01.jpg)

Then, open the **Edit>Preferences** window, go to the **Get Extensions** tab and search for **Install from Disk** in the dropdown menu located at the very top-right.
![](Documentation/Images/doc_install_04.jpg)

## Documentation

## I. VAT - Vertex Animation Textures Baker

### I.1. VAT - Intro

**Vertex Animation Texture** (VAT) is one of the simplest technique for **baking skeletal animation(s)** (or any animation) **into textures** by encoding data per vertex per frame in pixels. These textures are then sampled in a **vertex shader** to **play the animation** on a **static mesh**. This can lead to significant performance gains, as rendering skeletal meshes is typically the most expensive way to render animated meshes. By using static meshes, you can leverage instancing and particles to efficiently render crowds, etc. However, this technique also has its own pros and cons, which we'll discuss in the following sections. This documentation refers to VAT both as the technique of baking vertex data and the texture(s) resulting from that process.

### I.2. VAT - Principles

For **each frame and vertex**, the **XYZ vertex offset** is stored in the **RGB channels** of a **unique texture pixel**. This offset indicates how much the vertex has moved from the rest pose at that frame, though you can choose to store the *vertex local position* instead. Working with offsets is typically simpler, especially in *Unreal Engine*.

However, offsetting vertices in a vertex shader *doesn't update the normals* because it's not feasible in real-time applications. Normals may be computed in your DCC software, like Blender, in may different ways (e.g. smooth/flat/weighted normals) and re-evaluated each frame. Some expensive-ish methods require averaging nearby triangle normals, which a vertex shader cannot do.

Thus, **for each frame and vertex**, it's also common to bake the **XYZ vertex normal into a second VAT**. Note that this step can be skipped if the animations are minimal, with little movement, and/or if you don't mind the lighting/shadow issues resulting from *not* updating the normals (e.g. for distant props).

Finally, to *sample* the vertex animation offset and normal textures, a **special UVMap** is created to **assign a unique texel to each vertex**. Playing the animation in the vertex shader thus simply involves *manipulating the UV coordinates* to sample the texels for a specific frame, typically by scrolling the V component assuming a one-frame-per-row packing scheme was used.

### I.3. VAT - Packing Schemes & Issues
The simplest way data can be stored in a VAT is using a **one-frame-per-row** packing scheme. For example, with a mesh having *400 vertices* and *200 frames* of animation, the resulting *VAT resolution* would be *400x200*. Each frame's vertex data would be stored in a *single row of pixels*, one pixel per vertex, creating a *'stack' of 200 rows*, one-frame-per-row, as the name implies. **Playing the animation** involves sampling the texture and **offsetting the V coordinate by one texel at a time**.
Since each frame is adjacent in the texture, the pixel interpolation that naturally occurs when sampling on the GPU can be used to get frame linear interpolation for free. UVs between two frames will average them, allowing the V axis to be scrolled for smooth animation.
This can be troublesome for several reasons, which we'll cover in more detail later. For now, let's focus on one issue that arises when baking multiple animations and looping a specific one.
VATs are often used to render crowds, where a state machine selects and cycles through animations. This merely involves clamping the V coordinate to a specific clip's range and wrapping it around.
When looping a clip, interpolating between the last and first frames is necessary. However, since the VAT is a simple stack of frames, the last frame will instead interpolate with the first frame of the next animation. This can be fixed by adding extra frames to the VAT, or what may be called padding. For each clip, insert its last frame before its first, and append its first frame after its last. While this adds extra data and thus slightly increases the VAT resolution, the benefits should outweigh the drawbacks.
Now, this vertex-width-frame-height packing scheme has its limits.
Firstly, it often results in non-power-of-two (NPOT) VATs. While NPOT textures were once unsupported in most game engines, the situation has improved. However, there are still some important things to note.
For GPUs, NPOT textures don’t actually exist. They are padded and stored as the next power-of-two (POT) texture. For example, a 400x200 texture will be stored as a 512x256 texture. While this doesn’t directly affect the user, it does waste GPU memory and may thus affect memory-bandwidth. This shouldn't be worrying for smaller textures, but a 2049x2048 texture, for example, would be padded and stored as a 4096x2048 texture—just because of that extra pixel in width.
Secondly, while NPOT textures are widely supported in most game engines, they can still be troublesome or unsupported on certain hardware (e.g., mobile), so it's important to verify this isn't an issue.
Third, NPOT textures can cause problems with mipmapping. While this doesn't apply to VATs (which shouldn’t be mipmapped), it’s still worth mentioning. In short, NPOT textures should be fine as long as you're aware of the potential issues.
That said, when working with VATs, exceeding a resolution of 4096 pixels is generally not recommended. 8K textures may not be supported on mobile or web apps, and you can't simply downsize a VAT, like you would with, say, a diffuse or roughness texture. Each texel in a VAT texture holds specific information that can’t be lost or averaged with nearby texels!
If NPOT textures are an issue for you, VATs can simply be padded with blank pixels to fit the next POT resolution, and the necessary vertex-to-texel UVMap updated accordingly (extra padding decreases the texel size and thus UVs need to be scaled down).
To conclude on the vertex-width-frame-height packing scheme, assuming you don’t want to exceed a 4k resolution, it limits you to baking no more than 4096 frames (which is fine for most cases) and no more than 4096 vertices (which is more restrictive). However, an alternative packing method exists, though it comes with its own drawbacks.

The workaround is to use multiple rows of pixels to store one frame's worth of vertex data.
Sampling the animation then involves offsetting the V coordinates by the appropriate texel amount. Note that pixel interpolation can no longer be used for frame interpolation, as it would cause interpolation with other vertex data, not the next frame. Additionally, padding is unnecessary since interpolation is no longer an option. It's thus recommended to use Nearest sampling/filter to prevent the GPU from interpolating pixels.

# @TODO mention nearest sampling?

## II. Data - UV VCol Data Baker

### II.I. Data - Intro


