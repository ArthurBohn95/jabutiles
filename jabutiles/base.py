from typing import TypeVar, Generic, Literal

import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageChops, ImageFilter, ImageEnhance

from jabutiles.utils import coalesce, clamp

B = TypeVar('B', bound='BaseImage')



class BaseImage(Generic[B]):
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            **params,
        ) -> None:
        
        self._builder = params.get("builder", BaseImage)
        self.image: Image.Image
        
        if isinstance(image, Image.Image):
            self.image = image
        
        elif isinstance(image, str):
            self.image = Image.open(image)
        
        elif isinstance(image, np.ndarray):
            self.image = Image.fromarray(image)
        
        else:
            # A magenta dot
            self.image = Image.new('RGB', (1, 1), (255, 0, 255))
        
        # print("BaseImage.__init__")
    
    def __str__(self) -> str:
        return f"BASE | size:{self.size} mode:{self.mode}"
    
    def __repr__(self):
        try:
            display(self.image) # type: ignore
        
        finally:
            return self.__str__()
    
    # PROPERTIES # -------------------------------------------------------------
    @property
    def mode(self) -> str:
        return self.image.mode
    
    @property
    def size(self) -> tuple[int, int]:
        return self.image.size
    
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
        
        return np.array(self.image)
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy(self) -> B:
        """Returns a deep copy."""
        
        return self._builder(self.image.copy(), builder=self._builder)
    
    def copy_with_params(self,
            image: Image,
        ) -> B:
        """Returns a deep copy but keeping the original parameters."""
        
        # print("BaseImage.copy_with_params")
        
        return self._builder(image, builder=self._builder)
    
    def display(self,
            factor: float = 1.0,
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> None:
        """Displays the Image on a python notebook."""
        
        display(ImageOps.scale(self.image, factor, resample)) # type: ignore
    
    # IMAGE OPERATIONS
    def rotate(self,
            angle: int,
            expand: bool = True,
        ) -> B:
        """Rotates the Image counter clockwise.
        
        Args:
            angle (int): How many degrees to rotate CCW.
            expand (bool, optional): If the image resizes to acommodate the rotation. Defaults to True.
        
        Returns:
            The rotated Image
        """
        
        image = self.image.rotate(int(angle), expand=expand)
        
        return self.copy_with_params(image)
    
    def mirror(self,
            axis: Literal['x', 'y', 'p', 'n'],
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
        
        match axis:
            case 'x': image = ImageOps.flip(self.image)
            case 'y': image = ImageOps.mirror(self.image)
            case 'p': image = self.image.transpose(Image.Transpose.TRANSVERSE)
            case 'n': image = self.image.transpose(Image.Transpose.TRANSPOSE)
            case _:   image = self.image.copy()
        
        return self.copy_with_params(image)
    
    def scale(self,
            factor: float | tuple[float, float],
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> B:
        """'scale' as in 'stretch by factor(x,y) or factor(s)'"""
        
        if isinstance(factor, (int, float)):
            image = ImageOps.scale(self.image, factor, resample)
        
        elif isinstance(factor, tuple):
            w, h = self.size
            newsize = (int(w * factor[0]), int(h * factor[1]))
            image = self.image.resize(newsize, resample)
        
        else:
            # print(f"Strange parameters")
            image = self.image.copy()
        
        return self.copy_with_params(image)
    
    def crop(self,
            box: tuple[int, int, int, int],
        ) -> B:
        """Removes the border around the bounding box.  
        Order: (left, top, right, bottom)."""
        
        image = self.image.crop(box)
        
        return self.copy_with_params(image)
    
    def take(self,
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
    
    def offset(self,
            offset: tuple[int, int],
            wrap: bool = True,
        ) -> B:
        """'Slides' the texture by the offset amount."""
        
        if wrap:
            width, height = self.size
            offx, offy = offset
            
            posx = (width - offx) % width
            posy = (height - offy) % height
            
            return self.take((posx, posy), self.size)
        
        else:
            base_image = Image.new(self.mode, self.size, "black")
            base_image.paste(self.image, offset)
            
            return self.copy_with_params(base_image)
    
    def filter(self,
            filters: ImageFilter.Filter | list[ImageFilter.Filter],
            pad: int = 4,
        ) -> B:
        
        w, h = self.size
        
        # Pads the image with itself to avoid filter bleeding
        image = self.take((w-pad, h-pad), (w+pad*2, h+pad*2)).image
        
        filters = coalesce(filters, list)
        for f in filters:
            image = image.filter(f)
        
        # Crops the extra border, restoring the original size
        image = ImageOps.crop(image, pad)
        
        return self.copy_with_params(image)
    
    # ADVANCED OPERATIONS
    def outline(self,
            thickness: float = 1.0,
            color: str | tuple[int, int, int] = "white",
            combine: bool = True,
        ) -> B:
        
        ref_image = self.image.convert("RGBA")
        base_image = Image.new(ref_image.mode, ref_image.size, (0, 0, 0, 0))
        canvas = ImageDraw.Draw(base_image)
        
        # Ensures thickness is always at least 1
        T = clamp(thickness, (1, 1000))
        W, H = ref_image.size
        edge = ref_image.filter(ImageFilter.FIND_EDGES).load()
        
        for x in range(W):
            for y in range(H):
                if not edge[x,y][3]:
                    continue
                
                if T % 1 == 0: # 1, 2, 3, ...round corners
                    canvas.ellipse((x-T, y-T, x+T, y+T), fill=color)
                
                else: # 1.5, 2.5, 3.5, ... square corners
                    canvas.rectangle((x-T+0.5, y-T+0.5, x+T-0.5, y+T-0.5), fill=color)
        
        if combine:
            base_image.paste(ref_image, mask=ref_image)
        
        else:
            alpha = ImageEnhance.Brightness(ref_image).enhance(256)
            base_image = ImageChops.subtract(base_image, alpha)
        
        return self.copy_with_params(base_image)
    
