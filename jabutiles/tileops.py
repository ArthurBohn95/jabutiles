

from PIL import Image, ImageDraw, ImageOps, ImageEnhance

from jabutiles.tile_old import Tile
from jabutiles.utils import combine_choices, snap



class TileOps:
    # STATIC METHODS # ---------------------------------------------------------
    @staticmethod
    def create_symmetrical_outline(
            size: tuple[int, int],
            lines: list[tuple[tuple[float]]],
            **kwargs,
        ) -> Image.Image:
        
        image = Image.new("L", size, 0)
        draw  = ImageDraw.Draw(image)
        
        for line in lines:
            draw.line(line, fill=255)
        
        image.paste(ImageOps.flip(image), mask=ImageOps.invert(image))
        image.paste(ImageOps.mirror(image), mask=ImageOps.invert(image))
        
        return image
    
    @staticmethod
    def create_mask_from_outline(
            base: Image.Image,
            **kwargs,
        ) -> Image.Image:
        
        mask = base.copy()
        width, height = mask.size
        
        ImageDraw.floodfill(mask, (width / 2, height / 2), 255)
        
        return mask
    
    @staticmethod
    def convert_ort2iso(
            tile: Tile,
            pad: int = 2
        ) -> Tile:
        
        if tile.shape != 'ort':
            return tile
        
        from jabutiles.tilegen import TileGen
        
        w, h = tile.size
        base = tile.take((-pad, -pad), (w+2*pad, h+2*pad))
        base = base.rotate(-45).scale((1, 0.5))
        x = snap(base.size[1]-2, 2)
        w, h = x*2, x
        base = base.crop((pad, pad//2, w-pad, h-pad//2))
        
        isomask = TileGen.gen_iso_mask(base.size)
        return base.cutout(isomask)
    
    @staticmethod
    def merge_tiles(*tiles: tuple[Tile, Tile]) -> Tile:
        """
        tiles = [(tile, mask), (tile, mask), ...]
        """
        REFTILE = tiles[0][0]
        REFMASK = tiles[-1][1]
        SIZE = REFTILE.size
        
        image = Image.new('RGBA', SIZE, (0, 0, 0, 0))
        
        for tile, mask in tiles:
            image.paste(tile.image, mask=mask.as_mask.image)
        
        return Tile(image, REFMASK.shape)
    
    @staticmethod
    def merge_masks(*masks: Tile) -> Tile:
        """Adds several MASKs together.
        Their values are combined with bitwise OR.
        
        Returns:
            Tile: A single Tile MASK
        """
        
        assert len(masks) >= 2, "Insufficient masks to be merged (<2)"
        
        base = masks[0].as_mask.as_array
        
        for mask in masks[1:]:
            base |= mask.as_mask.as_array
        
        return Tile(base, masks[-1].shape)
    
    @staticmethod
    def combine_masks(
            mask_info: dict[str, Tile]
        ) -> tuple[str, Tile]:
        """ Combine the masks' data AND their neighbours' information"""
        
        assert len(mask_info) >= 2, "Insufficient masks to be combined (<2)"
        
        mask_data = mask_info.copy()
        base_edge, base_mask = mask_data.popitem()
        
        for edge, mask in mask_data.items():
            base_edge = combine_choices(base_edge, edge)
            base_mask = TileOps.merge_masks(base_mask, mask)
        
        return base_edge, base_mask


