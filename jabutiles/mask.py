from typing import Self, Sequence

import numpy as np
from PIL import Image, ImageOps, ImageDraw #, ImageChops, ImageFilter, ImageEnhance

from jabutiles.base import BaseImage
from jabutiles.utils import combine_choices
from jabutiles.configs import Shapes



class Mask(BaseImage["Mask"]):
    """A Mask is a special 'Tile' with a shape and orientation"""
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            shape: Shapes = None,
            edges: str = None,
            **params,
        ) -> None:
        
        params["builder"] = Mask
        super().__init__(image, **params)
        
        # Ensures all masks are Luminance channel only
        self.image = self.image.convert('L')
        
        self.shape: Shapes = shape if shape is not None else 'ort'
        self.edges: str = edges # .replace('x', '.') # TODO: autodetect
        
        # print("Mask.__init__")
    
    def __str__(self) -> str:
        return f"MASK | size:{self.size} mode:{self.mode} shape:{self.shape} edges:{self.edges}"
    
    # STATIC METHODS # ---------------------------------------------------------
    @staticmethod
    def _create_symmetrical_outline(
            size: tuple[int, int],
            lines: list[tuple[tuple[float]]],
            fill: bool = True,
            **params,
        ) -> Image.Image:
        
        image = Image.new("L", size, 0)
        draw  = ImageDraw.Draw(image)
        
        for line in lines:
            draw.line(line, fill=255)
        
        image.paste(ImageOps.flip(image), mask=ImageOps.invert(image))
        image.paste(ImageOps.mirror(image), mask=ImageOps.invert(image))
        
        if fill:
            ImageDraw.floodfill(image, (size[0] / 2, size[1] / 2), 255)
        
        return image
    
    @staticmethod
    def merge_masks(
            masks: Sequence["Mask"] | dict[str, "Mask"],
            **params,
        ) -> "Mask":
        
        assert len(masks) >= 2, "Insufficient masks to be merged (<2)"
        
        if isinstance(masks, Sequence):
            base = masks[0].as_array
            
            for mask in masks[1:]:
                base |= mask.as_array
            
            return Mask(base, masks[-1].shape)
        
        if isinstance(masks, dict):
            mask_data = masks.copy()
            base_edge, base_mask = mask_data.popitem()
            
            # Iterates and combines them
            for edge, mask in mask_data.items():
                base_edge = combine_choices(base_edge, edge)
                base_mask = Mask.merge_masks([base_mask, mask])
            
            return base_edge, base_mask
        
        return None
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(shape=self.shape, edges=self.edges, builder=self._builder)
        # print(f"Mask.copy_with_params:\n{params=}")
        return self._builder(image, **params)
    
    # IMAGE OPERATIONS
    def invert(self) -> Self:
        """'invert' as in 'negative'"""
        
        image = ImageOps.invert(self.image)
        
        return self.copy_with_params(image)
    



class MaskGen:
    pass
