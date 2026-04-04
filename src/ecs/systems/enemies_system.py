from ecs.entity_manager import EntityManager
from helpers.game_state_manager import GameStateManager
from ecs.components.position import PositionComponent
from ecs.components.velocity import VelocityComponent
from helpers.math import euclidean_distance
import random
from math import cos, sin, pi

class EnemiesSystem:
    def __init__(self, entity_manager: EntityManager, state_manager: GameStateManager):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.wander_timers = {}  # To track wandering timers for each enemy

    def update(self, delta_time: float) -> None | str:
        """Updates the position of all entities based on their velocity, checking for collisions"""

        if self.state_manager.get_state() != "PLAYING":
            return
        
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

            if distance_to_player > vision_range:
                # Player is out of vision range, enemy should wander
                self._wander(enemy_id, position, velocity, delta_time, wander_speed)

            if agressivity and distance_to_player <= vision_range:
                self._chase_player(position, player["position"], velocity, chase_speed)

            if agressivity and distance_to_player <= interaction_range:
                return self.state_manager.start_battle(enemy_id)

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
            angle = random.uniform(0, 2 * pi)  # Random angle in radians
            velocity.vx = wander_speed * cos(angle)  # X component
            velocity.vy = wander_speed * sin(angle)  # Y component

            self.wander_timers[entity_id] = random.uniform(1.0, 3.0)  # Wander for 1-3 seconds

    # Will be used when we implement enemy death
    def _cleanup_enemy(self, enemy_id: str):
        if enemy_id in self.wander_timers:
            del self.wander_timers[enemy_id]