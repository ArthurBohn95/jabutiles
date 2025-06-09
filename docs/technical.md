# About the classes:

## `jabutiles.base.BaseImage`

This is the most basic class used by jabutiles.

It is nothing more than a `PIL.Image` wrapped around functional style methods.  
This means that each operation returns a copy with the applied change.

It is not used directly, but inherited by the other core classes.  
Provides most of the Image operations: rotation, reflection, cropping, ...

<br>



## `jabutiles.mask.Mask(BaseImage)`

This class inherits from the BaseImage.

It is used to represent a pure greyscale (`L mode`) mask.  
Used as an alpha for a `Texture` or to overlay two `Texture`s.

Fully procedural.

Adds new methods.

Has two specialized children:



### `jabutiles.mask.ShapeMask(Mask)`

A special `Mask` that also defines the shape of the Mask.

It's used to govern rotation and reflection operations, as well as the final `Tile` shape.

Fully procedural.

Can be:
- `orthogonal`: square (Pokemon up to GBA, Stardew Valley)
- `isometric`: diamond (Age of Empires II, Diablo II)
- `hexagonal`: `.flat` (?) or `.point` (Heroes of Might and Magic III)



### `jabutiles.mask.EdgeMask(ShapeMask)`

A special `ShapeMask` that also governs interactions with its surroundings.

Partially procedural.

<br>



## `jabutiles.texture.Texture(BaseImage)`

This class inherits from the BaseImage.

It is used to represent pure RGB visual data.  
Usually generated in-code or loaded from an image file.

Adds new methods.

<br>



## `jabutiles.shade.Shade`

A collection of parameters to apply a "shadow" onto a `Texture`.

The shape is controlled by a `Mask`.

<br>



## `jabutiles.layer.Layer`

A combination of a `Texture`, a `Mask` and one/two `Shade`s.  

If only Texture, it's regarded as a base Texture.  
If only ShapeMask, it's regarded as a Shape cutter.  
If both exist, the Mask is the Texture's alpha.  

<br>



## `jabutiles.tile.Tile`

A collection of (at least one) `Layer`s.  
If only one, it MUST contain a `Texture`.

Usually follows this pattern:
```py
[
  Layer(Texture, None),           # 1. Base Layer, the Texture is the base
  Layer(Texture, Mask, Shade),    # 2. Detail Layer, overlays information
  ...                             #    Mask has no Shape nor Edges, is usually a pattern
  Layer(Texture, EdgeMask, Shade) # 3. Edges Layer, defines how to interact with neighbours
  ...                             #    Can be more than one if surrounded by different Textures
  Layer(None,    ShapeMask),      # 4. Shape Layer, defines the final appearance
]
```

Exporting the resulting Image means stacking up the layers.


