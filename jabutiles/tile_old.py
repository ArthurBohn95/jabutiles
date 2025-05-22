from typing import Literal

import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageChops, ImageFilter, ImageEnhance

from jabutiles.utils import coalesce, clamp
from jabutiles.configs import Shapes



class Tile:
    """
    A `Tile` is a `PIL.Image` wrapped around common image operations.
    
    All methods return a new copy and do not alter the original Image.
    """
    
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            ref: str | Image.Image | np.typing.NDArray = None,
            shape: Shapes = None,
        ) -> None:
        """The base Tile class for tiling operations
        
        Returns:
            Tile: A PIL.Image wrapped around tiling methods
        """
        
        self.image: Image.Image
        
        if isinstance(ref, Image.Image):
            self.image = ref
        
        elif isinstance(ref, str):
            self.image = Image.open(ref)
        
        elif isinstance(ref, np.ndarray):
            self.image = Image.fromarray(ref)
        
        else:
            self.image = Image.new('RGB', (1, 1), (255, 0, 255))
        
        if shape is None:
            shape = 'ort'
        
        self.shape: str = shape
    
    def __repr__(self):
        try:
            display(self.image) # type: ignore
        
        finally:
            print(f"size:{self.size} mode:{self.mode}")
    
    # PROPERTIES # -------------------------------------------------------------
    @property
    def mode(self) -> str:
        return self.image.mode
    
    @property
    def size(self) -> tuple[int, int]:
        return self.image.size
    
    @property
    def center(self) -> tuple[float, float]:
        size = self.size
        return size[0]/2, size[1]/2
    
    # @property
    # def as_mask(self) -> "Mask":
    #     """Converts the Tile to a Mask (only L channel).
    #     Useful to ensure a mask is indeed a mask.
        
    #     Returns:
    #         Mask: The converted Tile to Mask.
    #     """
        
    #     return Mask(self.image.convert('L'))
    
    @property
    def as_array(self) -> np.typing.NDArray:
        """Returns the Tile as a numpy array.
        Useful for matrix operations.
        
        Returns:
            np.ndarray: The numpy array.
        """
        
        return np.array(self.image)
    
    # METHODS # ----------------------------------------------------------------
    # BASICS
    def copy(self, image: Image = None) -> "Tile":
        if image is None:
            image = self.image.copy()
        
        return Tile(image, self.shape)
    
    def display(self,
            factor: float = 1.0,
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> None:
        
        display(ImageOps.scale(self.image, factor, resample)) # type: ignore
    
    # IMAGE DATA OPERATIONS
    def invert(self) -> "Tile":
        """'invert' as in 'negative'"""
        
        image = ImageOps.invert(self.image)
        
        return Tile(image, self.shape)
    
    def filter(self,
            filters: ImageFilter.Filter | list[ImageFilter.Filter],
            pad: int = 4,
        ) -> "Tile":
        
        w, h = self.size
        
        # Pads the image with itself to avoid filter bleeding
        image = self.take((w-pad, h-pad), (w+pad*2, h+pad*2)).image
        
        filters = coalesce(filters, list)
        for f in filters:
            image = image.filter(f)
        
        # Crops the extra border, restoring the original size
        image = ImageOps.crop(image, pad)
        
        return Tile(image, self.shape)
    
    def brightness(self, factor: float = 1.0) -> "Tile":
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Brightness(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def color(self, factor: float = 1.0) -> "Tile":
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Color(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def contrast(self, factor: float = 1.0) -> "Tile":
        if factor == 1.0:
            return self
        
        image = ImageEnhance.Contrast(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def enhance(self, enhancer: ImageEnhance._Enhance, factor: float = 1.0) -> "Tile":
        image = enhancer(self.image).enhance(factor)
        
        return Tile(image, self.shape)
    
    def multiply(self, color_tile: "Tile") -> "Tile":
        image = ImageChops.multiply(self.image, color_tile.image)
        
        return Tile(image, self.shape)
    
    # IMAGE SHAPE OPERATIONS
    def rotate(self,
            angle: int,
            expand: bool = True,
        ) -> "Tile":
        """Rotates the Tile counter clockwise.
        
        Args:
            angle (int): How many degrees to rotate CCW.
            expand (bool, optional): If the image resizes to acommodate the rotation. Defaults to True.
        
        Returns:
            Tile: _description_
        """
        
        image = self.image.rotate(int(angle), expand=expand)
        
        return Tile(image, self.shape)
    
    def mirror(self,
            axis: Literal['x', 'y', 'p', 'n'],
        ) -> "Tile":
        """Mirrors the Tile in the horizontal, vertical or diagonal directions.  
        
        Args:
            `axis`, one of:
            - `x`, top <-> bottom, on horizontal axis
            - `y`, left <-> right, on vertical axis
            - `p`, top left <-> bottom right, on diagonal x=y axis (positive)
            - `n`, bottom left <-> top right, on diagonal x=-y axis (negative)
        
        Returns:
            Tile: The mirrored Tile.
        """
        
        match axis:
            case 'x': image = ImageOps.flip(self.image)
            case 'y': image = ImageOps.mirror(self.image)
            case 'p': image = self.image.transpose(Image.Transpose.TRANSVERSE)
            case 'n': image = self.image.transpose(Image.Transpose.TRANSPOSE)
            case _:   image = self.image.copy()
        
        return Tile(image, self.shape)
    
    def scale(self,
            factor: float | tuple[float, float],
            resample: Image.Resampling = Image.Resampling.NEAREST,
        ) -> "Tile":
        """'scale' as in 'stretch by factor(x,y) or factor(x==y)'"""
        
        if isinstance(factor, (int, float)):
            image = ImageOps.scale(self.image, factor, resample)
        
        elif isinstance(factor, tuple):
            w, h = self.size
            newsize = (int(w * factor[0]), int(h * factor[1]))
            image = self.image.resize(newsize, resample)
        
        else:
            print(f"Strange parameters")
            image = self.image.copy()
        
        return Tile(image, self.shape)
    
    def cutout(self,
            mask: "Tile",
        ) -> "Tile":
        """'cutout' as in 'cookie cutter'"""
        
        image = self.image.copy()
        image.putalpha(mask.as_mask.image)
        
        return Tile(image, mask.shape)
    
    def crop(self,
            box: tuple[int, int, int, int],
        ) -> "Tile":
        
        image = self.image.crop(box)
        
        return Tile(image, self.shape)
    
    def take(self,
            pos: tuple[int, int],
            size: tuple[int, int],
        ) -> "Tile":
        
        x0, y0 = pos
        width, height = size
        wrap_width, wrap_height = self.size
        
        xidx = (np.arange(x0, x0+width)  % wrap_width)
        yidx = (np.arange(y0, y0+height) % wrap_height)
        
        crop = self.as_array[np.ix_(yidx, xidx)]
        
        return Tile(crop)
    
    def offset(self,
            offset: tuple[int, int],
            wrap: bool = True,
        ) -> "Tile":
        
        if wrap:
            width, height = self.size
            offx, offy = offset
            
            posx = (width - offx) % width
            posy = (height - offy) % height
            
            return self.take((posx, posy), self.size)
        
        else:
            base_image = Image.new(self.mode, self.size, "black")
            base_image.paste(self.image, offset)
            
            return Tile(base_image, self.shape)
    
    # IMAGE ADVANCED OPERATIONS
    def outline(self,
            thickness: float = 1.0,
            color: str | tuple[int, int, int] = "white",
            combine: bool = True,
        ) -> "Tile":
        
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
        
        return Tile(base_image, self.shape)
    
    def overlay(self,
            head: "Tile",
            mask: "Tile" = None,
            alpha: float = 0.5,
        ) -> "Tile":
        # TODO: review
        """Merges two tiles into a new one.
        Must have a MASK or alpha value (default, 0.5).
        
        If using a MASK, it must have the same dimensions as both DATA Tiles.
        The pixel values from the MASK range from 0 (full base) to 255 (full head).
        
        The alpha value is used if no MASK is present.
        Its value is applied to the Tiles as a whole, not by pixel.
        
        Args:
            base (Tile): The Tile that goes on the bottom.
            head (Tile): The Tile that goes on top.
            mask (Tile, optional): A special Tile that controls how each pixel is merged. Defaults to None.
            alpha (float, optional): A value that controls how all pixels are merged. Defaults to 0.5.
        
        Returns:
            Tile: A new Tile resulting from the combination of both Tiles.
        """
        
        if mask is None:
            image = Image.blend(self.image, head.image, alpha)
            shape = self.shape
        
        else:
            image = Image.composite(head.image, self.image, mask.as_mask.image)
            shape = mask.shape
        
        return Tile(image, shape)
    
    def shade(self,
            mask: "Tile",
            offset: tuple[int, int],
            brightness: float = 1.0,
            inverted: bool = False,
            wrapped: bool = True,
        ) -> "Tile":
        
        offset_mask = mask.offset(offset, wrapped).invert()
        base_adjusted = self.brightness(brightness)
        
        if inverted: # inverts which is overlaid on the other for double shades
            base_shaded = self.overlay(base_adjusted, offset_mask)
        else:
            base_shaded = base_adjusted.overlay(self, offset_mask)
        
        return base_shaded


