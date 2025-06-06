from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from jabutiles.mask import Mask

from PIL import Image

from jabutiles.shade import Shade
from jabutiles.texture import Texture
from jabutiles.maskgen import ShapeMaskGen
from jabutiles.utils_img import cut_image

# TODO: Add possibility to have more than 1 shades on self and others

class Layer:
    """"""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            texture: "Texture" = None,
            mask: "Mask" = None,
            on_self: "Shade" = None,
            on_other: "Shade" = None,
            # shade: "Shade" = None,
        ) -> None:
        
        # At least one of them must be present
        if texture is None and mask is None:
            raise Exception("Must have at least one of them")
        
        if texture is not None and mask is None:
            mask: "Mask" = ShapeMaskGen.orthogonal(texture.size)
        
        self.texture: "Texture" = texture
        self.mask: "Mask" = mask
        # self._shade: "Shade" = shade
        
        self.on_self: "Shade" = on_self
        self.on_other: "Shade" = on_other
    
    def __str__(self) -> str:
        return f"LAYER | subtype:{self.subtype}"
    
    def __repr__(self) -> str:
        try:
            display(self.image) # type: ignore
        
        finally:
            return self.__str__()
    
    # PROPERTIES # ------------------------------------------------------------
    @property
    def is_complete(self) -> bool:
        return self.texture is not None and self.mask is not None
    
    @property
    def is_shaded(self) -> bool:
        return self.on_self is not None or self.on_other is not None
    
    @property
    def subtype(self) -> str:
        from jabutiles.mask import EdgeMask
        
        if self.is_complete:
            if isinstance(self.mask, EdgeMask):
                return "edge"
            else:
                return "full"
        elif self.texture is not None:
            return "base"
        elif self.mask is not None:
            return "mask"
        else:
            return None
    
    @property
    def image(self) -> Image.Image:
        if self.mask is None:
            return self.texture.image
        
        if self.texture is None:
            return self.mask.image
        
        if self.on_self is not None:
            return self.on_self.stamp(self.texture, self.mask).image
        
        return cut_image(self.texture.image, self.mask.image)
    
    @property
    def size(self) -> tuple[int, int]:
        if self.texture is not None:
            return self.texture.size
        
        if self.mask is not None:
            return self.mask.size
    
    @property
    def as_texture(self) -> "Texture":
        return Texture(self.image)
