from ecs.entity_manager import EntityManager
from helpers.constants import TILE_SIZE

class CollisionSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def check_collision_with_tiles(self, entity_id: str, new_x: float, new_y: float) -> bool:
        """Checks if the entity at new_x and new_y collides with any non-walkable tiles"""
        tiles = self.entity_manager.get_entities_with_components(["tile", "position", "sprite"])
        object_that_collide = self.entity_manager.get_entity_by_id(entity_id)

        for tile_entity_id, tile_components in tiles:
            tile_component = tile_components["tile"]
            if not tile_component.is_walkable:
                # Check if this specific tile actually collides
                if self._calculate_collision(tile_components["position"], tile_components["sprite"], object_that_collide["sprite"], new_x, new_y):
                    return True  # Collision detected!
        
        return False  # No collision

    def _calculate_collision(self, tile_position, tile_sprite, collider_sprite, new_x, new_y) -> bool:
        """Check if entity at new_x, new_y collides with tile using AABB"""
        # Moving entity bounds
        entity_right = new_x + collider_sprite.width
        entity_bottom = new_y + collider_sprite.height
        
        # Tile bounds
        tile_right = tile_position.x + tile_sprite.width
        tile_bottom = tile_position.y + tile_sprite.height
        
        # AABB collision: check if rectangles overlap
        if (new_x < tile_right and 
            entity_right > tile_position.x and
            new_y < tile_bottom and 
            entity_bottom > tile_position.y):
            return True
        return False