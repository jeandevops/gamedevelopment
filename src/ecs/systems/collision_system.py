from ecs.entity_manager import EntityManager
from helpers.constants import MIN_COLLISION_OVERLAP_PIXELS
from helpers.logger import logger
import pygame

class CollisionSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
        self.min_overlap = MIN_COLLISION_OVERLAP_PIXELS

    def check_collision_with_tiles(self, entity_id: str, new_x: float, new_y: float) -> bool:
        """Checks if the entity at new_x and new_y collides with any tiles that have collision"""
        tiles = self.entity_manager.get_entities_with_components(["collision", "position"])
        moving_entity = self.entity_manager.get_entity_by_id(entity_id)

        if not moving_entity:
            raise ValueError("Entity not found")  # Entity not found, no collision
        
        if "sprite" not in moving_entity and "animated_sprite" not in moving_entity:
            raise ValueError("Entity must have a sprite or animated_sprite component for collision detection")
        
        moving_sprite = moving_entity.get("sprite") or moving_entity.get("animated_sprite")

        for _tile_entity_id, tile_components in tiles:
            collision = tile_components["collision"]
            
            # Check if this specific tile actually collides
            tile_sprite = tile_components.get("sprite") or tile_components.get("animated_sprite")
            if self._calculate_collision(
                tile_position=tile_components["position"],
                tile_sprite=tile_sprite,
                collider_sprite=moving_sprite,
                collider_new_x=new_x,
                collider_new_y=new_y,
                tile_tolerance=collision.tolerance
            ):
                return True  # Collision detected!
        
        return False  # No collision

    def _calculate_collision(self, tile_position, tile_sprite, collider_sprite, collider_new_x, collider_new_y, tile_tolerance: int = 0) -> bool:
        """
        Check if entity at collider_new_x, collider_new_y collides with tile using overlap detection.
        Uses pygame.Rect.clip() to find overlapping area.
        
        Args:
            tile_tolerance: Additional tolerance for this tile type (pixels).
                           Higher values make collision more forgiving (requires more overlap to trigger).
                           Negative values make collision stricter (less overlap needed).
        """
        # Create rectangles for collision detection
        entity_rect = pygame.Rect(collider_new_x, collider_new_y, collider_sprite.width, collider_sprite.height)
        tile_rect = pygame.Rect(tile_position.x, tile_position.y, tile_sprite.width, tile_sprite.height)
        
        # Get the overlapping area
        overlap_rect = entity_rect.clip(tile_rect)
        
        # If no overlap, no collision
        if overlap_rect.width <= 0 or overlap_rect.height <= 0:
            return False
        
        # Calculate required overlap threshold
        # Higher tolerance = need MORE overlap to trigger collision (more forgiving)
        # Negative tolerance = need LESS overlap (stricter collision)
        # For example: tile_tolerance=-1 means any overlap triggers it
        min_required_overlap = max(1, self.min_overlap + tile_tolerance)
        
        collision_detected = (overlap_rect.width >= min_required_overlap and overlap_rect.height >= min_required_overlap)
        
        return collision_detected