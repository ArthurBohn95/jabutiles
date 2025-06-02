from PIL import Image
import numpy as np

from jabutiles.configs import Shapes
from jabutiles.shapemask import ShapeMask



class EdgeMask(ShapeMask):
    def __init__(self,
            image: str | Image.Image | np.typing.NDArray = None,
            edges: str = None,
            **params
        ) -> None:
        
        super().__init__(image, **params)
        self.edges: str = edges
    



class EdgeMaskGen:
    pass
