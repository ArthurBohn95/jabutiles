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
            image: str | Image.Image | np.typing.NDArray = None,
            **params,
        ) -> None:
        
        params["builder"] = Texture
        super().__init__(image, **params)
        
        # Ensures all textures are full channel
        self.image = self.image.convert('RGBA')
        
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
        
        image = ImageEnhance.Brightness(self.image).enhance(factor)
        
        return self.copy_with_params(image)
    
    def color(self, factor: float = 1.0) -> Self:
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Color(self.image).enhance(factor)
        
        return self.copy_with_params(image)
    
    def contrast(self, factor: float = 1.0) -> Self:
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Contrast(self.image).enhance(factor)
        
        return self.copy_with_params(image)
    
    def cutout(self,
            mask: "Mask",
        ) -> "Tile":
        """Think of 'cutout' as in 'cookie cutter'.  
        Cuts a Texture to generate a Tile.
        """
        from jabutiles.tile import Tile
        
        image = self.image.copy()
        image.putalpha(mask.image)
        
        return Tile(image, mask.shape)



class TextureGen:
    pass
