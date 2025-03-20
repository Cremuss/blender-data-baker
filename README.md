![image info](Documentation/Images/gray.jpg)
# blender-data-baker
This addon packs several professional-grade techniques commonly used in the video game industry: Vertex Animation Textures, Bone Animation Textures, Object Animation Textures, Pivot Painter 2.0, UV Pivots and more.

## Summary

[Installation](#i.-installation)
[Documentation](#ii.-documentation)
  [I VAT - Vertex Animation Textures Baker](#i.-vat---vertex-animation-textures-baker)
    [I.I VAT - Intro](#i.1.-vat---intro)
    [I.I VAT - Animation](#i.2.-vat---animation)
    [I.I VAT - Mesh Sequence](#i.3.-vat---mesh-sequence)
  [II Data - UV VCol Data Baker](#ii.-data---uv-vcol-data-baker)
    [II.I Data - Intro](#ii.i.-data---intro)

## Glossary

VAT - The process of baking vertex data into textures AND the resulting texture(s)
BAT - The process of baking bone data into textures AND the resulting texture(s)
OAT - The process of baking object data into textures AND the resulting texture(s)
POT - Power of Two
NPOT - Non Power of Two
    
## Installation
This addon is available as an **official** [Blender extension](https://extensions.blender.org/about/). ![](Documentation/Images/doc_install_03.jpg)

If this isn't an option, you could still first download a **ZIP** of this git repo.
![](Documentation/Images/doc_install_01.jpg)

Then, open the **Edit>Preferences** window, go to the **Get Extensions** tab and search for **Install from Disk** in the dropdown menu located at the very top-right.
![](Documentation/Images/doc_install_04.jpg)

## Documentation

## I. VAT - Vertex Animation Textures Baker

### I.1. VAT - Intro

**Vertex Animation Texture** (VAT) is one of the simplest technique for **baking skeletal animation(s)** (or any animation) **into textures** by encoding data per vertex, per frame, in pixels. These textures are then sampled in a **vertex shader** to **play the animation** on a **static mesh**.

This can lead to significant performance gains, as rendering skeletal meshes is typically the most expensive way to render animated meshes. By using static meshes, you can leverage instancing and particles to efficiently render crowds, etc. However, this technique also has its own pros and cons, which we'll discuss in the following sections.

### I.2. VAT - Principles

For **each frame and vertex**, an **XYZ vector** is stored in the **RGB channels** of a **unique pixel** in a texture. That vector is often the vertex **offset**, indicating how much the vertex has moved from the rest pose, at that frame.

[img](Documentations/Images/)

> [!NOTE]
> You can opt for storing the vertex's *local position* instead of an *offset from a reference pose*. That local position would likely have to be then transformed from local to world space based on the mesh's world matrix. Working with offsets is typically simpler, especially in *Unreal Engine*.

Offsetting vertices in a vertex shader **does not update the normals**, and for good reasons. Normals may be computed in your DCC software, like Blender, in many different ways and *re-evaluated each frame* (e.g. smooth/flat/weighted normals). Some of these methods require averaging the normals of all triangles surrounding a vertex, which a **vertex shader cannot do**. Moreover, there's *no direct correlation* between a *vertex's position* (or its *offset*) and its *normal* so the normal can't be derived from the offset alone. For example, a vertex moved along its normal would change position but its normal wouldn't. This is a more complex topic than many tech artists may initially realize.

> [!NOTE]
> DDX/DDY can be used in *pixel shaders* to derive *flat normals* from the surface position but it results in a faceted look that is most often undesired.

Thus, **for each frame and vertex**, it's also common to bake the **XYZ vertex normal into a second VAT**. This can be skipped if the animations are minimal, with little movement, and/or if you don't mind the lighting/shadow issues you get from *not* updating the normals (e.g. for distant props).

Finally, to **sample** the offset and normal VATs, a **special UVMap** is created to **center each vertex on a unique texel**.

[img](Documentations/Images/)

Playing the animation in the vertex shader thus simply involves *manipulating the UV coordinates* of that UVMap to sample the texels corresponding to the desired frame. Often, it simply boils down to offsetting the V component, assuming a **one-frame-per-row** packing scheme was used, more on that in the following section.

[img](Documentations/Images/)

### I.3. VAT - Packing, Interpolation, Padding, Resolution

The simplest way data can be stored in a VAT is using a **one-frame-per-row** packing scheme. Let's consider baking a skeletal mesh made of **400 vertices** and having **200 frames** of animation. The resulting **VAT resolution** would be **400x200**: 200 rows (frames) of 400 pixels (vertices). In other words, the VAT texture would contain the data of every vertex for every frame, one frame stacked on top of each other.

[img](Documentations/Images/)

> [!NOTE]
> This method severly constraints the amount of vertices that can be baked, something that is discussed in later sections

**Playing the animation** involves sampling the texture and **offsetting the V coordinate by one row/texel at a time**.

[img](Documentations/Images/)

Since each frame is *adjacent* in the texture, the pixel interpolation that naturally occurs when sampling a texture on the GPU can be used to **get frame linear interpolation for free**. *UVs between two frames will average them*, allowing the V axis to be simply *scrolled* to get a butter smooth animation.

[img](Documentations/Images/)

> [!IMPORTANT]
> UVs may be stored in 16 bits by default in some game engines, including *Unreal Engine*. Thus, precision issues might arise with larger textures and undesired interpolation might occur between frames but also between vertices as well. That is something that can be prevented using Nearest sampling which, however, no longer allows us to leverage pixel interpolation to get frame interpolation for free. This is further discussed in later sections

Frame interpolation can be troublesome when **baking multiple animations** and **looping a specific one**. VATs are often used to **render and animate crowds**, where some kind of state machine *selects* and *cycles through animations*. Playing a specific clip in a VAT containing multiple clips merely involves *clamping the V coordinate* to a specific *clip's range* and *wrapping* it around when needed.

[img](Documentations/Images/)

In such a case, pixel interpolation (and thus frame interpolation) can be an issue because, when looping a specific clip, we would need to interpolate between that clip's last and first frames. However, since the VAT describes the whole animation as a simple stack of frames, the last frame will instead interpolate with the first frame of the next animation, and the first frame with the last frame of the previous animation.

[img](Documentations/Images/)

This can be fixed by adding extra frames to the VAT, a process we may call **padding**. For each clip, *insert its last frame before its first*, and *append its first frame after its last*.

[img](Documentations/Images/)

While **padding** duplicates frames and thus slightly **increases the VAT resolution**, the benefits should outweigh the drawbacks. That is, assuming you do use GPU interpolation to get frame interpolation for free, *else padding serves no purpose*.

> [!NOTE]
> You may choose to add padding on last frames only or first frames only but that’s assuming you know the direction the V coordinates have to be scrolled in, which may vary depending on the UV coordinate system of the targeted game engine/graphics API, and that animations may only be played in that direction.

Now, this **one-frame-per-row** packing scheme has its limits and there are a couple of things to note.

Firstly, it often results in **non-power-of-two** (NPOT) VATs. Vertex & frame count are unlikely to be a power of two and while NPOT textures *were once unsupported in most game engines*, the *situation has improved* but there are still some important things to note. It’s very hard to find information on what happens under the hood in older and more recent GPUs and coming with absolute truths on such a broad and obscure topic is unwise.

That said, it wouldn’t be unrealistic to assume that an **NPOT texture may be stored as the next power-of-two (POT) texture** on *some* hardware (e.g. mobile?). One may even read here and there older reports stating that a NPOT texture *may* be automatically padded with black pixels to be converted to a POT texture, causing interpolation issues on borders, but we digress. A **400x200** texture *may* be stored as a **512x256** texture depending on your targeted hardware, game engine, graphics API etc. It is however not something I have experienced with *Unreal Engine* in recent years.

[img](Documentations/Images/)

While this doesn’t directly affect the user if it was true (this is a memory layout thingy), it would waste precious GPU memory and would therefore affect memory-bandwidth. This shouldn't be worrying for smaller textures, but a 2049x2048 texture, for example, would be theoretically stored as a 4096x2048 texture on *some* hardware, just because of that extra pixel in width! Worrying, but again, it doesn't seem to be the case on recent hardware. Everything seems to point to an NPOT texture behaving just like a POT texture in memory, but, you know, GPUs... You were warned.

Secondly, while NPOT textures are **now widely supported in most game engines**, that doesn't mean they are widely supported by the hardware that you can target with said game engines (e.g. mobile?). Support may even be partial or bugged. It may be a good idea to double-check your targeted hardware specs and crash-test things.

Thirdly, NPOT textures can cause problems with **mipmapping**. While this **doesn't apply to VATs** (which shouldn’t be mipmapped), it’s still worth mentioning.

In short, NPOT textures **should be fine for most use cases in 2025**. This isn’t an absolute truth of course, so don’t take their support for granted. If they happen to be an issue for you, VATs can simply be **padded with blank pixels** to **fit the next POT resolution**, and the necessary *vertex-to-texel UVMap updated* accordingly (extra padding decreases the texel size).

[img](Documentations/Images/)

That said, when working with VATs, **exceeding 4096 pixels** is generally **not recommended**. 8K textures may not be supported on mobile or web apps and you **can't downsize a VAT** like you would with, say, a troublesome diffuse or roughness texture. Each texel in a VAT texture *holds specific information* that *can’t be lost* or averaged with nearby texels! If you need such a high resolution anyway, one might ask if VATs is the correct method for what you have in mind. There are other baking techniques that may be better suited, like *Bone Animation Textures*, and newer file formats like *Alembic* that may be worth considering.

To conclude on the **one-frame-per-row** packing scheme, assuming you don’t want to exceed 4096 pixels, it obviously limits you to baking no more than 4096 frames (which is fine for most cases) and no more than 4096 vertices (which is more restrictive). An **alternative packing method exists** that alleviates this constraint, though it comes with its *own drawbacks*.

The workaround is to use **multiple rows** to store **one frame**'s worth of vertex data.

[img](Documentations/Images/)

**Sampling** the animation then involves offsetting the V coordinates by the **appropriate row/texel amount**. Note that pixel interpolation can no longer be used for frame interpolation, as it would cause interpolation with other vertex data, not the next frame.

[img](Documentations/Images/)

Additionally, padding is unnecessary since interpolation is no longer an option. At this point it is recommended to use **Nearest** sampling to prevent the GPU from interpolating pixels and picking the closest texel instead. This may be particularly relevant if you happen to bake a lot of vertices and/or frames. As the VAT resolution increases to contain more data, the distance between each texel diminishes.

[img](Documentations/Images/)

Precision, when it comes to storing numbers in computers, is an issue as old as computer science. In fact, each vertex UV isn’t precisely centered on a texel. There’s a tiny bit of jitter and the amount of imprecision might become concerning as the distance between texels get too small, or in other words, as the VAT size increases. This is especially true as UVs might be stored in 16 bits float by default in most game engines, including *Unreal Engine*. Sampling a VAT with pixel interpolation might thus induce a tiny bit of ‘data corruption’ as each vertex might not precisely sample the desired frame, nor the desired vertex data as well. Thus, using Nearest sampling is often recommended.

[img](Documentations/Images/)

Using Nearest sampling might not even totally fix imprecision issues because of 16 bits float UVs. As you approach 4K and even higher resolutions, the distance between each texel is so small that the amount of imprecision in the UVs might be great enough for Nearest sampling to sample the wrong texel. In such case, you might try to use 32 bits UVs on that mesh if possible. This is called *full precision UVs in Unreal Engine*.

[img](Documentations/Images/)

> [!NOTE]
> Note that it is still possible to get frame linear interpolation despite using Nearest sampling. It simply involves sampling the VAT texture a second time, one frame ahead and doing the interpolation in the vertex shader manually, something that shouldn't be too expensive for most applications. This could even be toggled off at a distance on LODs etc.

To conclude on packing methods, there’s a third method of packing frame data in VATs, one that may be called **continuous** and one that best utilizes the empty pixels that you may either get with the **one-frame-per-row** packing scheme if requiring POT VATs, or more likely with the **multiple-rows-per-frame** packing scheme.

[img](Documentations/Images/)

This packing method simply stores one frame after the other and leaves no empty pixel.

[img](Documentations/Images/)

This requires a more complex algorithm to generate the UVs for sampling the VATs, and is considered experimental as it still needs thorough testing to ensure it doesn’t encounter precision issues (16-bit or even 32-bit). On paper, this **continuous** packing method promises to maximize the VAT's resolution and allowss data to be tightly packed in POT textures, ensuring wide hardware support.

@note vertex normal interpolation!

## II. Data - UV VCol Data Baker

### II.I. Data - Intro

The concept of **baking data into UVs and Vertex Colors** is likely as old as real-time rendering itself.

Many artists and tech artists are probably already familiar with using **vertex colors to paint masks** in the **RGBA channels**. These masks are commonly used to drive artistic processes, such as customizing a material: fading in moss here, adding cracks to a brick texture there, sprinkling sand between floor cracks, and so on. You get the idea, using vertex colors is usually a very *painterly process*.

Taking a step back, one might wonder if the **RGB channels of vertex colors** could be used to **store the XYZ components of a vector**. Any vector. And with some care, they can. The vertex color RGBA channels can be thought of as a way **for each vertex to store four 8-bit integers**.

Similarly, artists are often taught to view **UVs** solely as a means of **storing coordinates for texture projection** onto a 3D surface, along with the constraints that come with this mindset: *limiting texture deformation*, *hiding seams*, *staying within the [0:1] bounds* etc. However, if we take a step back, just like vertex colors, UVs can be seen as a way for **each vertex to store two 16- or 32-bit floats**. Most DCC softwares and real-time applications allow up to eight UV maps, which means up to **16 floats can be encoded per vertex**. 

While you do usually need to follow general guidelines when authoring a UV map for texture projection, like limiting stretch, these constraints no longer exist and possibilities become endless when you start thinking of **UVs as a way to store arbitrary data**, such as *baking pivots*, *axis*, *normals*, *shape keys/morph targets*, and so on.

The **Data Baker tool aims to facilitate and automate this process**.




