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
        """Renders all onto the screen"""


        # Render tiles:
        tiles = self._retrieve_tiles()
        for _entity_id, tile_components in tiles:
            if tile_components.get("animated_sprite"):
                tile_components["animated_sprite"].sprite.rect.topleft = (
                    tile_components["position"].x - self.camera_component.x,
                    tile_components["position"].y - self.camera_component.y
                )
                self.screen.blit(tile_components["animated_sprite"].sprite.current_image, tile_components["animated_sprite"].sprite.rect)
            else:
                pygame.draw.rect(
                    self.screen,
                    (255, 0, 255),  # Magenta for missing sprite
                    pygame.Rect(
                        tile_components["position"].x - self.camera_component.x,
                        tile_components["position"].y - self.camera_component.y,
                        tile_components["sprite"].width,
                        tile_components["sprite"].height
                    )
                )

        # Render player (for now, rendering as red rectangle)
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