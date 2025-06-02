from typing import Any, Literal

from PIL import Image, ImageOps, ImageDraw
import numpy as np

from jabutiles.mask import Mask
from jabutiles.utils import snap
from jabutiles.configs import Shapes, Mirrors, Rotations, TILE_MOVE_PARAMS



class ShapeMask(Mask):
    # DUNDERS # ----------------------------------------------------------------
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            shape: Shapes = 'ort',
            **params
        ) -> None:
        
        params["builder"] = ShapeMask
        super().__init__(image, **params)
        self._shape: Shapes = shape
    
    def __str__(self) -> str:
        return f"SHAPEMASK | size:{self.size} shape: {self.shape} mode:{self.mode}"
    
    # PROPERTIES # -------------------------------------------------------------
    @property
    def shape(self) -> str:
        return self._shape
    
    # METHODS # ----------------------------------------------------------------
    # BASIC INTERFACES
    def copy_with_params(self,
            image: Image,
        ) -> "ShapeMask":
        """Returns a deep copy but keeping the original parameters."""
        
        # print("BaseImage.copy_with_params")
        
        return self._builder(image, self.shape, builder=self._builder)
    
    # IMAGE OPERATIONS
    def rotate(self,
            angle: Rotations = 0,
            expand: bool = True,
        ) -> "ShapeMask":
        """Rotates the Mask counter clockwise.
        
        Args:
            angle (int): How many degrees to rotate CCW.
            expand (bool, optional): If the image resizes to acommodate the rotation. Defaults to True.
        
        Returns:
            The rotated Mask
        """
        
        if angle == 0 or angle not in TILE_MOVE_PARAMS[self.shape]['rotation']:
            return self
        
        return super().rotate(angle, expand)
    
    def mirror(self,
            axis: Mirrors = None,
        ) -> "ShapeMask":
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
        
        if axis is None or axis not in TILE_MOVE_PARAMS[self.shape]['mirror']:
            return self
        
        return super().mirror(axis)
    
    
    
    



class ShapeMaskGen:
    # STATIC METHODS # ---------------------------------------------------------
    @staticmethod
    def __symmetrical_outline(
            size: tuple[int, int],
            lines: list[tuple[tuple[float]]],
            fill: bool = True,
            **params,
        ) -> Image.Image:
        
        image = Image.new("L", size, 0)
        idraw = ImageDraw.Draw(image)
        
        for line in lines:
            idraw.line(line, fill=255)
        
        image.paste(ImageOps.flip(image), mask=ImageOps.invert(image))
        image.paste(ImageOps.mirror(image), mask=ImageOps.invert(image))
        
        if fill:
            ImageDraw.floodfill(image, (size[0] / 2, size[1] / 2), 255)
        
        return image
    
    @staticmethod
    def orthogonal(
            size: int | tuple[int, int],
            **params,
        ) -> ShapeMask:
        """Generates an orthogonal ShapeMask given the size.
        """
        
        if isinstance(size, int):
            size = (size, size)
        
        mask_image = Image.new('L', size, 255)
        
        return ShapeMask(mask_image, 'ort')
    
    @staticmethod
    def isometric(
            size: int | tuple[int, int],
            **params,
        ) -> ShapeMask:
        """Generates an isometric ShapeMask given the size.
        """
        
        if isinstance(size, int):
            size = size//2
            W, H = size*2, size
        else:
            W, H = size
        
        lines = [
            ((0, H/2-1), (W/2-1, 0)), # top-left diagonal
        ]
        
        image = ShapeMaskGen.__symmetrical_outline((W, H), lines, **params)
        
        return ShapeMask(image, 'iso')
    
    @staticmethod
    def hexagonal(
            size: int | tuple[int, int],
            top: Literal["flat", "point"] = "flat",
            grain: int = 4,
            **params
        ) -> ShapeMask:
        
        if isinstance(size, int):
            assert size % 2 == 0, "Size must be even numbered"
            
            SQRT3BY2 = 0.866
            size = size, int(snap(size*SQRT3BY2, grain)) # nearest multiple of grain
        
        # It's easier to always create as a flat top and rotate later
        W, H = size
        
        # Markers (Q.uarter, M.iddle)
        QW, MW = W/4, W/2
        QH, MH = H/4, H/2
        
        # Small correction for widths 8 and 12 (outliers)
        if W in (8, 12):
            QW += 0.5
        
        lines = [
            ((0.5, MH-0.5), (QW-0.5, 0.5)), # top-left diagonal
            ((QW+0.5, 0.5), (MW, 0.5)), # top line
        ]
        
        image = ShapeMaskGen.__symmetrical_outline((W, H), lines, **params)
        
        if top == 'point':
            image = image.rotate(90, expand=True)
        
        return ShapeMask(image, f'hex.{top}')
    
    @staticmethod
    def generate(
            size: int | tuple[int, int],
            shape: Shapes,
            **params: dict[str, Any],
        ) -> Mask:
        
        if '.' in shape:
            shape, sdev = shape.split('.')
        
        match shape:
            case 'ort':
                return ShapeMaskGen.orthogonal(size, **params)
            
            case 'iso':
                return ShapeMaskGen.isometric(size, **params)
            
            case 'hex':
                return ShapeMaskGen.hexagonal(size, sdev, **params)
            
            case _:
                return ShapeMask(None)
