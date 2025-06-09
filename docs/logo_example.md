This is how the logo was generated.

# Setup

``` python
# Imports
from jabutiles.tile import Tile
from jabutiles.layer import Layer
from jabutiles.shade import Shade
from jabutiles.maskgen import MaskGen, ShapeMaskGen
from jabutiles.texture import Texture, TextureGen
from jabutiles.utils_img import display_image

# Constants
SCALE = 8       # Scale to display and export the image
S     = 24      # Generic dimension for the textures and masks
SIZE  = (S, S)
FORCE = 0.8     # Shade brightness
```

# Textures

``` python
# Textures
tx1 = TextureGen.named_texture(SIZE, "dirt")
tx2 = TextureGen.named_texture(SIZE, "gravel")
tx3 = TextureGen.named_texture(SIZE, "grass")
```

| `tx1` | `tx2` | `tx3` |
|-----|-----|-----|
| ![tx1](imgs/tx1_dirt.png) | ![tx2](imgs/tx2_gravel.png) | ![tx3](imgs/tx3_grass.png) |

# Masks

``` python
# Masks
mk1 = MaskGen.brick_pattern(SIZE, (10, 10), 2, 1).offset((-1, -1), "wrap") # A brick path
mk2 = MaskGen.blob_draw(SIZE, [((S/2-0.5, S/2-0.5), S/2-4.5)]).invert()    # A centered circle
mk3 = ShapeMaskGen.hexagonal(SIZE)                                         # A hexagonal ShapeMask
```

| `mk1` | `mk2` | `mk3` |
|-----|-----|-----|
| ![mk1](imgs/mk1_brick.png) | ![mk2](imgs/mk2_blob.png) | ![mk3](imgs/mk3_shape.png) |

# Shades

``` python
# Shades
sh1 = Shade(1/FORCE, (-1, +1), "wrap", inverted=True)   # Bright corner
sh2 = Shade(FORCE, (-1, +1), "wrap")                    # Brick shadow
sh3 = Shade(FORCE, outline=2, dist=0.5, inverted=True)  # Enhance border
sh4 = Shade(FORCE, outline=2)                           # Occlusion
```

# Layers

``` python
# Layers
ly1 = Layer(tx1, None)          # Base dirt texture, no mask
ly2 = Layer(tx2, mk1, sh1, sh2) # Stone brick over dirt
ly3 = Layer(tx3, mk2, sh3, sh4) # Grass growth over bricks
ly4 = Layer(None, mk3)          # Hexagonal tile cut
```

| `ly1` | `ly2` | `ly3` | `ly4` |
|-----|-----|-----|-----|
| ![ly1](imgs/ly1_dirt.png) | ![ly2](imgs/ly2_path.png) | ![ly3](imgs/ly3_growth.png) | ![mk3](imgs/mk3_shape.png) |

## Interactions

| `ly1 + ly2` | `ly2 + ly3` | `ly1 + ly2 + ly3` |
|-------------|-------------|-------------|
| ![ly1_2](imgs/ly1_2.png) | ![ly2_3](imgs/ly2_3.png) | ![ly1_2_3](imgs/ly1_2_3.png) |

Shades are only cast during Layer interaction.  
Ex: The bricks only cast a shadow on the dirt when overlaid.
The only prior shade is on the brick itself, a bright corner (`sh1`)

# Tile

``` python
# Tile
tl1 = Tile([ly1, ly2, ly3, ly4]) # All 4 layers combined
```

# Final Result

``` python
display_image(tl1.image, SCALE)
```

![tl1](imgs/logo.png)
