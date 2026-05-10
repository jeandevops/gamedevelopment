"""
SystemManager - Central management of all ECS systems
Creates all systems once and provides them to game modes as needed
"""
from ecs.entity_manager import EntityManager
from ecs.components.camera import CameraComponent
from ecs.systems.render_system import RenderingSystem
from ecs.systems.animation_system import AnimationSystem
from ecs.systems.character_animation_system import CharacterAnimationSystem
from ecs.systems.movement_system import MovementSystem
from ecs.systems.enemies_system import EnemiesSystem
from ecs.systems.battle_ui_system import BattleUISystem
from ecs.systems.camera_system import CameraSystem
from ecs.systems.text_system import DialoguePreparation
from ecs.systems.text_system import DialogueSystem
from helpers.game_state_manager import GameStateManager
from helpers.bitmap_font_loader import BitmapFont
import pygame


class SystemManager:
    """Manages all ECS systems - creates them once, provides them as needed"""
    
    def __init__(self, 
                 entity_manager: EntityManager, 
                 state_manager: GameStateManager, 
                 screen: pygame.Surface,
                 camera_component: CameraComponent,
                 font: BitmapFont):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.screen = screen
        self.camera_component = camera_component
        
        # Create all systems once (never recreated)
        self.rendering_system = RenderingSystem(screen, entity_manager, camera_component, font)
        self.animation_system = AnimationSystem(entity_manager)
        self.character_animation_system = CharacterAnimationSystem(entity_manager)
        self.movement_system = MovementSystem(entity_manager)
        self.enemies_system = EnemiesSystem(entity_manager, state_manager)
        self.battle_ui_system = BattleUISystem(entity_manager, screen)
        self.camera_system = CameraSystem(camera_component)
        self.dialogue_pagination_system = DialoguePreparation(font)
        self.dialogue_system = DialogueSystem()
    
    def get_world_systems(self) -> dict:
        """Get systems needed for world exploration game mode"""
        return {
            "rendering_system": self.rendering_system,
            "animation_system": self.animation_system,
            "character_animation_system": self.character_animation_system,
            "movement_system": self.movement_system,
            "enemies_system": self.enemies_system,
            "camera_system": self.camera_system,
            "entity_manager": self.entity_manager,
            "state_manager": self.state_manager,
        }
    
    def get_battle_systems(self) -> dict:
        """Get systems needed for battle game mode"""
        return {
            "rendering_system": self.rendering_system,
            "animation_system": self.animation_system,
            "character_animation_system": self.character_animation_system,
            "battle_ui_system": self.battle_ui_system,
            "entity_manager": self.entity_manager,
            "state_manager": self.state_manager,
        }
    
    def get_dialog_systems(self) -> dict:
        """Get systems needed for dialogue game mode"""
        return {
            "rendering_system": self.rendering_system,
            "animation_system": self.animation_system,
            "character_animation_system": self.character_animation_system,
            "entity_manager": self.entity_manager,
            "state_manager": self.state_manager,
            "dialogue_system": self.dialogue_system,
            "dialog_pagination_system": self.dialogue_pagination_system,
        }
    
    def update_camera(self, new_camera: CameraComponent) -> None:
        """Update rendering system camera (for battle zoom)"""
        self.rendering_system.camera_component = new_camera
