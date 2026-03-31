from ecs.entity_manager import EntityManager
from ecs.systems.collision_system import CollisionSystem

class EnemiesSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.collision_system = CollisionSystem(entity_manager)

    def update(self, delta_time: float) -> None:
        """Updates the position of all entities based on their velocity, checking for collisions"""
        player = self.entity_manager.get_entity_by_id("player")
        if player is None:
            return
        for enemy_id, components in self.entity_manager.get_entities_with_components(['enemy']):
            pass
        # For each enemy, check if player is within vision range of the enemy

        # If so, calculate path to player and set velocity towards player

        # Update position based on velocity and delta_time, checking for collisions