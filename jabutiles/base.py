from typing import TypeVar, Generic, Literal
import random as rnd

import numpy as np
from PIL import Image, ImageOps, ImageFilter

from jabutiles.utils import coalesce
from jabutiles.utils_img import get_outline
from jabutiles.configs import Rotation, Reflection, REFLECTIONS



B = TypeVar('B', bound='BaseImage')
class BaseImage(Generic[B]):
    """A Base form of the PIL.Image.
    Encapsulates methods used by tilers.
    """
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            **params,
        ) -> None:
        """
        Can receive an Image:
            - From a path (str)
            - From another Image (copy)
            - From raw data (np.array)
        """
        # print("BaseImage.__init__")
        
        self._builder = params.get("builder", BaseImage)
        self._image: Image.Image
        
        if isinstance(image, Image.Image):
            self._image = image
        
        elif isinstance(image, str):
            self._image = Image.open(image)
        
        elif isinstance(image, np.ndarray):
            self._image = Image.fromarray(image)
        
        else:
            # A magenta pixel
            self._image = Image.new('RGB', (1, 1), (255, 0, 255))
            # raise Exception(f"wtf")
    
    def __str__(self) -> str:
        return f"BASE | size:{self.size} mode:{self.mode}"
    
    def __repr__(self) -> str:
        try:
            display(self._image) # type: ignore
        
        finally:
            return self.__str__()
    
    # PROPERTIES # -------------------------------------------------------------
    @property
    def image(self) -> Image.Image:
        return self._image
    
    @property
    def mode(self) -> str:
        return self._image.mode
    
    @property
    def size(self) -> tuple[int, int]:
        return self._image.size
    
    @property
    def width(self) -> int:
        return self.size[0]
    
    @property
    def height(self) -> int:
        return self.size[1]
    
    @property
    def as_array(self) -> np.typing.NDArray:
        """Returns the Tile as a numpy array.
        Useful for matrix operations.
        
        Returns:
            np.ndarray: The numpy array.
        """
        
        return np.array(self._image)
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy(self) -> B:
        """Returns a deep copy."""
        
        return self._builder(self._image.copy(), builder=self._builder)
    
    def copy_with_params(self,
            image: Image.Image,
        ) -> B:
        """Returns a deep copy but keeping the original parameters."""
        
        return self._builder(image, builder=self._builder)
    
    def display(self,
            factor: float = 1.0,
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> None:
        """Displays the Image on a python notebook."""
        
        display(ImageOps.scale(self.image, factor, resample)) # type: ignore
    
    def save(self, path: str) -> None:
        self.image.save(path)
    
    # IMAGE OPERATIONS
    def rotate(self, # VALIDATED
            angle: Rotation,
            expand: bool = True,
        ) -> B:
        """Rotates the Image counter clockwise.
        
        Args:
            angle (int): How many degrees to rotate CCW.
            expand (bool, optional): If the image resizes to acommodate the rotation. Defaults to True.
        
        Returns:
            The rotated Image
        """
        
        if angle == 0:
            return self
        
        image = self._image.rotate(int(angle), expand=expand)
        
        return self.copy_with_params(image)
    
    def reflect(self, # VALIDATED
            axis: Reflection,
        ) -> B:
        """Mirrors the Image in the horizontal, vertical or diagonal directions.  
        
        Args:
            `axis`, one of:
            - `x`, top <-> bottom, on horizontal axis
            - `y`, left <-> right, on vertical axis
            - `p`, top left <-> bottom right, on diagonal x=y axis (positive)
            - `n`, bottom left <-> top right, on diagonal x=-y axis (negative)
        
        Returns:
            The mirrored Image.
        """
        
        if axis not in REFLECTIONS:
            return self
        
        match axis:
            case 'x': image = ImageOps.flip(self._image)
            case 'y': image = ImageOps.mirror(self._image)
            case 'p': image = self._image.transpose(Image.Transpose.TRANSVERSE)
            case 'n': image = self._image.transpose(Image.Transpose.TRANSPOSE)
        
        return self.copy_with_params(image)
    
    def scale(self, # VALIDATED
            factor: float | tuple[float, float],
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> B:
        """'scale' as in 'stretch by factor(x,y) or factor(s)'"""
        
        if isinstance(factor, (int, float)):
            image = ImageOps.scale(self._image, factor, resample)
        
        elif isinstance(factor, tuple):
            w, h = self.size
            newsize = (int(w * factor[0]), int(h * factor[1]))
            image = self._image.resize(newsize, resample)
        
        else:
            # print(f"Strange parameters")
            image = self._image.copy()
        
        return self.copy_with_params(image)
    
    def crop(self, # VALIDATED
            box: tuple[int, int, int, int],
        ) -> B:
        """Removes the border around the bounding box.  
        Order: (left, top, right, bottom)."""
        
        image = self._image.crop(box)
        
        return self.copy_with_params(image)
    
    def take(self, # VALIDATED
            pos: tuple[int, int],
            size: tuple[int, int],
        ) -> B:
        """Similar to crop but accepts wrapping values."""
        
        x0, y0 = pos
        width, height = size
        wrap_width, wrap_height = self.size
        
        xidx = (np.arange(x0, x0+width)  % wrap_width)
        yidx = (np.arange(y0, y0+height) % wrap_height)
        
        crop = self.as_array[np.ix_(yidx, xidx)]
        
        return self.copy_with_params(crop)
    
    def offset(self, # VALIDATED
            offset: int | tuple[int, int],
            how: Literal[None, 'wrap', 'bleed'] = None,
        ) -> B:
        """'Slides' the texture by the offset amount."""
        
        if isinstance(offset, int):
            offset = offset, offset
        
        match how:
            case "wrap":
                width, height = self.size
                offx, offy = offset
                
                posx = (width - offx) % width
                posy = (height - offy) % height
                
                return self.take((posx, posy), self.size)
            
            case "bleed":
                pad = max(abs(offset[0]), abs(offset[1]))
                offset = pad - offset[0], pad - offset[1]
                return self.bleed(pad).take(offset, self.size)
            
            case _:
                image = Image.new(self.mode, self.size, "black")
                image.paste(self._image, offset)
                
                return self.copy_with_params(image)
    
    def bleed(self, # VALIDATED
            pad: int = 0,
        ) -> B:
        """A special type of padding, where the edge pixels are repeated"""
        
        array = self.as_array
        
        # Determine padding shape
        if array.ndim == 2:  # Grayscale 'L'
            pad_width = ((pad, pad), (pad, pad))
        elif array.ndim == 3:  # 'RGB', 'RGBA', or 'LA'
            pad_width = ((pad, pad), (pad, pad), (0, 0))
        
        padded = np.pad(array, pad_width, mode='edge')
        image = Image.fromarray(padded, mode=self.mode)
        
        return self.copy_with_params(image)
    
    def smooth(self, # VALIDATED
            level: int = 1,
            wrap: bool = True,
            pad: int = 4,
        ) -> B:
        
        FILTERS = {
            -1: ImageFilter.SHARPEN,
            1 : ImageFilter.SMOOTH,
            2 : ImageFilter.SMOOTH_MORE,
            3 : ImageFilter.BLUR,
        }
        
        if level not in FILTERS:
            return self
        
        w, h = self.size
        
        if wrap:
            # Pads the image with itself to avoid filter bleeding
            image = self.take((w-pad, h-pad), (w+pad*2, h+pad*2)).image
        
        else:
            # Pads the image with edge repetition
            image = self.bleed(pad).image
        
        # Applies the filter
        image = image.filter(FILTERS[level])
        
        # Crops the extra border, restoring the original size
        image = ImageOps.crop(image, pad)
        
        return self.copy_with_params(image)
    
    # ADVANCED OPERATIONS
    def outline(self, # VALIDATED
            thickness: float = 1.0,
            color: str | tuple[int, int, int] = "white",
            combine: bool = True,
            dist: float = 1.0,
        ) -> B:
        
        base_image = self.image.copy()
        outline = get_outline(base_image, thickness, color, dist)
        
        if combine:
            base_image.paste(outline, mask=outline)
        
        return self.copy_with_params(base_image)
    
    def repeat(self, # VALIDATED
            size: tuple[int, int],
            mirrors: list[str] = None,
            rotations: list[int] = None,
        ) -> B:
        
        # Simple repetition without changes
        if rotations is None and mirrors is None:
            return self.take((0, 0), size)
        
        mirrors = coalesce(mirrors, list)
        rotations = coalesce(rotations, list)
        
        base: Image.Image = Image.new(self.mode, size)
        
        W, H = self.size
        for row in range(0, size[1], H):
            for col in range(0, size[0], W):
                r = rnd.choice(rotations)
                m = rnd.choice(mirrors)
                
                image = self.rotate(r).reflect(m).image
                base.paste(image, (col, row))
        
        return self.copy_with_params(base)
    

