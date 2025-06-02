from typing import Self, TYPE_CHECKING
if TYPE_CHECKING:
    from jabutiles.tile import Tile
    from jabutiles.mask import Mask

import numpy as np
from PIL import Image, ImageEnhance

from jabutiles.base import BaseImage



class Texture(BaseImage["Texture"]):
    """A Texture is a simple image."""
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray,
            **params,
        ) -> None:
        
        params["builder"] = Texture
        super().__init__(image, **params)
        
        # Ensures all textures are full channel
        self._image: Image.Image = self._image.convert('RGBA')
        
        # print("Texture.__init__")
    
    def __str__(self) -> str:
        return f"TEXTURE | size:{self.size} mode:{self.mode}"
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(builder=self._builder)
        # print(f"Texture.copy_with_params:\n{params=}")
        return self._builder(image, **params)
    
    # IMAGE OPERATIONS
    def brightness(self, factor: float = 1.0) -> Self:
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Brightness(self._image).enhance(factor)
        
        return self.copy_with_params(image)
    
    def color(self, factor: float = 1.0) -> Self:
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Color(self._image).enhance(factor)
        
        return self.copy_with_params(image)
    
    def contrast(self, factor: float = 1.0) -> Self:
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Contrast(self._image).enhance(factor)
        
        return self.copy_with_params(image)
    
    # TODO: review
    def overlay(self,
            head: "Texture",
            mask: "Mask" = None,
            alpha: float = 0.5,
        ) -> "Texture":
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
            image = Image.blend(self._image, head.image, alpha)
        
        else:
            image = Image.composite(head.image, self._image, mask.image)
        
        return self.copy_with_params(image)
    
    def shade(self,
            mask: "Mask",
            offset: tuple[int, int],
            brightness: float = 1.0,
            inverted: bool = False,
            wrapped: bool = True,
        ) -> "Tile":
        
        offset_mask = mask.offset(offset, wrapped).invert()
        base_adjusted = self.brightness(brightness)
        
        if inverted: # inverts which is overlaid on the other for double shades
            base_shaded = self.overlay(base_adjusted, offset_mask)
        else:
            base_shaded = base_adjusted.overlay(self, offset_mask)
        
        return base_shaded
    
    # OUTPUTS
    def cutout(self,
            mask: "Mask",
        ) -> "Tile":
        """Cuts a Texture to generate a Tile.
        
        Always returns a Tile.
        """
        
        from jabutiles.tile import Tile
        
        return Tile(self._image.copy(), mask)
    



class TextureGen:
    pass
