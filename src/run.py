import pygame
import os
from abc import ABC, abstractmethod

# Utils
from helpers.constants import CAMERA_WIDTH, \
                              CAMERA_HEIGHT, \
                              FPS, \
                              CAMERA_LERP_SPEED, \
                              TEXT_SPRITES_PATH
from helpers.map_file_loader import load_map
from helpers.bitmap_font_loader import BitmapFont
from helpers.system_manager import SystemManager
from world.map_loader import MapFactory
from world.player_factory import PlayerFactory
from world.enemies_factory import EnemiesFactory
from world.hud_factory import HUDFactory

# Components:
from ecs.components.camera import CameraComponent
from ecs.components.dialogue import DialogueBoxComponent
from ecs.systems.text_system import DialoguePreparation

# Systems:
from ecs.systems.event_handler_system import DialogEventHandlerSystem
from ecs.systems.event_handler_system import WorldEventHandlerSystem
from ecs.systems.event_handler_system import BattleEventHandlerSystem

# Entity Manager
from ecs.entity_manager import EntityManager

from helpers.game_state_manager import GameStateManager

class Game(ABC):
    @abstractmethod
    def __init__(self, screen: pygame.Surface, **systems):
        self.screen = screen
        self.systems = systems

    @abstractmethod
    def main_loop(self):
        raise NotImplementedError("Subclasses must implement this method")

class WorldExploringGame(Game):
    def __init__(self, screen: pygame.Surface, **systems):
        super().__init__(screen, **systems)
        self.entity_manager = systems["entity_manager"]
        self.state_manager = systems["state_manager"]
        self.camera_system = systems["camera_system"]
        self.event_handler_system = systems.get("event_handler_system")
        self.movement_system = systems["movement_system"]
        self.animation_system = systems["animation_system"]
        self.character_animation_system = systems["character_animation_system"]
        self.enemies_system = systems["enemies_system"]
        self.rendering_system = systems["rendering_system"]

    def _render(self, delta_time: float):
        # Render and animate:
        self.character_animation_system.update()
        self.screen.fill((114, 117, 27))         # Fill with color #72751B:
        self.animation_system.animate(delta_time=delta_time)
        self.rendering_system.render()
        pygame.display.update()
        
    def main_loop(self):
        # Create world-specific event handler (not in system manager)
        self.event_handler_system = WorldEventHandlerSystem(self.entity_manager)
        
        # Object that will defines the FPS dinamically:
        clock = pygame.time.Clock()
        # Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
        _FIXED_DELTA_TIME = 1.0 / FPS
        time_accumulator = 0.0

        # Retrieve player entity:
        player = self.entity_manager.get_entity_by_id("player")

        while self.state_manager.get_state() == "PLAYING":
            # Get elapsed time since last frame and limit to target FPS
            milliseconds_elapsed = clock.tick(FPS)
            delta_time = milliseconds_elapsed / 1000.0
            # Accumulate time
            time_accumulator += delta_time
            # Process input events
            self.event_handler_system.process_events(pygame.event.get())
            # Update movement with fixed timestep, using time_accumulator as a buffer
            # to prevent inconsistent moves during lag spikes
            while time_accumulator >= _FIXED_DELTA_TIME:
                battle_enemy_id = self.enemies_system.update(delta_time=_FIXED_DELTA_TIME)
                self.movement_system.update(delta_time=_FIXED_DELTA_TIME)
                time_accumulator -= _FIXED_DELTA_TIME
            #@TODO: Investigate why this is out of the time_accumulator loops,
            # Cause stutters when lag spikes but prevent stutters when player move slowly
            player_x = player["position"].x
            player_y = player["position"].y
            self.camera_system.update(target_x=player_x, target_y=player_y, delta_time=delta_time)
            self._render(delta_time)

class BattleGame(Game):
    def __init__(self, screen: pygame.Surface, zoom_scale: float = 2.0, **systems):
        super().__init__(screen, **systems)
        self.entity_manager = systems["entity_manager"]
        self.state_manager = systems["state_manager"]
        self.animation_system = systems["animation_system"]
        self.character_animation_system = systems["character_animation_system"]
        self.rendering_system = systems["rendering_system"]
        self.battle_ui_system = systems["battle_ui_system"]
        self.zoom_scale = zoom_scale
        
        # Create a smaller surface for zoomed rendering
        screen_width, screen_height = screen.get_size()
        self.zoomed_width = int(screen_width / zoom_scale)
        self.zoomed_height = int(screen_height / zoom_scale)
        self.zoomed_surface = pygame.Surface((self.zoomed_width, self.zoomed_height))
        
        # Temporarily swap the screen for rendering
        self.original_screen = self.rendering_system.screen
        self.rendering_system.screen = self.zoomed_surface

    def _render(self, delta_time: float):
        # Render and animate:
        self.character_animation_system.update()
        self.zoomed_surface.fill((114, 117, 27))
        self.animation_system.animate(delta_time=delta_time)
        self.rendering_system.render()
        
        # Render battle UI (HP bars) to zoomed surface
        enemy_id = self.state_manager.get_current_enemy()
        if enemy_id:
            self.battle_ui_system.update(enemy_id)
        
        # Scale up the zoomed surface and blit to the main screen
        scaled_surface = pygame.transform.scale(self.zoomed_surface, self.screen.get_size())
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.update()

    def main_loop(self):
        # Create battle-specific event handler (not in system manager)
        self.event_handler_system = BattleEventHandlerSystem(self.entity_manager, self.state_manager)
        
        # Object that will defines the FPS dinamically:
        clock = pygame.time.Clock()
        # Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
        _FIXED_DELTA_TIME = 1.0 / FPS
        time_accumulator = 0.0
        
        current_enemy = self.state_manager.get_current_enemy()

        if not current_enemy:
            raise RuntimeError("No current enemy set in GameStateManager, cannot start battle loop")

        while self.state_manager.get_state() == "BATTLE_STARTED":
            # Get elapsed time since last frame and limit to target FPS
            milliseconds_elapsed = clock.tick(FPS)
            delta_time = milliseconds_elapsed / 1000.0
            # Process battle menu events
            self.event_handler_system.process_events(pygame.event.get())
            self.battle_ui_system.update(current_enemy)
            while time_accumulator >= _FIXED_DELTA_TIME:
                self._render(delta_time)
                time_accumulator -= _FIXED_DELTA_TIME

        # Delete all remaining huds at the end of the battle loop:
        huds = self.entity_manager.get_entities_with_components(["hud"])
        for _entity_id, components in huds:
                self.entity_manager.delete_entity(_entity_id)

        # Delete battle text boxes:

        #if battle won:
        # Restore the original screen to rendering system for next game mode
        self.rendering_system.screen = self.original_screen
        self.state_manager.change_state("PLAYING")

class DialogGame(Game):
    def __init__(self, screen: pygame.Surface, font: BitmapFont, **systems):
        super().__init__(screen, **systems)
        self.entity_manager = systems["entity_manager"]
        self.state_manager = systems["state_manager"]
        self.dialog_pagination_system = systems["dialog_pagination_system"]
        self.dialogue_system = systems["dialogue_system"]
        self.animation_system = systems["animation_system"]
        self.character_animation_system = systems["character_animation_system"]
        self.rendering_system = systems["rendering_system"]

    def _render(self, delta_time: float):
        # Render and animate:
        self.character_animation_system.update()
        self.screen.fill((114, 117, 27))         # Fill with color #72751B:
        self.animation_system.animate(delta_time=delta_time)
        self.rendering_system.render()
        pygame.display.update()
        
    def main_loop(self, interlocutor_id: str):
        # Create dialogue-specific event handler (not in system manager)
        self.event_handler_system = DialogEventHandlerSystem(self.entity_manager, self.state_manager)
        
        # Prepare dialogue if not already prepared
        self.dialog_pagination_system.run(self.entity_manager, interlocutor_id)
        
        # Object that will defines the FPS dinamically:
        clock = pygame.time.Clock()
        # Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
        _FIXED_DELTA_TIME = 1.0 / FPS
        time_accumulator = 0.0

        while self.state_manager.get_state() == "DIALOGUE":
            # Get elapsed time since last frame and limit to target FPS
            milliseconds_elapsed = clock.tick(FPS)
            delta_time = milliseconds_elapsed / 1000.0
            
            # Process dialogue input events
            self.event_handler_system.process_events(pygame.event.get(), interlocutor_id)
            
            # Update dialogue typewriter effect
            self.dialogue_system.update(self.entity_manager, delta_time)
            
            # Render the scene with dialogue
            self._render(delta_time)

class Run:
    @staticmethod
    def _create_entities(map_name: str,
                         entity_manager: EntityManager,
                         player_initial_position: tuple[int, int]
                         ) -> None:
        # Load map data
        map_data = load_map(map_name)

        # Create map factory and load tiles
        map_factory = MapFactory(map_data=map_data)
        map_factory.load_tiles(entity_manager)

        # Create enemies
        enemy_factory = EnemiesFactory(entity_manager, map_data)
        enemy_factory.create_enemies()

        # Create player
        player_factory = PlayerFactory()
        player_factory.create_player(entity_manager, *player_initial_position)

    @staticmethod
    def start():
        # Initialize primary components
        pygame.init()
        pygame.display.set_caption("World of Tiles")
        
        # Setup
        entity_manager = EntityManager()
        state_manager = GameStateManager()
        camera_component = CameraComponent(x=0, y=0, viewport_width=CAMERA_WIDTH, viewport_height=CAMERA_HEIGHT, lerp_speed=CAMERA_LERP_SPEED)
        fullscreen_mode = pygame.FULLSCREEN | pygame.SCALED if os.getenv("FULLSCREEN", "0") == "1" else pygame.SCALED
        font = BitmapFont(
            image_path=TEXT_SPRITES_PATH,
            char_width=8,
            char_height=8,
            chars_order = r"""~1234567890-+!@#$%^&*()_={}[]|\:;"'<,>.?/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"""
        )

        # Create display ONCE
        screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT), fullscreen_mode)
        
        # Load first map
        Run._create_entities("forest", entity_manager, player_initial_position=(32, 32))
        
        # Create system manager ONCE - all systems created here
        system_manager = SystemManager(entity_manager, state_manager, screen, camera_component, font)
        
        state_manager.change_state("PLAYING")

        # Main game loop - alternate between game modes
        while True:
            # WORLD EXPLORATION MODE
            if state_manager.get_state() == "PLAYING":
                world_systems = system_manager.get_world_systems()
                # Restore world camera after battle
                system_manager.update_camera(camera_component)
                world_game = WorldExploringGame(screen, **world_systems)
                world_game.main_loop()

            # DIALOGUE MODE
            if state_manager.get_state() == "DIALOGUE":
                interlocutor = state_manager.get_current_interlocutor()
                if not interlocutor:
                    raise RuntimeError("Interlocutor not found, cannot start dialogue")
                dialog_systems = system_manager.get_dialog_systems()
                dialog_game = DialogGame(screen, font, **dialog_systems)
                dialog_game.main_loop(interlocutor)
            
            # BATTLE SETUP MODE
            if state_manager.get_state() == "BATTLE_BEGIN":
                # Get player position for battle camera
                player = entity_manager.get_entity_by_id("player")
                if player is None:
                    raise RuntimeError("Player entity not found, cannot start battle")
                
                player_x = player["position"].x
                player_y = player["position"].y
                
                # Create battle camera (zoomed in on player area)
                battle_grid_x = int(player_x) - (camera_component.viewport_width // 4)
                battle_grid_y = int(player_y) - (camera_component.viewport_height // 4)
                battle_camera = CameraComponent(
                    x=battle_grid_x, 
                    y=battle_grid_y, 
                    viewport_width=CAMERA_WIDTH, 
                    viewport_height=CAMERA_HEIGHT, 
                    lerp_speed=CAMERA_LERP_SPEED
                )
                
                # Update rendering system to use battle camera
                system_manager.update_camera(battle_camera)
                
                # Get the current enemy
                current_enemy_id = state_manager.get_current_enemy()
                if not current_enemy_id:
                    raise RuntimeError("No current enemy set in GameStateManager")

                current_enemy = entity_manager.get_entity_by_id(current_enemy_id)
                if not current_enemy:
                    raise RuntimeError(f"Enemy entity with ID '{current_enemy_id}' not found, cannot create battle HUD")
                
                # Check if enemy has dialogue - if so, show dialogue first
                if "dialogue" in current_enemy and current_enemy["dialogue"].text:
                    # Create dialogue box for the enemy
                    HUDFactory.create_dialogue_box(entity_manager, current_enemy_id)
                    # Prepare dialogue pagination
                    DialoguePreparation(font).run(entity_manager, current_enemy_id)
                    # Transition to dialogue state
                    state_manager.start_conversation(current_enemy_id)
                else:
                    # No dialogue, go directly to battle
                    HUDFactory.create_battle_hud(entity_manager, current_enemy_id)
                    state_manager.change_state("BATTLE_STARTED")
            
            # BATTLE EXECUTION MODE
            if state_manager.get_state() == "BATTLE_STARTED":
                current_enemy_id = state_manager.get_current_enemy()
                if not current_enemy_id:
                    raise RuntimeError("No current enemy set in GameStateManager")
                
                # Ensure HUD is created (in case we came from dialogue)
                if not entity_manager.get_entity_by_id(f"hp_hud_{current_enemy_id}"):
                    HUDFactory.create_battle_hud(entity_manager, current_enemy_id)
                
                # Start battle with systems
                battle_systems = system_manager.get_battle_systems()
                battle_game = BattleGame(screen, zoom_scale=2.0, **battle_systems)
                battle_game.main_loop()

if __name__ == "__main__":
    Run.start()