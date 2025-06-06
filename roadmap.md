# RoadMap

## Tile Shapes

1. Initially, only orthogonal tiles will have full support.
This means all operations must run seamlessly on orthogonal shaped Masks and Tiles.

2. Isometric will come later, as they are mostly a 45 degree rotation with half the height, and share the same number of edges.

3. Lastly, both types of hexagonals will be included.
As they are quite different from both shapes so far, they'll need special care.

## Numpy

Numpy is currently only used for some operations:
- Mask.merge()
- BaseImage.take()
- TextureGen.random_rgb()

If really wanted, it could be fully removed in favor for pure python, with the caveat of possibly slower operations.

OR

All operations could benefit with some numpy calls, for a faster but tighter experience.


