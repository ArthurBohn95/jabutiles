"""
"""

from typing import Any, Literal, Sequence

from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

from jabutiles.tile_old import Tile
from jabutiles.utils import snap
from jabutiles.configs import Shapes
from jabutiles.tileops import TileOps



class TileGen:
    # MASK GENERATORS # --------------------------------------------------------
    @staticmethod
    def gen_ort_mask(size: int | tuple[int, int], **kwargs) -> Tile:
        """ Generates an orthogonal mask Tile given the size. """
        
        if isinstance(size, int):
            size = (size, size)
        
        mask_image = Image.new('L', size, 255)
        
        return Tile(mask_image)
    
    @staticmethod
    def gen_iso_mask(size: int | tuple[int, int], **kwargs) -> Tile:
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
        
        outline = TileOps.create_symmetrical_outline((W, H), lines, **kwargs)
        mask_image = TileOps.create_mask_from_outline(outline)
        
        return Tile(mask_image, 'iso')
    
    @staticmethod
    def gen_hex_mask(
            size: int | tuple[int, int],
            top: Literal["flat", "point"] = "flat",
            grain: int = 4,
            **kwargs
        ) -> Tile:
        
        if isinstance(size, int):
            assert size % 2 == 0, "Size must be even numbered"
            
            SQRT3BY2 = 0.866
            size = size, int(snap(size*SQRT3BY2, grain)) # nearest multiple of grain
        
        
        # It's easier to always create as a flat top and rotate later
        width, height = size
        
        # Markers (Q.uarter, M.iddle)
        QW, MW = width/4, width/2
        QH, MH = height/4, height/2
        
        # Small correction for widths 8 and 12 (outliers)
        if width in (8, 12):
            QW += 0.5
        
        lines = [
            ((0.5, MH-0.5), (QW-0.5, 0.5)), # top-left diagonal
            ((QW+0.5, 0.5), (MW, 0.5)), # top line
        ]
        
        outline = TileOps.create_symmetrical_outline((width, height), lines, **kwargs)
        mask_image = TileOps.create_mask_from_outline(outline)
        
        if top == 'point':
            mask_image = mask_image.rotate(90, expand=True)
        
        return Tile(mask_image, f'hex.{top}')
    
    @staticmethod
    def gen_shape_mask(
            size: int | tuple[int, int],
            shape: Shapes,
            **params: dict[str, Any],
        ) -> Tile:
        
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
                return Tile(None)
    
    @staticmethod
    def gen_brick_pattern_mask(
            size: tuple[int, int],
            brick_size: tuple[int, int],
            gap_width: int = 0,
            edge_width: int = 0,
            base_value: int = 0,
            fill_value: int = 255,
            row_offset: int = None,
            invert: bool = True,
            **params: dict[str, Any],
        ) -> Tile:
        """Works with:
        ```
        gap_width  | 1 | 2 | 3 | 4 | 5 | 6 | ...
        edge_width | * | * | * | X | * | ? | ...
        ```
        """
        
        MW, MH = size       # Mask Width and Height
        BW, BH = brick_size # Brick Width and Height
        BRW = MW + 2*BW     # Brick Row Width
        HBW = BW//2         # Half Brick Width
        if row_offset is None:
            row_offset = HBW
        
        brick_template = Image.new('L', brick_size, base_value)
        brick_temp_canv = ImageDraw.Draw(brick_template)
        brick_temp_canv.line(((0.5, 0.5), (BW+0.5, 0.5)), fill_value, gap_width)
        brick_temp_canv.line(((HBW+0.5, 0.5), (HBW+0.5, BH+0.5)), fill_value, gap_width)
        
        # Some fuckery, don't mess with it
        if edge_width:
            CO = gap_width / 2 if gap_width % 2 == 0 else 0.5 * gap_width
            polyconf = dict(n_sides=4, rotation=45, fill=fill_value)
            
            rad = edge_width + gap_width
            brick_temp_canv.regular_polygon((HBW+0.5, 0.5, rad), **polyconf)
            brick_temp_canv.regular_polygon((HBW+0.5, BH+CO, rad), **polyconf)
            
            if gap_width % 2 == 0:
                brick_temp_canv.regular_polygon((HBW+CO+0.5, 0.5, rad), **polyconf)
                brick_temp_canv.regular_polygon((HBW+CO+0.5, BH+CO+0.5, rad), **polyconf)
        
        # Builds the single brick row with the single brick template
        brick_row = Image.new('L', (BRW, BH), base_value)
        for col in range(0, BRW, BW):
            brick_row.paste(brick_template, (col, 0))
        
        # Pastes the brick row template on each new row
        # The offset can be overriden with `row_offset=<int>`
        mask_image  = Image.new("L", size, base_value)
        
        for cnt, row in enumerate(range(0, MH, BH)):
            offset = (cnt % 2) * row_offset - (HBW + BW)
            
            mask_image.paste(brick_row, (offset, row))
        
        if invert:
            mask_image = ImageOps.invert(mask_image)
        
        return Tile(mask_image)
    
    @staticmethod
    def gen_line_draw_mask(
            size: tuple[int, int],
            lines: Sequence[tuple[float, float, float, float]],
            **params: dict[str, Any],
        ) -> Tile:
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
        
        return Tile(mask_image)
    
    @staticmethod
    def gen_blobs_mask(
            size: tuple[int, int],
            blobs: Sequence[tuple[tuple[float, float], tuple[float, float]]],
            **params: dict[str, Any],
        ) -> Tile:
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
        
        return Tile(mask_image)
    
    
    # TEXTURE GENERATORS # -----------------------------------------------------
    @staticmethod
    def gen_random_rgb(
            size: tuple[int, int],
            ranges: list[tuple[int, int]],
            mode: Literal['minmax', 'avgdev'] = 'minmax',
        ) -> Tile:
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
        
        return Tile(image)
    
    @staticmethod
    def gen_random_mask(
            size: tuple[int, int],
            vrange: tuple[int, int],
        ) -> Tile:
        """ Generates a random Mask Tile"""
        
        image = Image.fromarray(np.stack(
            np.random.randint(vrange[0], vrange[1], size, dtype=np.uint8), axis=-1), 'L')
        
        return Tile(image)
    
    @staticmethod
    def gen_texture_tile(
            size: int | tuple[int, int],
            texture_name: str,
            **kwargs,
        ) -> Tile:
        
        if isinstance(size, int):
            size = (size, size)
        
        FULL_SIZE = size
        HALF_SIZE = size[0]//2, size[1]//2
        HALF_WIDTH = size[0]//2, size[1]
        QUARTER_HEIGHT = size[0], size[1]//4
        
        tile: Tile = None
        
        match texture_name.lower():
            case 'grass':
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((48, 64), (64, 108), (24, 32)))
                    .filter([ImageFilter.SMOOTH_MORE])
                    .enhance(ImageEnhance.Color, 0.9)
                )
            case 'grass.dry': # path
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((80, 8), (80, 8), (24, 4)), 'avgdev')
                    .filter([ImageFilter.SMOOTH_MORE])
                    .enhance(ImageEnhance.Color, 0.66)
                )
            case 'grass.wet': # moss
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((48, 4), (64, 4), (24, 4)), 'avgdev')
                    #.filter([ImageFilter.SMOOTH_MORE])
                )
            
            case 'water':
                tile = (TileGen
                    .gen_random_rgb(HALF_WIDTH, ((24, 32), (32, 48), (80, 120)))
                    .scale((2, 1))
                    .filter([ImageFilter.SMOOTH, ImageFilter.SMOOTH])
                )
            case 'water.shallow': # puddle
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((64, 8), (72, 8), (120, 12)), 'avgdev')
                    .filter([ImageFilter.SMOOTH, ImageFilter.SMOOTH])
                )
            
            case 'dirt':
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((140, 160), (100, 120), (64, 80)))
                    .filter([ImageFilter.SMOOTH_MORE])
                )
            case 'dirt.wet': # mud
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((100, 6), (72, 6), (56, 4)), 'avgdev')
                    .filter([ImageFilter.SMOOTH])
                )
            
            case 'sand':
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((240, 255), (200, 220), (180, 192)))
                    .filter([ImageFilter.SMOOTH])
                    # .enhance(ImageEnhance.Color, 0.2)
                )
            case 'clay':
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((108, 120), (64, 80), (48, 64)))
                    .filter([ImageFilter.SMOOTH_MORE])
                )
            
            case 'stone':
                tile = (TileGen
                    .gen_random_rgb(HALF_SIZE, ((100, 112), (100, 112), (100, 112)))
                    .scale(2, Image.Resampling.NEAREST)
                    .enhance(ImageEnhance.Color, 0.2)
                )
            case 'stone.raw':
                tile = (TileGen
                    .gen_random_rgb(FULL_SIZE, ((96, 48), (96, 48), (96, 12)), 'avgdev')
                    .filter([ImageFilter.SMOOTH_MORE])
                    .enhance(ImageEnhance.Color, 0.05)
                )
            
            case 'wood':
                tile = (TileGen
                    .gen_random_rgb(QUARTER_HEIGHT, ((80, 8), (32, 6), (16, 4)), 'avgdev')
                    .scale((1, 4))
                    .filter([ImageFilter.BLUR])
                    .enhance(ImageEnhance.Contrast, 0.666)
                    .enhance(ImageEnhance.Color, 0.75)         # 0.666
                    .enhance(ImageEnhance.Brightness, 1.1)    # 1.333
                )
            
            # case '':
            #     return
            
            case _:
                tile = Tile()
        
        return tile

