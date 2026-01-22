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

            if self.collision_system.check_collision_with_tiles(entity_id, new_x, new_y):
                continue

            position.x = new_x
            position.y = new_y