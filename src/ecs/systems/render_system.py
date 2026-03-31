from ecs.entity_manager import EntityManager
from ecs.components.camera import CameraComponent
import pygame
from helpers.constants import TILE_SIZE
from helpers.logger import logger
from typing import Generator

class RenderingSystem:
    def __init__(self, screen: pygame.Surface, entity_manager: EntityManager, camera_component: CameraComponent):
        self.screen = screen
        self.entity_manager = entity_manager
        self.camera_component = camera_component

    def render(self):
        """Renders all onto the screen"""

        # Render tiles:
        tiles = self._retrieve_tiles()
        visible_tiles = self._filter_visible_tiles(tiles)
        visible_tiles_count = 0
        for _entity_id, tile_components in visible_tiles:
            visible_tiles_count += 1
            if tile_components.get("animated_sprite"):
                tile_components["animated_sprite"].sprite.rect.topleft = (
                    tile_components["position"].x - self.camera_component.x,
                    tile_components["position"].y - self.camera_component.y
                )
                self.screen.blit(tile_components["animated_sprite"].sprite.image, tile_components["animated_sprite"].sprite.rect)

        logger.debug(f"Rendering {len(tiles)} tiles, {visible_tiles_count} visible")

        # Render characters:
        characters = self.entity_manager.get_entities_with_components(["position", "animated_sprite"])
        for _entity_id, components in characters:
            if "tile" in components:
                continue  # Skip tiles, already rendered
            
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