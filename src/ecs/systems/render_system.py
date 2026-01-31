from ecs.entity_manager import EntityManager
from ecs.components.camera import CameraComponent
from helpers.constants import TILE_COLORS
import pygame

class RenderingSystem:
    def __init__(self, screen: pygame.Surface, entity_manager: EntityManager, camera_component: CameraComponent):
        self.screen = screen
        self.entity_manager = entity_manager
        self.camera_component = camera_component

    def render(self):
        """Renders all tiles onto the screen"""

        tiles = self._retrieve_tiles()
        for _entity_id, tile_components in tiles:
            tile_color = self._get_tile_color(tile_components["tile"].tile_type)
            if tile_components.get("animated_sprite"):
                tile_components["animated_sprite"].sprite.rect.topleft = (
                    tile_components["position"].x - self.camera_component.x,
                    tile_components["position"].y - self.camera_component.y
                )
                self.screen.blit(tile_components["animated_sprite"].sprite.current_image, tile_components["animated_sprite"].sprite.rect)
            else:
                pygame.draw.rect(
                    self.screen,
                    tile_color,
                    pygame.Rect(
                        tile_components["position"].x - self.camera_component.x,
                        tile_components["position"].y - self.camera_component.y,
                        tile_components["sprite"].width,
                        tile_components["sprite"].height
                    )
                )

        player = self.entity_manager.get_entity_by_id("player")
        pygame.draw.rect(
            self.screen,
            (255, 0, 0),
            pygame.Rect(
                player["position"].x - self.camera_component.x,
                player["position"].y - self.camera_component.y,
                player["sprite"].width,
                player["sprite"].height
            )
        )

    def _retrieve_tiles(self) -> list[tuple[str, dict]]:
        """Retrieves all tile entities from the EntityManager"""
        tiles = self.entity_manager.get_entities_with_components(["tile"])
        return tiles

    def _get_tile_color(self, tile_type: int):
        """Returns the color associated with a tile type"""
        return TILE_COLORS.get(tile_type, (255, 0, 255))  # Default to magenta for unknown types
