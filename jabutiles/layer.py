from PIL import Image

from jabutiles.mask import Mask
from jabutiles.texture import Texture
from jabutiles.utils_img import cut_image



class Layer:
    def __init__(self,
            texture: Texture = None,
            mask: Mask = None,
        ) -> None:
        
        # At least one of them must be present
        if texture is None and mask is None:
            raise Exception("Must have at least one of them")
        
        self.texture: Texture = texture
        self.mask: Mask = mask
    
    @property
    def image(self) -> Image.Image:
        if self.mask is None:
            return self.texture.image
        
        if self.texture is None:
            return self.mask.image
        
        return cut_image(self.texture.image, self.mask.image)
    
