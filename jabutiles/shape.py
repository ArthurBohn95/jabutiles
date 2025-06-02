from jabutiles.configs import Shapes, Mirrors, Rotations, SHAPE_EDGE_INFO



class Shape:
    def __init__(self,
            shape: Shapes = 'ort',
        ) -> None:
        
        self._shape: Shapes = shape
    
    def can_rotate(self,
            angle: Rotations = 0,
        ) -> bool:
        
        if angle == 0:
            return False
        
        return angle in SHAPE_EDGE_INFO[self._shape]['rotation']
    
    def can_mirror(self,
            axis: Mirrors = None,
        ) -> bool:
        
        if axis is None:
            return False
        
        return axis in SHAPE_EDGE_INFO[self._shape]['mirror']
    
    
    
    
    
    
    