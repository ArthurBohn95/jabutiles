"""
"""

from typing import Any, Literal, Sequence

from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

from jabutiles.mask import Mask
from jabutiles.utils import snap
from jabutiles.configs import Shapes
from jabutiles.texture import Texture



class TileGen:
    # MASK GENERATORS # --------------------------------------------------------
    @staticmethod
    def gen_ort_mask(size: int | tuple[int, int], **params) -> Mask:
        """ Generates an orthogonal mask Tile given the size. """
        
        if isinstance(size, int):
            size = (size, size)
        
        mask_image = Image.new('L', size, 255)
        
        return Mask(mask_image)
    
    @staticmethod
    def gen_iso_mask(size: int | tuple[int, int], **params) -> Mask:
        """Generates an isometric mask Tile given the size.
        """
        
        if isinstance(size, int):
            size = size//2
            W, H = size*2, size
        else:
            W, H = size
        
        lines = [
            ((0, H/2-1), (W/2-1, 0)), # top-left diagonal
        ]
        
        image = Mask._create_symmetrical_outline((W, H), lines, **params)
        
        return Mask(image, 'iso')
    
    @staticmethod
    def gen_hex_mask(
            size: int | tuple[int, int],
            top: Literal["flat", "point"] = "flat",
            grain: int = 4,
            **params
        ) -> Mask:
        
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
        
        image = Mask._create_symmetrical_outline((W, H), lines, **params)
        
        if top == 'point':
            image = image.rotate(90, expand=True)
        
        return Mask(image, f'hex.{top}')
    
    @staticmethod
    def gen_shape_mask(
            size: int | tuple[int, int],
            shape: Shapes,
            **params: dict[str, Any],
        ) -> Mask:
        
        if '.' in shape:
            shape, sdev = shape.split('.')
        
        match shape:
            case 'ort':
                return TileGen.gen_ort_mask(size, **params)
            
            case 'iso':
                return TileGen.gen_iso_mask(size, **params)
            
            case 'hex':
                return TileGen.gen_hex_mask(size, sdev, **params)
            
            case _:
                return Mask(None)
    
    @staticmethod
    def gen_brick_pattern_mask(
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
        
        if isinstance(mask_size, int) : mask_size  = (mask_size, mask_size)
        if isinstance(brick_size, int): brick_size = (brick_size, brick_size)
        if isinstance(gap_size, int)  : gap_size   = (gap_size, gap_size)
        
        # Constants
        MW, MH = mask_size      # Mask Width and Height
        BW, BH = brick_size     # Brick Width and Height
        GW, GH = gap_size       # Gap Width and Height
        
        HBW = BW // 2           # Half Brick Width
        BTW = BW + GW           # Brick Template Width
        BTH = BH + GH           # Brick Template Height
        BRW = MW + 2*(BW + GW)  # Brick Row Width
        BRH = BH + GH           # Brick Row Height
        
        if row_offset is None:
            row_offset = BTW // 2
        else:
            row_offset %= BTW
        
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
    def gen_line_draw_mask(
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
        
        mask_image = Image.new('L', size, BASE_VALUE)
        canvas = ImageDraw.Draw(mask_image)
        
        for line in lines:
            p0, p1, width = line
            canvas.line((p0, p1), FILL_VALUE, width)
        
        if INVERT:
            mask_image = ImageOps.invert(mask_image)
        
        return Mask(mask_image)
    
    @staticmethod
    def gen_blobs_mask(
            size: tuple[int, int],
            blobs: Sequence[tuple[tuple[float, float], tuple[float, float]]],
            **params: dict[str, Any],
        ) -> Mask:
        """
        ```
        size = (10, 10)
        blobs = [
            ((cx, cy), (rx, ry)), # for ellipses
            ((cx, cy), r),        # for circles
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
    
    
    # TEXTURE GENERATORS # -----------------------------------------------------
    @staticmethod
    def gen_random_rgb(
            size: tuple[int, int],
            ranges: list[tuple[int, int]],
            mode: Literal['minmax', 'avgdev'] = 'minmax',
        ) -> Texture:
        """ Generates a random RGB Tile from the channels ranges. """
        
        size = size[1], size[0]
        
        if mode == 'minmax':
            image = (Image.fromarray(
                np.stack((
                    np.random.randint(ranges[0][0], ranges[0][1], size, dtype=np.uint8),
                    np.random.randint(ranges[1][0], ranges[1][1], size, dtype=np.uint8),
                    np.random.randint(ranges[2][0], ranges[2][1], size, dtype=np.uint8),
                ), axis=-1),
                'RGB')
            )
        
        elif mode == 'avgdev':
            image = (Image.fromarray(
                np.stack((
                    np.random.randint(ranges[0][0]-ranges[0][1], ranges[0][0]+ranges[0][1], size, dtype=np.uint8),
                    np.random.randint(ranges[1][0]-ranges[1][1], ranges[1][0]+ranges[1][1], size, dtype=np.uint8),
                    np.random.randint(ranges[2][0]-ranges[2][1], ranges[2][0]+ranges[2][1], size, dtype=np.uint8),
                ), axis=-1),
                'RGB')
            )
        
        return Texture(image)
    
    @staticmethod
    def gen_random_mask(
            size: tuple[int, int],
            vrange: tuple[int, int],
        ) -> Mask:
        """ Generates a random Mask Tile"""
        
        image = Image.fromarray(np.stack(
            np.random.randint(vrange[0], vrange[1], size, dtype=np.uint8), axis=-1), 'L')
        
        return Mask(image)
    
    @staticmethod
    def gen_texture_tile(
            size: int | tuple[int, int],
            texture_name: str,
            **params,
        ) -> Texture:
        
        if isinstance(size, int):
            size = (size, size)
        
        FULL_SIZE = size
        HALF_SIZE = size[0]//2, size[1]//2
        HALF_WIDTH = size[0]//2, size[1]
        QUARTER_HEIGHT = size[0], size[1]//4
        
        texture: Texture = None
        
        match texture_name.lower():
            case 'grass':
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((48, 64), (64, 108), (24, 32)))
                    .filter([ImageFilter.SMOOTH_MORE])
                    .color(0.9)
                )
            case 'grass.dry': # path
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((80, 8), (80, 8), (24, 4)), 'avgdev')
                    .filter([ImageFilter.SMOOTH_MORE])
                    .color(0.66)
                )
            case 'grass.wet': # moss
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((48, 4), (64, 4), (24, 4)), 'avgdev')
                )
            
            case 'water':
                texture = (TileGen
                    .gen_random_rgb(HALF_WIDTH, ((24, 32), (32, 48), (80, 120)))
                    .scale((2, 1))
                    .filter([ImageFilter.SMOOTH, ImageFilter.SMOOTH])
                )
            case 'water.shallow': # puddle
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((64, 8), (72, 8), (120, 12)), 'avgdev')
                    .filter([ImageFilter.SMOOTH, ImageFilter.SMOOTH])
                )
            
            case 'dirt':
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((140, 160), (100, 120), (64, 80)))
                    .filter([ImageFilter.SMOOTH_MORE])
                )
            case 'dirt.wet': # mud
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((100, 6), (72, 6), (56, 4)), 'avgdev')
                    .filter([ImageFilter.SMOOTH])
                )
            
            case 'sand':
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((240, 255), (200, 220), (180, 192)))
                    .filter([ImageFilter.SMOOTH])
                )
            case 'clay':
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((108, 120), (64, 80), (48, 64)))
                    .filter([ImageFilter.SMOOTH_MORE])
                )
            
            case 'stone':
                texture = (TileGen
                    .gen_random_rgb(HALF_SIZE, ((100, 112), (100, 112), (100, 112)))
                    .scale(2, Image.Resampling.NEAREST)
                    .color(0.2)
                )
            case 'stone.raw':
                texture = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((96, 48), (96, 48), (96, 12)), 'avgdev')
                    .filter([ImageFilter.SMOOTH_MORE])
                    .color(0.05)
                )
            
            case 'wood':
                texture = (TileGen
                    .gen_random_rgb(QUARTER_HEIGHT, ((80, 8), (32, 6), (16, 4)), 'avgdev')
                    .scale((1, 4))
                    .filter([ImageFilter.BLUR])
                    .contrast(0.666)
                    .color(0.75)        # 0.666
                    .brightness(1.1)    # 1.333  
                )
            
            # case '':
            #     return
            
            case _:
                texture = Texture()
        
        return texture

