class DirectionComponent:
    def __init__(self):
        self.direction = "down"
        # Map velocity combinations to directions
        self.direction_map = {
            (True, False, False, False): "right",     # +x only
            (False, False, True, False): "left",       # -x only
            (False, True, False, False): "down",       # +y only
            (False, False, False, True): "up",        # -y only
            (True, True, False, False): "down_right",  # +x, +y
            (False, True, True, False): "down_left",    # -x, +y
            (True, False, False, True): "up_right",   # +x, -y
            (False, False, True, True): "up_left",     # -x, -y
        }
    
    def set_direction(self, vx: float, vy: float):
        """Update direction based on velocity"""
        if vx == 0 and vy == 0:
            # No input, keep current direction
            return
        
        # Check for diagonal movement
        moving_right = vx > 0
        moving_left = vx < 0
        moving_down = vy > 0
        moving_up = vy < 0
        
        # Create key for direction lookup
        key = (moving_right, moving_down, moving_left, moving_up)
        
        # Get direction from map, default to current direction if not found
        self.direction = self.direction_map.get(key, self.direction)