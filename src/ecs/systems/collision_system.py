from ecs.entity_manager import EntityManager

class CollisionSystem:
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager

    def check_collision_with_tiles(self, entity_id: str, new_x: float, new_y: float) -> bool:
        """Checks if the entity at new_x and new_y collides with any non-walkable tiles"""
        tiles = self.entity_manager.get_entities_with_components(["tile", "position"])
        moving_entity = self.entity_manager.get_entity_by_id(entity_id)

        if not moving_entity:
            return False  # Entity not found, no collision
        
        if "sprite" not in moving_entity and "animated_sprite" not in moving_entity:
            return False  # No sprite to check collision against
        
        moving_sprite = moving_entity.get("sprite") or moving_entity.get("animated_sprite")

        for _tile_entity_id, tile_components in tiles:
            tile_component = tile_components["tile"]
            if not tile_component.is_walkable:
                # Check if this specific tile actually collides
                tile_component_sprite = tile_components.get("sprite") or tile_components.get("animated_sprite")
                if self._calculate_collision(tile_position=tile_components["position"],
                                             tile_sprite=tile_component_sprite,
                                             collider_sprite=moving_sprite,
                                             collider_new_x=new_x,
                                             collider_new_y=new_y):
                    return True  # Collision detected!
        
        return False  # No collision

    def _calculate_collision(self, tile_position, tile_sprite, collider_sprite, collider_new_x, collider_new_y) -> bool:
        """Check if entity at collider_new_x, collider_new_y collides with tile using AABB"""
        # Moving entity bounds
        entity_right = collider_new_x + collider_sprite.width
        entity_bottom = collider_new_y + collider_sprite.height
        
        # Tile bounds
        tile_right = tile_position.x + tile_sprite.width
        tile_bottom = tile_position.y + tile_sprite.height

        # AABB collision: check if rectangles overlap
        if (collider_new_x < tile_right and 
            entity_right > tile_position.x and
            collider_new_y < tile_bottom and 
            entity_bottom > tile_position.y):
            return True
        return False