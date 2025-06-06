from typing import Self, TYPE_CHECKING
if TYPE_CHECKING:
    from jabutiles.texture import Texture

from PIL import Image, ImageOps

from jabutiles.base import BaseImage
from jabutiles.configs import (
    Shape, Rotation, Reflection, ImageSource,
    SHAPES, ROTATIONS, REFLECTIONS, SHAPE_EDGE_INFO, SHAPE_EDGE_SIZE
)
from jabutiles.utils import shift_string, combine_choices
from jabutiles.utils_img import cut_image



class Mask(BaseImage["Mask"]):
    """A Mask is a greyscale alpha image"""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            image: ImageSource = None,
            **params,
        ) -> None:
        
        params.setdefault("builder", Mask)
        super().__init__(image, **params)
        
        # Ensures all masks are Luminance channel only
        self._image: Image.Image = self._image.convert('L')
        
        # print("Mask.__init__")
    
    def __str__(self) -> str:
        return f"MASK | size:{self.size} mode:{self.mode}"
    
    # METHODS # ---------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(builder=self._builder)
        return self._builder(image, **params)
    
    # EXPANDED OPERATIONS
    def invert(self) -> Self:
        """'invert' as in 'negative'"""
        
        image = ImageOps.invert(self._image)
        
        return self.copy_with_params(image)
    
    def merge(self,
            other: "Mask",
        ) -> Self:
        
        assert self.size == other.size, \
            f"Incompatible mask sizes: {self.size=} vs {other.size=}"
        
        base = self.as_array
        base |= other.as_array
        
        return self.copy_with_params(base)
    
    def diff(self, other: "Mask") -> "Mask":
        """The opposite of merge"""
        
        return self.merge(other.invert()).invert()
    
    # OUTPUT
    def cut(self,
            texture: "Texture",
        ) -> Image.Image:
        """Uses the mask to cut the texture. Returns an Image."""
        
        return cut_image(texture.image, self.image)



class ShapeMask(Mask):
    """A ShapeMask is a greyscale alpha image for defining Tile shapes"""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            image: ImageSource = None,
            shape: Shape = None,
            **params,
        ) -> None:
        
        params.setdefault("builder", ShapeMask)
        super().__init__(image, **params)
        
        assert shape in SHAPES, f"Unknown shape: {shape}"
        self._shape: Shape = shape
    
    def __str__(self) -> str:
        return f"SHAPEMASK | size:{self.size} mode:{self.mode} shape:{self.shape}"
    
    # PROPERTIES # ------------------------------------------------------------
    @property
    def shape(self) -> Shape:
        return self._shape
    
    # METHODS # ---------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(builder=self._builder, shape=self.shape)
        
        return self._builder(image, **params)
    
    def can_rotate(self,
            angle: Rotation,
        ) -> bool:
        
        if angle not in ROTATIONS:
            return False
        
        return angle in SHAPE_EDGE_INFO[self.shape]['rotation']
    
    def can_reflect(self,
            axis: Reflection,
        ) -> bool:
        
        if axis not in REFLECTIONS:
            return False
        
        return axis in SHAPE_EDGE_INFO[self.shape]['reflection']
    
    # BASIC OPERATIONS # ------------------------------------------------------
    def rotate(self,
            angle: Rotation,
            expand: bool = True,
        ) -> Self:
        
        if not self.can_rotate(angle):
            print(f"No rotation")
            return self
        
        return super().rotate(angle, expand)
    
    def reflect(self,
            axis: Reflection,
        ) -> Self:
        
        if not self.can_reflect(axis):
            print(f"No reflection")
            return self
        
        return super().reflect(axis)



class EdgeMask(ShapeMask):
    """An EdgeMask is a greyscale alpha image for border interaction"""
    
    # DUNDERS # ---------------------------------------------------------------
    def __init__(self,
            image: ImageSource = None,
            shape: Shape = None,
            edges: str = None,
            **params,
        ) -> None:
        
        assert shape in SHAPES, f"Unknown shape: {shape}"
        assert len(edges) == SHAPE_EDGE_SIZE[shape], f"Unknown edges: {edges}"
        
        params.setdefault("builder", EdgeMask)
        super().__init__(image, shape, **params)
        
        self._edges: str = edges
    
    def __str__(self) -> str:
        return f"SHAPEMASK | size:{self.size} mode:{self.mode}"\
            f" shape:{self.shape} edges:{self.edges}"
    
    # PROPERTIES # ------------------------------------------------------------
    @property
    def edges(self) -> str:
        return self._edges
    
    # METHODS # ---------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> Self:
        """Returns a deep copy but keeping the original parameters."""
        
        params = dict(builder=self._builder, shape=self.shape, edges=self.edges)
        
        return self._builder(image, **params)
    
    # BASIC OPERATIONS # ------------------------------------------------------
    def rotate(self,
            angle: Rotation,
            expand: bool = True,
        ) -> Self:
        
        if not self.can_rotate(angle):
            return self
        
        params = SHAPE_EDGE_INFO[self.shape]["rotation"]
        
        result = super().rotate(angle, expand)
        result._edges = shift_string(self.edges, *params)
        
        return result
    
    def reflect(self,
            axis: Reflection,
        ) -> Self:
        
        if not self.can_reflect(axis):
            return self
        
        params = SHAPE_EDGE_INFO[self.shape]["reflection"]
        
        result = super().reflect(axis)
        result._edges = shift_string(self._edges, *params)
        
        return result
    
    # EXPANDED OPERATIONS
    def merge(self,
            other: "EdgeMask",
        ) -> Self:
        
        assert self.size == other.size, \
            f"Incompatible edge mask sizes: {self.size=} vs {other.size=}"
        
        assert self.shape == other.shape, \
            f"Incompatible edge mask types: {self.shape=} vs {other.shape=}"
        
        result = super().merge(other)
        result._edges = combine_choices(self.edges, other.edges)
        
        return result

