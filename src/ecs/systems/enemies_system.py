from ecs.entity_manager import EntityManager
from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from ecs.systems.collision_system import CollisionSystem
from helpers.math import euclidean_distance
import random

class EnemiesSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.collision_system = CollisionSystem(entity_manager)
        self.wander_timers = {}  # To track wandering timers for non-aggressive enemies

    def update(self, delta_time: float) -> None:
        """Updates the position of all entities based on their velocity, checking for collisions"""
        player = self.entity_manager.get_entity_by_id("player")
        if player is None:
            return

        player_x = player["position"].x
        player_y = player["position"].y

        for enemy_id, components in self.entity_manager.get_entities_with_components(['position', 'velocity', 'ai_behavior']):
            if "position" not in components or "velocity" not in components or "ai_behavior" not in components:
                continue  # Skip if essential components are missing
            position = components['position']
            velocity = components['velocity']
            ai_behavior = components['ai_behavior']
            agressivity = ai_behavior.aggressive
            vision_range = ai_behavior.vision_range
            interaction_range = ai_behavior.interaction_range
            wander_speed = ai_behavior.wander_speed
            chase_speed = ai_behavior.chase_speed

            # Calculate distance to player
            distance_to_player = euclidean_distance(position.x, position.y, player_x, player_y)

            if distance_to_player <= vision_range:
                # Player is within vision range, set velocity towards player
                if agressivity:
                    self._chase_player(position, player["position"], velocity, chase_speed)
                else:
                    self._wander(enemy_id, position, velocity, delta_time, wander_speed)
            elif distance_to_player <= interaction_range:
                # Player is within interaction range, implement specific behavior
                pass
            else:
                # Enemy keep wandering
                self._wander(enemy_id, position, velocity, delta_time, wander_speed)

    def _chase_player(self, pos: PositionComponent, target_position: PositionComponent, velocity: VelocityComponent, chase_speed: int) -> None:
        """Sets the velocity of the enemy to move towards the player"""
        direction_x = target_position.x - pos.x
        direction_y = target_position.y - pos.y

        magnitude = euclidean_distance(pos.x, pos.y, target_position.x, target_position.y)
        if magnitude > 0:
            velocity.vx = (direction_x / magnitude) * chase_speed
            velocity.vy = (direction_y / magnitude) * chase_speed

    def _wander(self, entity_id: str, pos: PositionComponent, velocity: VelocityComponent, delta_time: float, wander_speed: int) -> None:
        """Implements wandering behavior for non-aggressive enemies"""
        if entity_id not in self.wander_timers:
            self.wander_timers[entity_id] = 0.0
        
        self.wander_timers[entity_id] -= delta_time

        if self.wander_timers[entity_id] <= 0:
            # Choose a random direction to wander in
            angle = random.uniform(0, 2 * 3.14159) # Random angle in radians
            speed = wander_speed
            velocity.vx = speed * 3.14159 * (angle / (2* 3.14159)) # Convert angle to velocity components
            velocity.vy = speed * 3.14159 * ((angle - 3.14159/2) / (2* 3.14159)) # Convert angle to velocity components

            self.wander_timers[entity_id] = random.uniform(1.0, 3.0)  # Wander for 1-3 seconds