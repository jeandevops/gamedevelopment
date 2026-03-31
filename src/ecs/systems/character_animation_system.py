from ecs.entity_manager import EntityManager

class CharacterAnimationSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        # Map velocity combinations to directions
        self.direction_map = {
            (True, False, False, False): "right",     # +x only
            (False, False, True, False): "left",      # -x only
            (False, True, False, False): "down",      # +y only
            (False, False, False, True): "up",        # -y only
            (True, True, False, False): "down_right", # +x, +y
            (False, True, True, False): "down_left",  # -x, +y
            (True, False, False, True): "up_right",   # +x, -y
            (False, False, True, True): "up_left",    # -x, -y
        }

    def _set_direction(self, vx: float, vy: float, current_direction: str) -> str:
        """Update direction based on velocity"""
        if vx == 0 and vy == 0:
            # No input, keep current direction
            return current_direction
        
        # Check for diagonal movement
        moving_right = vx > 0
        moving_left = vx < 0
        moving_down = vy > 0
        moving_up = vy < 0
        
        # Create key for direction lookup
        key = (moving_right, moving_down, moving_left, moving_up)
        
        # Get direction from map, default to current direction if not found
        return self.direction_map.get(key, current_direction)

    def update(self):
        characters = self.entity_manager.get_entities_with_components(["position", "velocity", "direction", "animated_sprite", "sprite_pool"])
        for _character_id, components in characters:
            velocity = components["velocity"]
            direction = components["direction"]
            animation = components["animated_sprite"]
            sprites = components["sprite_pool"]

            #@TODO: treat exceptionss (the variables can be None)

            direction.set_direction(self._set_direction(velocity.vx, velocity.vy, direction.direction))
        
            # Check if moving
            is_moving = velocity.vx != 0 or velocity.vy != 0

            if is_moving:
                animation.sprite = sprites[direction.direction]    
            else:
                animation.sprite = sprites["idle_" + direction.direction]
            animation.animate = True