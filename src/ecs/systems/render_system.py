from ecs.entity_manager import EntityManager
from ecs.components.camera import CameraComponent
from helpers.constants import TILE_COLORS, TILE_SIZE
import pygame

class RenderingSystem:
    def __init__(self, screen: pygame.Surface, entity_manager: EntityManager, camera_component: CameraComponent):
        self.screen = screen
        self.entity_manager = entity_manager
        self.camera_component = camera_component

    def render(self):
        """Renders all tiles onto the screen"""

        tiles = self._retrieve_tiles()
        for entity_id, tile_component in tiles:
            position_component = self.entity_manager.get_entity_by_id(entity_id)["position"]
            if position_component is None:
                continue
            tile_color = self._get_tile_color(tile_component.tile_type)
            pygame.draw.rect(
                self.screen,
                tile_color,
                pygame.Rect(
                    position_component.x - self.camera_component.x,
                    position_component.y - self.camera_component.y,
                    TILE_SIZE["width"],
                    TILE_SIZE["height"]
                )
            )

    def _retrieve_tiles(self) -> list[tuple[str, dict]]:
        """Retrieves all tile entities from the EntityManager"""
        tiles = self.entity_manager.get_entities_with_component("tile")
        return tiles

    def _get_tile_color(self, tile_type: int):
        """Returns the color associated with a tile type"""
        return TILE_COLORS.get(tile_type, (255, 0, 255))  # Default to magenta for unknown types
