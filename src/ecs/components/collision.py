from helpers.constants import GRASS, SAND, WATER, WOOD


class CollisionComponent:
    """
    Defines collision behavior for an entity.
    
    If an entity has this component with tolerance = 0, it's solid (blocks movement).
    """
    
    def __init__(self, tolerance: int = 0):
        """
        Initialize collision component.
        
        Args:
            tolerance: Collision tolerance in pixels.
                      0 = strict collision (solid wall/water)
                      Positive = more forgiving (needs more overlap to collide, for trees/semi-solid)
                      Example: tolerance=12 means need 13+ pixel overlap to collide
        """
        self.tolerance = tolerance