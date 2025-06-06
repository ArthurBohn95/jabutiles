from jabutiles.texture import Texture
from jabutiles.maskgen import ShapeMaskGen
from jabutiles.utils import snap




def convert_ort2iso(
        texture: Texture,
        pad: int = 2
    ) -> Texture:
    
    w, h = texture.size
    isoimg = texture.take((-pad, -pad), (w+2*pad, h+2*pad))
    isoimg = isoimg.rotate(-45).scale((1, 0.5))
    x = snap(isoimg.size[1]-2, 2)
    w, h = x*2, x
    isoimg = isoimg.crop((pad, pad//2, w-pad, h-pad//2))
    
    isomask = ShapeMaskGen.isometric(isoimg.size)
    return isomask.cut(isoimg)


