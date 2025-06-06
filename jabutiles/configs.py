"""
"""

from typing import Union, Literal

import numpy as np
from PIL import Image



type ImageSource = Union[str, Image.Image, np.typing.NDArray]

type Shape = Literal[
    'orthogonal',
    'isometric',
    'hexagonal.flat',
    'hexagonal.point',
]
SHAPES: Shape = [
    'orthogonal',
    'isometric',
    'hexagonal.flat',
    'hexagonal.point',
    'other',
]

type Rotation = Literal[0, 90, 180, 270]
ROTATIONS: Rotation = [0, 90, 180, 270]

type Reflection = Literal['x', 'y', 'p', 'n']
REFLECTIONS: Reflection = ['x', 'y', 'p', 'n']

type EdgeOp = Literal['rotation', 'reflection']
EDGEOPS: EdgeOp = ['rotation', 'reflection']


SHAPE_EDGE_SIZE: dict[Shape, int] = {
    'orthogonal'     : 8,
    'isometric'      : 8,
    'hexagonal.flat' : 6,
    'hexagonal.point': 6,
}

# Operation: rotation(angle), reflection(axis)
# Value: angle or axis
SHAPE_EDGE_INFO: \
    dict[Shape, dict[EdgeOp, dict[Rotation | Reflection, tuple[int, bool]]]] = {
    # ORTHOGONAL (SQUARE) -----------------------------------------------------
    "orthogonal": {
        # Rotation
        # | 0     | 90    | 180   | 270   |
        # | 1 2 3 | 3 4 5 | 5 6 7 | 7 8 1 |
        # | 8   4 | 2   6 | 4   8 | 6   2 |
        # | 7 6 5 | 1 8 7 | 3 2 1 | 5 4 3 |
        # Reflection
        # | 0     | 'x'   | 'y'   | 'p'   | 'n'   |
        # | 1 2 3 | 7 6 5 | 3 2 1 | 5 4 3 | 1 8 7 |
        # | 8   4 | 8   4 | 4   8 | 6   2 | 2   6 |
        # | 7 6 5 | 1 2 3 | 5 6 7 | 7 8 1 | 3 4 5 |
        "rotation": {
            0  : (+0, False), # Do Nothing
            90 : (-2, False), # (3, 4, 5, 6, 7, 8, 1, 2)
            180: (-4, False), # (5, 6, 7, 8, 1, 2, 3, 4)
            270: (+2, False), # (7, 8, 1, 2, 3, 4, 5, 6)
        },
        "reflection": {
            'x': (-1, True),  # (7, 6, 5, 4, 3, 2, 1, 8)
            'y': (+3, True),  # (3, 2, 1, 8, 7, 6, 5, 4)
            'p': (-3, True),  # (5, 4, 3, 2, 1, 8, 7, 6)
            'n': (+1, True),  # (1, 8, 7, 6, 5, 4, 3, 2)
        },
    },
    
    # ISOMETRIC ---------------------------------------------------------------
    "isometric": {
        # Rotation
        # | 0         | 90        | 180       | 270       |
        # |     1     |           |     5     |           |
        # |   8   2   |           |   4   6   |           |
        # | 7       3 |     X     | 3       7 |     X     |
        # |   6   4   |           |   2   8   |           |
        # |     5     |           |     1     |           |
        # Reflection
        # | 0         | 'x'       | 'y'       | 'p'       | 'n'       |
        # |     1     |     5     |     1     |           |           |
        # |   8   2   |   6   4   |   2   8   |           |           |
        # | 7       3 | 7       3 | 3       7 |     X     |     X     |
        # |   6   4   |   8   2   |   4   6   |           |           |
        # |     5     |     1     |     5     |           |           |
        "rotation": {
            0  : (+0, False), # Do Nothing
            180: (+4, False), # (5, 6, 7, 8, 1, 2, 3, 4)
        },
        "reflection": {
            'x': (-3, True),  # (5, 4, 3, 2, 1, 8, 7, 6)
            'y': (+1, True),  # (1, 8, 7, 6, 5, 4, 3, 2)
        },
    },
    
    # HEXAGONAL ---------------------------------------------------------------
    "hexagonal.flat": {
        # FLAT
        # Rotation
        # | 0     | 90    | 180   | 270   |
        # |  1 2  |       |  4 5  |       |
        # | 6   3 |   X   | 3   6 |   X   |
        # |  5 4  |       |  2 1  |       |
        # Reflection
        # | 0     | 'x'   | 'y'   | 'p'   | 'n'   |
        # |  1 2  |  5 4  |  2 1  |       |       |
        # | 6   3 | 6   3 | 3   6 |   X   |   X   |
        # |  5 4  |  1 2  |  4 5  |       |       |
        "rotation": {
            0  : (+0, False), # Do Nothing
            180: (+3, False), # (4, 5, 6, 1, 2, 3)
        },
        "reflection": {
            'x': (-1, True),  # (5, 4, 3, 2, 1, 6)
            'y': (+2, True),  # (2, 1, 6, 5, 4, 3)
        },
    },
    
    "hexagonal.point": {
        # POINT
        # Rotation
        # | 0     | 90    | 180   | 270   |
        # |   1   |       |   4   |       |
        # | 6   2 |   X   | 3   5 |   X   |
        # | 5   3 |       | 2   6 |       |
        # |   4   |       |   1   |       |
        # Reflection
        # | 0     | 'x'   | 'y'   | 'p'   | 'n'   |
        # |   1   |   4   |   1   |       |       |
        # | 6   2 | 5   3 | 2   6 |   X   |   X   |
        # | 5   3 | 6   2 | 3   4 |       |       |
        # |   4   |   1   |   4   |       |       |
        "rotation": {
            0  : (+0, False), # Do Nothing
            180: (+3, False), # (4, 5, 6, 1, 2, 3)
        },
        "reflection": {
            'x': (-2, True),  # (4, 3, 2, 1, 6, 5)
            'y': (+1, True),  # (1, 6, 5, 4, 3, 2)
        },
    },
}


