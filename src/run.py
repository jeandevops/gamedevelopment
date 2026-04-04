import pygame
import os

# Utils
from helpers.constants import CAMERA_WIDTH, CAMERA_HEIGHT, FPS, CAMERA_LERP_SPEED
from helpers.map_file_loader import load_map
from world.map_loader import MapFactory
from world.player_factory import PlayerFactory
from world.enemies_factory import EnemiesFactory

# Components:
from ecs.components.camera import CameraComponent

# Systems:
from ecs.systems.render_system import RenderingSystem
from ecs.systems.camera_system import CameraSystem
from ecs.systems.event_handler_system import EventHandlerSystem
from ecs.systems.event_handler_system import WorldEventHandlerSystem
from ecs.systems.event_handler_system import BattleEventHandlerSystem
from ecs.systems.movement_system import MovementSystem
from ecs.systems.animation_system import AnimationSystem
from ecs.systems.character_animation_system import CharacterAnimationSystem
from ecs.systems.enemies_system import EnemiesSystem

# Entity Manager
from ecs.entity_manager import EntityManager

from helpers.game_state_manager import GameStateManager

class Game:
    def __init__(self,
                 entity_manager: EntityManager,
                 state_manager: GameStateManager,
                 camera_component: CameraComponent,
                 camera_system: CameraSystem,
                 event_handler_system: EventHandlerSystem,
                 movement_system: MovementSystem,
                 animation_system: AnimationSystem,
                 player_animation_system: CharacterAnimationSystem,
                 enemies_system: EnemiesSystem,
                 fullscreen_mode: int,
                 ):
        self.entity_manager = entity_manager
        self.state_manager = state_manager
        self.camera_component = camera_component
        self.camera_system = camera_system
        self.event_handler_system = event_handler_system
        self.movement_system = movement_system
        self.animation_system = animation_system
        self.player_animation_system = player_animation_system
        self.enemies_system = enemies_system
        self.fullscreen_mode = fullscreen_mode
        self.screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT), self.fullscreen_mode)

    def _render(self, delta_time: float):
        # Render and animate:
        self.player_animation_system.update()
        self.screen.fill((0, 0, 0))
        self.animation_system.animate(delta_time=delta_time)
        self.rendering_system.render()
        pygame.display.update()

    def _create_entities(self,
                         map_name: str,
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
        player_factory.create_player(self.entity_manager, *player_initial_position)
        
    def main_loop(self):
        pygame.init()
        pygame.display.set_caption("World of Tiles")

        self.state_manager.change_state("PLAYING")

        # Load first map:
        self._create_entities("forest", self.entity_manager, player_initial_position=(32, 32))

        # Object that will defines the FPS dinamically:
        clock = pygame.time.Clock()
        # Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
        _FIXED_DELTA_TIME = 1.0 / FPS
        time_accumulator = 0.0

        # Retrieve player entity:
        player = self.entity_manager.get_entity_by_id("player")

        while True:
            self.screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT), self.fullscreen_mode)
            self.rendering_system = RenderingSystem(self.screen, self.entity_manager, self.camera_component)
            self.event_handler_system = WorldEventHandlerSystem(self.entity_manager, self.state_manager)

            print("Entering main loop with state:", self.state_manager.get_state())

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

                # Get player position for camera
                if player:
                    player_x = player["position"].x
                    player_y = player["position"].y
                    self.camera_system.update(target_x=player_x, target_y=player_y, delta_time=delta_time)

                self._render(delta_time)

            # When a battle start:
            # Generate battle grid based on the current camera position (visible tiles):
            if self.state_manager.get_state() == "BATTLE_BEGIN":
                self.state_manager.change_state("BATTLE_STARTED")
                # The battle grid will be generated based on player position, not camera, to ensure the battle area is centered around the player:
                battle_grid_x = int(player_x) - (self.camera_component.viewport_width // 4)  # Center battle grid around player
                battle_grid_y = int(player_y) - (self.camera_component.viewport_height // 4)
                battle_grid_width = self.camera_component.viewport_width // 2
                battle_grid_height = self.camera_component.viewport_height // 2
                battle_camera = CameraComponent(x=battle_grid_x, y=battle_grid_y, viewport_width=battle_grid_width, viewport_height=battle_grid_height, lerp_speed=CAMERA_LERP_SPEED)
                #@TODO: To implement the isometric grid in the future:
                #battle_grid = map_factory.generate_battle_grid(battle_grid_x, battle_grid_y, battle_grid_width, battle_grid_height, entity_manager)

                # Close up to the battle area:
                self.screen = pygame.display.set_mode((battle_grid_width, battle_grid_height), self.fullscreen_mode)
                self.rendering_system = RenderingSystem(self.screen, self.entity_manager, battle_camera)


            while self.state_manager.get_state() == "BATTLE_STARTED":
                # Process battle menu events
                self.event_handler_system = BattleEventHandlerSystem(self.entity_manager, self.state_manager)
                self.event_handler_system.process_events(pygame.event.get())
                self._render(delta_time)

class run:
    @staticmethod
    def start():
        # Initialize game components and systems here, then create Game instance and call main loop
        entity_manager = EntityManager()
        state_manager = GameStateManager()
        # Initialize camera
        camera_component = CameraComponent(x=0, y=0, viewport_width=CAMERA_WIDTH, viewport_height=CAMERA_HEIGHT, lerp_speed=CAMERA_LERP_SPEED)
        camera_system = CameraSystem(camera_component, state_manager)
        event_handler_system = WorldEventHandlerSystem(entity_manager, state_manager)
        movement_system = MovementSystem(entity_manager, state_manager)
        animation_system = AnimationSystem(entity_manager)
        player_animation_system = CharacterAnimationSystem(entity_manager)
        enemies_system = EnemiesSystem(entity_manager, state_manager)
        
        # Check for fullscrren mode and set display mode accordingly
        fullscreen_mode = pygame.FULLSCREEN | pygame.SCALED if os.getenv("FULLSCREEN", "0") == "1" else pygame.SCALED
        
        game = Game(
            entity_manager=entity_manager,
            state_manager=state_manager,
            camera_component=camera_component,
            event_handler_system=event_handler_system,
            movement_system=movement_system,
            camera_system=camera_system,
            animation_system=animation_system,
            player_animation_system=player_animation_system,
            enemies_system=enemies_system,
            fullscreen_mode=fullscreen_mode,
        )

        game.main_loop()

if __name__ == "__main__":
    run.start()