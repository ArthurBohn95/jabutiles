from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from jabutiles.shade import Shade

from PIL import Image, ImageOps

from jabutiles.mask import Mask, ShapeMask
from jabutiles.layer import Layer
from jabutiles.texture import Texture
from jabutiles.utils_img import cut_image, display_image



class Tile:
    """"""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            layers: list["Layer"],
            **params,
        ) -> None:
        
        self._layers: list["Layer"] = list(layers)
        self.__cache: Image.Image = None
    
    def __len__(self) -> int:
        return len(self._layers)
    
    def __str__(self) -> str:
        s = f"TILE | size:{len(self)}"
        for l in self._layers:
            s += f"\n  > {l}"
        return s
    
    # PROPERTIES # ------------------------------------------------------------
    @property
    def size(self) -> tuple[int, int]:
        return self._layers[0].size
    
    @property
    def image(self) -> Image.Image:
        if self.__cache is not None:
            print(f"Using cached image")
            return self.__cache
        
        if len(self._layers) == 1:
            return self._layers[0].image
        
        last_is_shape: bool = self._layers[-1].subtype == "mask"
        last_layer: int = len(self)
        if last_is_shape:
            last_layer -= 1
        
        image = Image.new("RGB", self.size, (0, 0, 0))
        
        for idx in range(0, last_layer):
            layer: "Layer" = self._layers[idx]
            
            shade = layer.on_other
            if shade is not None:
                image = shade.stamp(Texture(image), layer.mask).image
            
            image.paste(layer.image, mask=layer.mask.image)
        
        if last_is_shape:
            image = cut_image(image, self._layers[-1].mask.image)
        
        self.__cache = image
        
        return image
    
    # METHODS # ---------------------------------------------------------------
    # BASIC INTERFACES
    def display(self,
            factor: float = 1.0,
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> None:
        """Displays the Image on a python notebook."""
        
        display(ImageOps.scale(self.image, factor, resample)) # type: ignore
    
    # BASIC OPERATIONS
    def set_base(self,
            base: "Texture",
        ) -> None:
        
        # Clears any previous base layer
        if self._layers[0].subtype in ('base', 'full'):
            self._layers.pop(0)
        
        # Adds it at the front
        self._layers.insert(0, Layer(base))
        
        # Resets cache
        self.__cache = None
    
    def set_shape(self,
            mask: "ShapeMask",
        ) -> None:
        
        assert isinstance(mask, ShapeMask), "Mask is not a shape type"
        
        # Clears any previous shape layer
        if self._layers[-1].subtype == "mask":
            self._layers.pop(-1)
        
        # Adds it at the end
        self._layers.append(Layer(None, mask))
        
        # Resets cache
        self.__cache = None
    
