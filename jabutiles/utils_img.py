import random as rnd

from PIL import (
    Image, ImageOps, ImageDraw, ImageChops, ImageFilter, ImageEnhance
)

from jabutiles.utils import clamp



def display_image(img: Image.Image, scale: float = 10) -> None:
    display(ImageOps.scale(img, scale, Image.Resampling.NEAREST)) # type: ignore


def make_symmetrical_outline(
        size: tuple[int, int],
        lines: list[tuple[tuple[float]]],
        filled: bool = True,
        **params,
    ) -> Image.Image:
    
    image = Image.new("L", size, 0)
    idraw = ImageDraw.Draw(image)
    
    for line in lines:
        idraw.line(line, fill=255)
    
    image.paste(ImageOps.flip(image), mask=ImageOps.invert(image))
    image.paste(ImageOps.mirror(image), mask=ImageOps.invert(image))
    
    if filled:
        ImageDraw.floodfill(image, (size[0] / 2, size[1] / 2), 255)
    
    return image


def fanout(
        image: Image.Image,
        filled: bool = True,
    ) -> Image.Image:
    
    base = image.copy()
    base.paste(base.rotate(90, Image.Resampling.NEAREST), mask=ImageOps.invert(base))
    base.paste(base.rotate(180, Image.Resampling.NEAREST), mask=ImageOps.invert(base))
    
    if filled:
        ImageDraw.floodfill(base, (base.size[0] / 2, base.size[1] / 2), 255)
    
    return base


def cut_image(
        image: Image.Image,
        mask: Image.Image,
    ) -> Image.Image:
    
    if mask.mode != 'L':
        mask.convert('L')
    
    base = image.copy()
    base.putalpha(mask)
    
    return base


def get_outline(
        image: Image.Image,
        thickness: float = 1.0,
        color: str | tuple[int, int, int] = "white",
        dist: float = 1.0,
    ) -> Image.Image:
    
    ref_image = image.convert("RGBA")
    
    if image.mode in ('L', 'LA'):
        alpha = ImageEnhance.Brightness(image).enhance(255)
        ref_image.putalpha(alpha)
    
    outline = Image.new(ref_image.mode, ref_image.size, (0, 0, 0, 0))
    canvas = ImageDraw.Draw(outline)
    
    # Ensures thickness is always at least 1
    T = clamp(thickness, (1, 1000))
    W, H = ref_image.size
    edge = ref_image.filter(ImageFilter.FIND_EDGES).load()
    
    for x in range(W):
        for y in range(H):
            if not edge[x,y][3]:
                continue
            
            if dist < rnd.random():
                continue
            
            if T % 1 == 0: # 1, 2, 3, ...round corners
                canvas.ellipse((x-T, y-T, x+T, y+T), fill=color)
            
            else: # 1.5, 2.5, 3.5, ... square corners
                canvas.rectangle((x-T+0.5, y-T+0.5, x+T-0.5, y+T-0.5), fill=color)
    
    alpha = ImageEnhance.Brightness(ref_image).enhance(255)
    outline = ImageChops.subtract(outline, alpha)
    
    return outline




