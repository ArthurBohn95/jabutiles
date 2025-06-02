# jabutiles
A 2D Tile library for python.

Most of the backend is pillow (PIL fork), the rest is numpy.

<br> <br> <br> <br> <br>

# About the classes:

## `jabutiles.base.BaseImage`

This is the most basic class used by jabutiles.

It is nothing more than a PIL.Image wrapped around functional style methods.  
This means that each operation returns a copy of the class with the change.

It is not used directly, but inherited by the other core classes.  
Provides most of the Image operations: rotation, mirroring, cropping, ...

<br>


## `jabutiles.mask.Mask (BaseImage)`

This class inherits from the BaseImage.

It is used to represent a pure L mask.  
Used as an alpha for a Texture or to overlay two Textures.

Can have additional components:

### `jabutiles.shape.Shape`

A class that defines what is the purpose of the Mask.

It's used to govern rotation and reflection operations.

Can be:
- `orthogonal`: square (GB/GBC/GBA Pokemon, Stardew Valley)
- `isometric`: diamond (Age of Empires II, Diablo II)
- `hexagonal`: both `flat` (?) and `point` (Heroes of Might and Magic III)

### `jabutiles.edges.Edges`

A class that governs how the Mask interacts with surrounding Masks.

Adds new methods:
- `invert`: Inverts the grayscale values (0 <-> 255)

<br>

## `jabutiles.texture.Texture (BaseImage)`

This class inherits from the BaseImage.

It is used to represent pure RGB(A) visual data, such as a Texture.  
Usually generated in-code or loaded from an image file.

Adds new methods:


<br>

## `jabutiles.layer.Layer`

A combination of a Texture and/or a Mask.  
Must have at least one of them present.

If both exist, the Mask is the Texture's alpha.  
If only Texture, it's regarded as a base Texture.  
If only Mask, it's regarded as a Shape cutter.

<br>

## `jabutiles.tile.Tile`

A collection of Layers (at least one).  
If only one layer, MUST contain a Texture.

Usually follows this pattern:
```py
[
  (Texture, None),        # 1. Base Layer, the Texture is the base
  (Texture, Mask),        # 2. Detail Layer, overlays information
  ...                     # Mask has no Shape nor Edges, is usually a pattern
  (Texture, Mask(Edges))  # 3. Edges Layer, defines how to interact with neighbours
  ...                     # Can be more than one if surrounded by different Textures
  (None,    Mask(Shape)), # 4. Shape Layer, defines the final appearance
]
```

Exporting the resulting Image means stacking up the layers.



