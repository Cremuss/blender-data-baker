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

**Vertex Animation Texture** (VAT) is one of the simplest technique for **baking skeletal animation(s)** (or any animation) **into textures** by encoding data per vertex, per frame, in pixels. These textures are then sampled in a **vertex shader** to **play the animation** on a **static mesh**. This can lead to significant performance gains, as rendering skeletal meshes is typically the most expensive way to render animated meshes. By using static meshes, you can leverage instancing and particles to efficiently render crowds, etc. However, this technique also has its own pros and cons, which we'll discuss in the following sections. This documentation refers to VAT both as the technique of baking vertex data and the texture(s) resulting from that process.

### I.2. VAT - Principles

For **each frame and vertex**, the **XYZ vertex offset** is stored in the **RGB channels** of a **unique texture pixel**. This offset indicates how much the vertex has moved from the rest pose at that frame, though you can choose to store the *vertex local position* instead. Working with offsets is typically simpler, especially in *Unreal Engine*.

However, offsetting vertices in a vertex shader **does not update the normals** because it's not feasible in real-time applications. Normals may be computed in your DCC software, like Blender, in may different ways (e.g. smooth/flat/weighted normals) and *re-evaluated each frame*. Some expensive-ish methods require averaging nearby triangle normals, which a **vertex shader cannot do**.

Thus, **for each frame and vertex**, it's also common to bake the **XYZ vertex normal into a second VAT**. Note that this step can be skipped if the animations are minimal, with little movement, and/or if you don't mind the lighting/shadow issues resulting from *not* updating the normals (e.g. for distant props).

Finally, to *sample* the offset and normal VATs, a **special UVMap** is created to **center each vertex on a unique texel**. Playing the animation in the vertex shader thus simply involves *manipulating the UV coordinates* to sample the texels corresponding to the desired animation frame. Often, it simply boils down to offsetting the V component, assuming a **one-frame-per-row** packing scheme was used.

### I.3. VAT - Packing, Interpolation, Padding, Resolution

The simplest way data can be stored in a VAT is using a **one-frame-per-row** packing scheme. Let's consider baking a skeletal mesh made of **400 vertices** and having **200 frames** of animation. The resulting **VAT resolution** would be **400x200** since each frame's vertex data would be stored in a *single row of pixels*, one pixel per vertex, creating a *'stack' of 200 rows*, one-frame-per-row, as the name implies.

[img](Documentations/Images/)

**Playing the animation** involves sampling the texture and **offsetting the V coordinate by one row/texel at a time**.

[img](Documentations/Images/)

Since each frame is *adjacent* in the texture, the pixel interpolation that naturally occurs when sampling a texture on the GPU can be used to **get frame linear interpolation for free**. *UVs between two frames will average them*, allowing the V axis to be *scrolled* for smooth animation.

[img](Documentations/Images/)

That said, this can be *troublesome* for several reasons, which we'll cover in more detail later. For now, let's focus on one issue that arises when **baking multiple animations** and **looping a specific one**.

VATs are often used to **render and animate crowds**, where some kind of state machine *selects* and *cycles through animations*. This merely involves *clamping the V coordinate* to a specific *clip's range* and *wrapping* it around when needed.

[img](Documentations/Images/)

In such a case, pixel interpolation (and thus frame interpolation) can be an issue because, when looping a specific clip, we would need to interpolate between that clip's last and first frames. However, since the VAT describes the whole animation as a simple stack of frames, the last frame will instead interpolate with the first frame of the next animation, and the first frame with the last frame of the previous animation.

[img](Documentations/Images/)

This can be fixed by adding extra frames to the VAT, what may be called **padding**. For each clip, *insert its last frame before its first*, and *append its first frame after its last*, though you may choose to do just one of the two. That’s assuming you know the direction the V coordinates have to be scrolled, which may vary depending on the UV coordinate system of the targeted game engine, and that animations may only be played in that direction. While **padding** duplicates frames and thus slightly **increases the VAT resolution**, the benefits should outweigh the drawbacks.

[img](Documentations/Images/)

Now, this **one-frame-per-row** packing scheme has its limits.

Firstly, it often results in **non-power-of-two** (NPOT) VATs. Vertex & frame count are unlikely to be a power of two and while NPOT textures *were once unsupported in most game engines*, the *situation has improved* but there are still some important things to note. It’s very hard to find information on what happens under the hood in older and more recent GPUs and coming with absolute truths on such a broad and obscure topic is unwise. It wouldn’t be unrealistic to assume that an **NPOT texture may be store as the next power-of-two** (POT) texture on a lot of hardware. One may even read here and there that a NPOT texture may be padded with black pixels to be converted to a POT texture, causing interpolation issues on borders, but we digress. A **400x200** texture *may* be stored as a **512x256** texture depending on your targeted hardware, game-engine, graphics API etc.

[img](Documentations/Images/)

While this doesn’t directly affect the user, it does waste precious GPU memory and may therefore affect memory-bandwidth. This shouldn't be worrying for smaller textures, but a 2049x2048 texture, for example, would be theoretically padded and stored as a 4096x2048 texture on *some* hardware, just because of that extra pixel in width! Worrying. I’d try to work with a vertex & frame count that isn’t *that far off* from a POT.

Secondly, while NPOT textures are **now widely supported in most game engines**, they can still be troublesome or *unsupported on certain hardware* (e.g. mobile?). It may be a good idea to double-check your targeted hardware specs.

Third, NPOT textures can cause problems with *mipmapping*. While this **doesn't apply to VATs** (which shouldn’t be mipmapped), it’s still worth mentioning.

In short, NPOT textures **should be fine for most use cases in 2025**. This isn’t an absolute truth of course, so don’t take their support for granted. If they happen to be an issue for you, VATs can simply be **padded with blank pixels** to **fit the next POT resolution**, and the necessary *vertex-to-texel UVMap updated* accordingly (extra padding decreases the texel size).

[img](Documentations/Images/)

That said, when working with VATs, **exceeding 4096 pixels** is generally **not recommended**. 8K textures may not be supported on mobile or web apps and you **can't downsize a VAT** like you would with, say, a troublesome diffuse or roughness texture. Each texel in a VAT texture *holds specific information* that *can’t be lost* or averaged with nearby texels! If you need such a high resolution anyway, one might ask if VATs is the correct method for what you have in mind. There are other baking techniques that may be better suited, like *Bone Animation Textures*, and newer file formats like *Alembic* that may be worth considering.

To conclude on the **one-frame-per-row** packing scheme, assuming you don’t want to exceed 4096 pixels, it obviously limits you to baking no more than 4096 frames (which is fine for most cases) and no more than 4096 vertices (which is more restrictive). An **alternative packing method exists** that alleviates this constraint, though it comes with its *own drawbacks*.

The workaround is to use **multiple-rows-per-frame** to store one frame's worth of vertex data.

[img](Documentations/Images/)

Sampling the animation then involves offsetting the V coordinates by the **appropriate row/texel amount**. Note that pixel interpolation can no longer be used for frame interpolation, as it would cause interpolation with other vertex data, not the next frame.

[img](Documentations/Images/)

Additionally, padding is unnecessary since interpolation is no longer an option. At this point it is recommended to use **Nearest** sampling to prevent the GPU from interpolating pixels and picking the closest texel instead. This may be particularly relevant if you happen to bake a lot of vertices and/or frames. As the VAT resolution increases to contain more data, the distance between each texel diminishes.

[img](Documentations/Images/)

Precision, when it comes to storing numbers in computers, is an issue as old as computer science. In fact, each vertex UV isn’t precisely centered on a texel, there’s a tiny bit of jitter and the amount of imprecision might become concerning as the distance between texels get too small, or in other words, as the VAT size increases. This is especially true as UVs might be stored in 16 bits float by default in most game engines, including Unreal Engine. Sampling VAT might thus induce a tiny bit of ‘data corruption’ as each texel not only interpolate between frames but also between themselves. Thus, Nearest sampling is often required.
In such case, there’s often a toggle to enable 32 bits UVs on that mesh if needed. Note that it is still possible to get frame linear interpolation despite using nearest. It simply involves sampling the VAT texture a second time, one frame ahead and doing the interpolation in the vertex shader manually, something that you can probably afford.

To conclude on packing methods, there’s a third method of packing frame data in VATs, one that may be called **continuous** and one that may best utilize the empty pixels resulting either from the **one-frame-per-row** packing scheme if working with the constraint of having POT VATs, or from the **multiple-rows-per-frame** packing scheme if the texture width isn’t a divisor of the vertex count.

[img](Documentations/Images/)

In both cases, you might instead want to store one frame after the other and leave no empty pixel.

[img](Documentations/Images/)

This requires a more complex algorithm to generate the UVs with which to sample the VATs, one deemed experimental because it still needs to be battle tested to prove that it doesn’t suffer from 16bits or even 32bits precision issues. This **continuous** packing method makes the most of the VAT’s resolution and ensures data is tightly packed in POT textures.

## II. Data - UV VCol Data Baker

### II.I. Data - Intro


