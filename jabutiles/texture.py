from typing import Self, Literal, TYPE_CHECKING
if TYPE_CHECKING:
    # Future Imports
    from jabutiles.tile import Tile
    from jabutiles.mask import Mask
    from jabutiles.layer import Layer
    from jabutiles.texture import Texture

import numpy as np
from PIL import Image, ImageEnhance

from jabutiles.base import BaseImage
from jabutiles.utils_img import cut_image



class Texture(BaseImage["Texture"]):
    """A Texture is a simple image."""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray,
            **params,
        ) -> None:
        # print("Texture.__init__")
        
        params["builder"] = Texture
        super().__init__(image, **params)
        
        # Ensures all textures are color channel
        self._image: Image.Image = self._image.convert('RGB')
    
    def __str__(self) -> str:
        return f"TEXTURE | size:{self.size} mode:{self.mode}"
    
    # METHODS # ---------------------------------------------------------------
    # BASIC OPERATIONS
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
    
    # OUTPUT OPERATIONS -------------------------------------------------------
    def combine(self,
            other: "Texture",
            mask: "Mask" = None,
            alpha: float = 0.5,
        ) -> "Texture":
        """
        """
        
        if mask is None:
            image = Image.blend(self.image, other.image, alpha)
        
        else:
            image = Image.composite(other.image, self.image, mask.image)
        
        return self.copy_with_params(image)
    
    def cutout(self,
            mask: "Mask",
        ) -> "Layer":
        
        from jabutiles.layer import Layer
        
        return Layer(self, mask)
    
    def overlay(self,
            head: "Texture",
            mask: "Mask" = None,
        ) -> list["Layer"]:
        
        from jabutiles.layer import Layer
        
        return [
            Layer(self, None),
            Layer(head, mask),
        ]
    
    # def shade(self,
    #         mask: "Mask",
    #         offset: tuple[int, int],
    #         brightness: float = 1.0,
    #         inverted: bool = False,
    #         offset_wrap: str = "wrap",
    #     ) -> "Tile":
        
    #     offset_mask = mask.offset(offset, offset_wrap).invert()
    #     base_adjusted = self.brightness(brightness)
        
    #     if inverted: # inverts which is overlaid on the other for double shades
    #         return self.combine(base_adjusted, offset_mask)
    #     else:
    #         return base_adjusted.combine(self, offset_mask)
    



class TextureGen:
    # TEXTURE GENERATORS # ----------------------------------------------------
    @staticmethod
    def random_rgb(
            size: int | tuple[int, int],
            ranges: list[tuple[int, int]],
            mode: Literal['minmax', 'avgdev'] = 'minmax',
        ) -> Texture:
        """ Generates a random RGB Texture from the channels ranges. """
        
        if isinstance(size, int):
            size = size, size
        else:
            size = size[1], size[0] # Yep, numpy is inverted
        
        match mode:
            case 'minmax':
                R = ranges[0][0], ranges[0][1]
                G = ranges[1][0], ranges[1][1]
                B = ranges[2][0], ranges[2][1]
            
            case 'avgdev':
                R = ranges[0][0] - ranges[0][1], ranges[0][0] + ranges[0][1]
                G = ranges[1][0] - ranges[1][1], ranges[1][0] + ranges[1][1]
                B = ranges[2][0] - ranges[2][1], ranges[2][0] + ranges[2][1]
        
        image = Image.fromarray(
            np.stack((
                np.random.randint(*R, size, np.uint8),
                np.random.randint(*G, size, np.uint8),
                np.random.randint(*B, size, np.uint8),
            ), axis=-1), 'RGB')
        
        return Texture(image)
    
    @staticmethod
    def named_texture(
            size: int | tuple[int, int],
            name: str,
            **params,
        ) -> Texture:
        
        if isinstance(size, int):
            size = (size, size)
        
        FULL_SIZE = size
        HALF_SIZE = size[0]//2, size[1]//2
        HALF_WIDTH = size[0]//2, size[1]
        QUARTER_HEIGHT = size[0], size[1]//4
        
        texture: Texture = None
        
        match name.lower():
            case 'grass':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((48, 64), (64, 108), (24, 32)))
                    .smooth(2)
                    .color(0.9)
                )
            case 'grass.dry' | 'path':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((80, 8), (80, 8), (24, 4)), 'avgdev')
                    .smooth(2)
                    .color(0.66)
                )
            case 'grass.wet' | 'moss':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((48, 4), (64, 4), (24, 4)), 'avgdev')
                )
            
            case 'water':
                texture = (TextureGen
                    .random_rgb(HALF_WIDTH,
                        ((24, 32), (32, 48), (80, 120)))
                    .scale((2, 1))
                    .smooth(1)
                    .smooth(1)
                )
            case 'water.shallow' | 'puddle':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((64, 8), (72, 8), (120, 12)), 'avgdev')
                    .smooth(1)
                    .smooth(1)
                )
            
            case 'dirt':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((140, 160), (100, 120), (64, 80)))
                    .smooth(2)
                )
            case 'dirt.wet' | 'mud':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((100, 6), (72, 6), (56, 4)), 'avgdev')
                    .smooth(1)
                )
            
            case 'sand':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((240, 255), (200, 220), (180, 192)))
                    .smooth(1)
                )
            case 'clay':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((108, 120), (64, 80), (48, 64)))
                    .smooth(2)
                )
            
            case 'stone':
                texture = (TextureGen
                    .random_rgb(HALF_SIZE,
                        ((100, 112), (100, 112), (100, 112)))
                    .scale(2, Image.Resampling.NEAREST)
                    .color(0.2)
                )
            case 'stone.raw' | 'gravel':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((96, 48), (96, 48), (96, 12)), 'avgdev')
                    .smooth(2)
                    .color(0.05)
                )
            case 'stone.smooth' | 'marble':
                texture = (TextureGen
                    .random_rgb(FULL_SIZE,
                        ((180, 4), (180, 8), (192, 16)), "avgdev")
                    .smooth(1)
                    .color(0.1)
                )
            
            case 'wood':
                texture = (TextureGen
                    .random_rgb(QUARTER_HEIGHT,
                        ((80, 8), (32, 6), (16, 4)), 'avgdev')
                    .scale((1, 4))
                    .smooth(3)
                    .contrast(0.666)
                    .color(0.75)        # 0.666
                    .brightness(1.1)    # 1.333  
                )
            
            # case '':
            #     return
            
            case _:
                texture = Texture()
        
        return texture
    
