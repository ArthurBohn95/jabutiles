""" """

from typing import Any, Literal, Sequence

import numpy as np
from PIL import Image, ImageOps, ImageDraw

from jabutiles.mask import Mask, ShapeMask, EdgeMask
from jabutiles.utils import snap
from jabutiles.utils_img import make_symmetrical_outline, fanout



class MaskGen:
    @staticmethod
    def noise(
            size: int | tuple[int, int],
            vrange: tuple[int, int],
        ) -> Mask:
        """ Generates a random noise Mask Tile"""
        
        image = Image.fromarray(np.stack(
            np.random.randint(vrange[0], vrange[1], size, dtype=np.uint8), axis=-1), 'L')
        
        return Mask(image)
    
    
    @staticmethod
    def brick_pattern(
            mask_size: int | tuple[int, int],
            brick_size: int | tuple[int, int],
            gap_size: int | tuple[int, int] = 1,
            edge_size: int = 0,
            row_offset: int = None,
            invert: bool = True,
            **params: dict,
        ) -> Mask:
        """
        """
        
        # Parameters setup
        DEBUG: bool = params.get("debug", False)
        
        fval: int = 255 if not DEBUG else 127
        
        if isinstance(gap_size,   int): gap_size   = (gap_size, gap_size)
        if isinstance(mask_size,  int): mask_size  = (mask_size, mask_size)
        if isinstance(brick_size, int): brick_size = (brick_size, brick_size)
        
        # Constants
        MW, MH = mask_size      # Mask Width and Height
        BW, BH = brick_size     # Brick Width and Height
        GW, GH = gap_size       # Gap Width and Height
        
        HBW = BW // 2           # Half Brick Width
        BTW = BW + GW           # Brick Template Width
        BTH = BH + GH           # Brick Template Height
        BRW = MW + 2*(BW + GW)  # Brick Row Width
        BRH = BH + GH           # Brick Row Height
        
        if row_offset is None: row_offset = BTW // 2
        else:                  row_offset %= BTW
        
        GOX = (GW - 0.5) // 2   # Gap Offset on x-axis
        GOY = (GH - 0.5) // 2   # Gap Offset on y-axis
        
        # Creates the single brick template
        brick_template = Image.new('L', (BTW, BTH), 0)
        brick_canvas = ImageDraw.Draw(brick_template)
        
        # Draws the gaps
        brick_canvas.line(((0.5, GOY), (BRW+0.5, GOY)), fval, GH)
        brick_canvas.line(((GOX+HBW, 0.5), (GOX+HBW, BRH+0.5)), fval, GW)
        
        # Adds the rounded edges
        if edge_size:
            radius = edge_size + 1
            polyconf = dict(n_sides=4, rotation=45, fill=255)
            
            # Adds the top-left corner
            brick_canvas.regular_polygon((HBW, GH-1, radius), **polyconf)
            # Adds the top-right corner
            brick_canvas.regular_polygon((HBW+GW-1, GH-1, radius), **polyconf)
            
            # Flips the corners top-bottom and pastes them back
            flipped = ImageOps.flip(brick_template)
            brick_template.paste(flipped, (0, GH), flipped)
        
        # Generates the long brick row
        brick_row = Image.new('L', (BRW, BRH), 0)
        for col in range(0, BRW, BTW):
            brick_row.paste(brick_template, (col, 0))
        
        # Pastes the brick rows with offsets
        image = Image.new('L', mask_size, 0)
        for cnt, row in enumerate(range(0, MH, BRH)):
            offset = ((cnt % 2) * row_offset) - (HBW + BTW)
            image.paste(brick_row, (offset, row))
        
        # Images are generated with 1s on 0s, so must be inverted
        if invert:
            image = ImageOps.invert(image)
        
        return Mask(image)
    
    
    @staticmethod
    def line_draw(
            size: tuple[int, int],
            lines: Sequence[tuple[float, float, float, float]],
            **params: dict[str, Any],
        ) -> Mask:
        """
        ```
        size = (10, 10)
        lines = [
            ((x0, y0), (x1, y1), width),
            ...
        ]
        ```
        """
        
        BASE_VALUE = params.get('base_value', 0)
        FILL_VALUE = params.get('fill_value', 255)
        INVERT = params.get('invert', False)
        
        image = Image.new('L', size, BASE_VALUE)
        canvas = ImageDraw.Draw(image)
        
        for line in lines:
            p0, p1, width = line
            canvas.line((p0, p1), FILL_VALUE, width)
        
        if INVERT:
            image = ImageOps.invert(image)
        
        return Mask(image)
    
    
    @staticmethod
    def blob_draw(
            size: tuple[int, int],
            blobs: Sequence[tuple[tuple[float, float], tuple[float, float]]],
            **params: dict[str, Any],
        ) -> Mask:
        """
        ```
        size = (10, 10)
        blobs = [
            ((cx, cy), r),        # for circles
            ((cx, cy), (rx, ry)), # for ellipses
            ...
        ]
        # center x and y
        # r = radius
        # rx = radius on x axis (width/2)
        # ry = radius on y axis (height/2)
        ```
        """
        
        BASE_VALUE = params.get('base_value', 0)
        FILL_VALUE = params.get('fill_value', 255)
        INVERT = params.get('invert', False)
        
        mask_image = Image.new('L', size, BASE_VALUE)
        canvas = ImageDraw.Draw(mask_image)
        
        for blob in blobs:
            pos, args = blob
            
            if isinstance(args, tuple):
                x, y = pos
                w, h = args
                canvas.ellipse((x-w, y-h, x+w, y+h), FILL_VALUE)
            else:
                canvas.circle(pos, args, FILL_VALUE)
        
        if INVERT:
            mask_image = ImageOps.invert(mask_image)
        
        return Mask(mask_image)



class ShapeMaskGen:
    @staticmethod
    def orthogonal(
            size: int | tuple[int, int],
            **params,
        ) -> ShapeMask:
        """Generates an orthogonal Mask given the size.
        """
        
        if isinstance(size, int):
            size = (size, size)
        
        mask_image = Image.new('L', size, 255)
        
        return ShapeMask(mask_image, 'orthogonal')
    
    @staticmethod
    def isometric(
            size: int | tuple[int, int],
            **params,
        ) -> ShapeMask:
        """Generates an isometric Mask given the size.
        """
        
        if isinstance(size, int):
            size = size//2
            W, H = size*2, size
        else:
            W, H = size
        
        lines = [
            ((0, H/2-1), (W/2-1, 0)), # top-left diagonal
        ]
        
        image = make_symmetrical_outline((W, H), lines, **params)
        
        return ShapeMask(image, 'isometric')
    
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
        
        image = make_symmetrical_outline((W, H), lines, **params)
        
        if top == 'point':
            image = image.rotate(90, expand=True)
        
        return ShapeMask(image, f'hexagonal.{top}')
    
    # # Experimental
    # @staticmethod
    # def octogonal(
    #         size: int | tuple[int, int],
    #         top: Literal["flat", "point"] = "flat",
    #         **params,
    #     ) -> ShapeMask:
    #     """Generates an experimental octogonal Mask given the size.
    #     """
        
    #     if isinstance(size, int):
    #         size = size, size
        
    #     # It's easier to always create as a flat top and rotate later
    #     W, H = size
        
    #     # Markers (Q.uarter, M.iddle)
    #     QW, MW = W/4, W/2
    #     QH, MH = H/4, H/2
    #     SW, SH = (2*W)**0.5, (2*H)**0.5
        
    #     lines = [
    #         ((0, SH), (SW, 0)), # top-left diagonal
    #         ((SW, 0), (W-SW, 0)), # top border
    #     ]
        
    #     image = Image.new('L', size, 0)
    #     canvas = ImageDraw.Draw(image)
        
    #     for line in lines:
    #         canvas.line(line, fill=255)
        
    #     image = fanout(image, False)
        
    #     return ShapeMask(image, 'other')



class EdgeMaskGen:
    pass

