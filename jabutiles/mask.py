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
            # shape: Shapes = None,
            # edges: str = None,
            **params,
        ) -> None:
        
        params["builder"] = Mask
        super().__init__(image, **params)
        
        # Ensures all masks are Luminance channel only
        self._image = self._image.convert('L')
        
        # self.edges: str = edges # .replace('x', '.') # TODO: autodetect
        
        # print("Mask.__init__")
    
    def __str__(self) -> str:
        return f"MASK | size:{self.size} mode:{self.mode}"
    
    # STATIC METHODS # ---------------------------------------------------------
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
        
        params = dict(builder=self._builder)
        # print(f"Mask.copy_with_params:\n{params=}")
        return self._builder(image, **params)
    
    # IMAGE OPERATIONS
    def invert(self) -> Self:
        """'invert' as in 'negative'"""
        
        image = ImageOps.invert(self._image)
        
        return self.copy_with_params(image)
    
    # OUTPUTS
    def cutout(self,
            mask: "Mask",
        ) -> "Mask":
        """Think of 'cutout' as in 'cookie cutter'.  
        Cuts a Texture to generate a Tile.
        
        Always returns a Mask.
        """
        
        image = super().cutout(mask.image)
        
        return self.copy_with_params(image)
    



class MaskGen:
    pass
