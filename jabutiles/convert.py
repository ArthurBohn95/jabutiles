from jabutiles.tile import Tile
from jabutiles.utils import snap
from jabutiles.texture import Texture
from jabutiles.tilegen import TileGen



def convert_ort2iso(
        tile: Tile | Texture,
        pad: int = 2
    ) -> Tile:
    
    w, h = tile.size
    base = tile.take((-pad, -pad), (w+2*pad, h+2*pad))
    base = base.rotate(-45).scale((1, 0.5))
    x = snap(base.size[1]-2, 2)
    w, h = x*2, x
    base = base.crop((pad, pad//2, w-pad, h-pad//2))
    
    isomask = TileGen.gen_iso_mask(base.size)
    return base.cutout(isomask)


