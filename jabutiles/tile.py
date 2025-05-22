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
    
    # IMAGE OPERATIONS
    def overlay(self,
            head: "Tile",
            mask: "Mask" = None,
            alpha: float = 0.5,
        ) -> "Tile":
        # TODO: review
        """Merges two tiles into a new one.
        Must have a MASK or alpha value (default, 0.5).
        
        If using a MASK, it must have the same dimensions as both DATA Tiles.
        The pixel values from the MASK range from 0 (full base) to 255 (full head).
        
        The alpha value is used if no MASK is present.
        Its value is applied to the Tiles as a whole, not by pixel.
        
        Args:
            base (Tile): The Tile that goes on the bottom.
            head (Tile): The Tile that goes on top.
            mask (Tile, optional): A special Tile that controls how each pixel is merged. Defaults to None.
            alpha (float, optional): A value that controls how all pixels are merged. Defaults to 0.5.
        
        Returns:
            Tile: A new Tile resulting from the combination of both Tiles.
        """
        
        if mask is None:
            image = Image.blend(self.image, head.image, alpha)
            shape = self.shape
        
        else:
            image = Image.composite(head.image, self.image, mask.image)
            shape = mask.shape
        
        return Tile(image, shape)
    
