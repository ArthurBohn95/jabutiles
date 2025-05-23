from typing import Self, TYPE_CHECKING
if TYPE_CHECKING:
    from jabutiles.mask import Mask

import numpy as np
from PIL import Image

from jabutiles.configs import Shapes
from jabutiles.texture import Texture



class Tile(Texture):
    """A Tile is a Texture with a purpose and a shape.  
    Can be thought as the combination of Texture + Mask.
    """
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            shape: Shapes = None,
            **params,
        ) -> None:
        
        params["builder"] = Tile
        super().__init__(image, **params)
        
        # Ensures all tiles are full channel
        self.image: Image.Image = self.image.convert('RGBA')
        
        self.shape: Shapes = shape if shape is not None else 'ort'
        
        # print("Tile.__init__")
    
    def __str__(self) -> str:
        return f"TILE | size:{self.size} mode:{self.mode} shape:{self.shape}"
    
    # STATIC METHODS # ---------------------------------------------------------
    @staticmethod
    def merge_tiles(*tiles: tuple["Texture", "Mask"]) -> "Tile":
        """
        tiles = [(tile, mask), (tile, mask), ...]
        """
        assert len(tiles) >= 2
        
        FIRST: tuple["Texture", "Mask"] = tiles[0]
        LAST: tuple["Texture", "Mask"] = tiles[-1]
        
        first_no_mask: bool = FIRST[1] is None
        last_is_cut: bool = LAST[0] is None
        
        start_at: int = 0
        end_at: int = len(tiles)
        
        # If the last tuple is just the mask, do the cutout
        if last_is_cut:
            end_at = end_at - 1
        
        if first_no_mask: # The first texture is used in full
            start_at = 1
            image = tiles[0][0].image.copy()
        
        else: # A black template is used
            image = Image.new('RGBA', FIRST[0].size, (0, 0, 0, 0))
        
        # Iterative pasting
        shape: Shapes = "ort"
        for tile, mask in tiles[start_at:end_at]:
            image.paste(tile.image, mask=mask.image)
            shape = mask.shape
        
        tile = Tile(image, shape)
        
        if last_is_cut:
            tile = tile.cutout(LAST[1])
        
        return tile
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(shape=self.shape, builder=self._builder)
        # print(f"Mask.copy_with_params:\n{params=}")
        return self._builder(image, **params)
    
