from typing import Literal

from PIL import Image

from jabutiles.mask import Mask
from jabutiles.texture import Texture



class Shade:
    def __init__(self,
            force: float = 1.0,
            offset: int | tuple[int, int] = 0,
            border: Literal["wrap", "bleed"] | None = None,
            outline: float = 0.0,
            dist: float = 1.0,
            inverted: bool = False,
        ) -> None:
        
        self.force: float = force
        self.offset: int | tuple[int, int] = offset
        self.border: Literal["wrap", "bleed"] = border
        self.outline: float = outline
        self.dist: float = dist
        self.inverted: bool = inverted
    
    def __str__(self) -> str:
        return f"SHADE | force:{self.force}"
    
    def apply(self,
            mask: Mask,
        ) -> Mask:
        
        shade_mask: Mask = mask.copy()
        
        # TODO: Implement dist for offsets too, not only outlines
        
        if self.inverted:
            shade_mask = shade_mask.invert()
        
        if self.outline > 0.0:
            shade_mask = shade_mask.outline(self.outline, dist=self.dist)
        
        if self.offset:
            shade_mask = shade_mask.offset(self.offset, self.border)
        
        # Selects only the differences between them
        # shade_mask = mask.diff(shade_mask)
        
        return shade_mask
    
    def stamp(self,
            texture: Texture,
            mask: Mask,
        ) -> Texture:
        
        shaded_texture = texture.brightness(self.force)
        shaded_mask = self.apply(mask)
        
        return texture.combine(shaded_texture, shaded_mask)


