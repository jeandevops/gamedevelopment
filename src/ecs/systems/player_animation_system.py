from ecs.entity_manager import EntityManager

class PlayerAnimationSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    def update(self):
        player = self.entity_manager.get_entity_by_id("player")
        if not player:
            return
        
        velocity = player["velocity"]
        direction = player["direction"]
        animation = player["animated_sprite"]
        sprites = player["sprite_pool"]

        #@TODO: treat exceptionss (the variables can be None)

        direction.set_direction(velocity.vx, velocity.vy)
        
        # Check if moving
        is_moving = velocity.vx != 0 or velocity.vy != 0

        if is_moving:
            animation.sprite = sprites[direction.direction]
            animation.animate = True
        else:
            animation.sprite = sprites["idle_" + direction.direction]
            animation.animate = True