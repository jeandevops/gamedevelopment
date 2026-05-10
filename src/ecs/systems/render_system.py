from ecs.entity_manager import EntityManager
from ecs.components.camera import CameraComponent
import pygame
from helpers.constants import TILE_SIZE
from typing import Generator, Optional

class RenderingSystem:
    def __init__(self, screen: pygame.Surface, entity_manager: EntityManager, camera_component: CameraComponent, font=None):
        self.screen = screen
        self.entity_manager = entity_manager
        self.camera_component = camera_component
        self.font = font  # Optional bitmap font for dialogue rendering

    def render(self):
        """Renders all onto the screen with depth sorting for collision tiles and characters"""

        # Get and separate tiles by collision status
        tiles = self._retrieve_tiles()
        visible_tiles = self._filter_visible_tiles(tiles)
        
        non_collision_tiles = []
        collision_tiles = []
        
        for entity_id, tile_components in visible_tiles:
            if self._is_collision_tile(tile_components):
                collision_tiles.append((entity_id, tile_components))
            else:
                non_collision_tiles.append((entity_id, tile_components))
        
        # Render non-collision tiles first (background layer)
        for entity_id, tile_components in non_collision_tiles:
            self._render_tile(entity_id, tile_components)
        
        # Collect collision tiles and characters for depth sorting
        depth_entities = []
        
        # Add collision tiles
        for entity_id, tile_components in collision_tiles:
            depth_entities.append(("tile", entity_id, tile_components))
        
        # Add characters
        characters = self.entity_manager.get_entities_with_components(["position", "animated_sprite", "character"])
        for entity_id, components in characters:
            depth_entities.append(("character", entity_id, components))
        
        # Sort by Y position (lower Y renders first, appears behind)
        depth_entities.sort(key=lambda x: x[2]["position"].y)
        
        # Render depth-sorted entities
        for entity_type, entity_id, components in depth_entities:
            if entity_type == "tile":
                self._render_tile(entity_id, components)
            else:
                self._render_character(entity_id, components)

        # Render HUDs (background first, then bars):
        huds = self.entity_manager.get_entities_with_components(["position", "animated_sprite", "hud"])
        background_huds = []
        bar_huds = []
        
        # Separate backgrounds from bars in a single pass
        for _entity_id, components in huds:
            if "background" in _entity_id:
                background_huds.append((_entity_id, components))
            else:
                bar_huds.append((_entity_id, components))
        
        # Render all backgrounds first
        for _entity_id, components in background_huds:
            self.screen.blit(
                components["animated_sprite"].sprite.image,
                (
                    components["position"].x - self.camera_component.x,
                    components["position"].y - self.camera_component.y
                )
            )

        # Then render all bars on top
        for _entity_id, components in bar_huds:
            self.screen.blit(
                components["animated_sprite"].sprite.image,
                (
                    components["position"].x - self.camera_component.x,
                    components["position"].y - self.camera_component.y
                )
            )
        
        # Render dialogue text if font is available
        if self.font:
            self._render_dialogues()

    def _is_collision_tile(self, tile_components: dict) -> bool:
        """Check if a tile is a collision tile (LANDSCAPING or OBSTACLES layers)"""
        tile = tile_components.get("tile")
        if not tile:
            return False
        
        # Tile types: MARGIN=0, COMMON_TERRAIN=1, LANDSCAPING=2, OBSTACLES=3
        # Collision tiles are LANDSCAPING (2) and OBSTACLES (3)
        return tile.tile_type in [2, 3]

    def _render_tile(self, entity_id: str, tile_components: dict):
        """Render a single tile"""
        if tile_components.get("animated_sprite"):
            tile_components["animated_sprite"].sprite.rect.topleft = (
                tile_components["position"].x - self.camera_component.x,
                tile_components["position"].y - self.camera_component.y
            )
            self.screen.blit(tile_components["animated_sprite"].sprite.image, tile_components["animated_sprite"].sprite.rect)

    def _render_character(self, entity_id: str, components: dict):
        """Render a single character"""
        self.screen.blit(
            components["animated_sprite"].sprite.image,
            (
                components["position"].x - self.camera_component.x,
                components["position"].y - self.camera_component.y
            )
        )


    def _retrieve_tiles(self) -> list[tuple[str, dict]]:
        """Retrieves all tile entities from the EntityManager"""
        tiles = self.entity_manager.get_entities_with_components(["tile"])
        return tiles

    def _filter_visible_tiles(self, tiles: list[tuple[str, dict]]) -> Generator[tuple[str, dict], None, None]:
        """Filters tiles to only those visible within the camera viewport"""
        margin = TILE_SIZE["width"]  # One tile margin

        cam_x, cam_y = self.camera_component.x, self.camera_component.y
        screen_width, screen_height = self.screen.get_size()

        for entity_id, components in tiles:
            pos = components["position"]
            # If tile is within the camera viewport plus margin
            if (cam_x - margin <= pos.x <= cam_x + screen_width + margin and
                cam_y - margin <= pos.y <= cam_y + screen_height + margin):
                yield entity_id, components

    def _render_dialogues(self):
        """Render dialogue text for all entities that have dialogue components.
        
        Searches for entities with both 'dialogue' and 'dialogue_box' components,
        then renders the visible characters of the current page using the bitmap font.
        """
        # Get all entities with dialogue and dialogue_box components
        dialogue_entities = self.entity_manager.get_entities_with_components(["dialogue", "dialogue_box"])
        
        for entity_id, components in dialogue_entities:
            dialogue = components["dialogue"]
            dialogue_box = components["dialogue_box"]
            
            # Only render if there are pages to display
            if not dialogue.pages or dialogue.current_page >= len(dialogue.pages):
                continue
            
            # Get current page text
            current_page = dialogue.pages[dialogue.current_page]
            
            # Render each line of the current page
            for line_idx, line in enumerate(current_page):
                y_offset = line_idx * self.font.char_height
                
                # Render visible characters of this line
                visible_in_line = min(
                    dialogue.visible_chars - sum(len(current_page[i]) for i in range(line_idx)),
                    len(line)
                )
                
                for char_idx in range(visible_in_line):
                    char = line[char_idx]
                    if char not in self.font.chars:
                        continue
                    
                    x_offset = char_idx * self.font.char_width
                    screen_x = dialogue_box.rect.x + x_offset - self.camera_component.x
                    screen_y = dialogue_box.rect.y + y_offset - self.camera_component.y
                    
                    # Only render if within screen bounds
                    if -self.font.char_width <= screen_x < self.screen.get_width() and \
                       -self.font.char_height <= screen_y < self.screen.get_height():
                        self.screen.blit(self.font.chars[char], (screen_x, screen_y))