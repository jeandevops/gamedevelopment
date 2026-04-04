from ecs.entity_manager import EntityManager
from ecs.systems.collision_system import CollisionSystem

class MovementSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.collision_system = CollisionSystem(entity_manager)

    def update(self, delta_time: float) -> None:
        """Updates the position of all entities based on their velocity, checking for collisions"""

        for entity_id, components in self.entity_manager.get_entities_with_components(['position', 'velocity']):
            position = components['position']
            velocity = components['velocity']

            # Update position based on velocity and delta_time
            new_x = position.x + velocity.vx * delta_time
            new_y = position.y + velocity.vy * delta_time

            # Check full diagonal movement
            if not self.collision_system.check_collision_with_tiles(entity_id, new_x, new_y):
                position.x = round(new_x)
                position.y = round(new_y)
            else:
                # Collision detected - try sliding along one axis
                # Try moving only on X axis
                if not self.collision_system.check_collision_with_tiles(entity_id, new_x, position.y):
                    position.x = round(new_x)
                # Try moving only on Y axis
                elif not self.collision_system.check_collision_with_tiles(entity_id, position.x, new_y):
                    position.y = round(new_y)
                # If both axes collide, don't move (blocked)