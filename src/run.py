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
from ecs.systems.movement_system import MovementSystem
from ecs.systems.animation_system import AnimationSystem
from ecs.systems.character_animation_system import CharacterAnimationSystem
from ecs.systems.enemies_system import EnemiesSystem

# Entity Manager
from ecs.entity_manager import EntityManager

from helpers.game_state_manager import GameStateManager

pygame.init()
pygame.display.set_caption("World of Tiles")

entity_manager = EntityManager()

state_manager = GameStateManager()
state_manager.change_state("PLAYING")

# Load first map:
map_data = load_map("forest")
map_factory = MapFactory(map_data=map_data)
map_factory.load_tiles(entity_manager)
enemy_factory = EnemiesFactory(entity_manager, map_data)
enemy_factory.create_enemies()

# Create player
player_factory = PlayerFactory()
player_factory.create_player(entity_manager, x=32, y=32)

# Initialize camera
camera_component = CameraComponent(x=0, y=0, viewport_width=CAMERA_WIDTH, viewport_height=CAMERA_HEIGHT, lerp_speed=CAMERA_LERP_SPEED)
camera_system = CameraSystem(camera_component, state_manager)

# Initialize systems
event_handler_system = EventHandlerSystem(entity_manager, state_manager)
movement_system = MovementSystem(entity_manager, state_manager)
animation_system = AnimationSystem(entity_manager)
player_animation_system = CharacterAnimationSystem(entity_manager)
enemies_system = EnemiesSystem(entity_manager, state_manager)

fullscreen_mode = pygame.FULLSCREEN | pygame.SCALED if os.getenv("FULLSCREEN", "0") == "1" else pygame.SCALED

# Object that will defines the FPS dinamically:
clock = pygame.time.Clock()

# Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
_FIXED_DELTA_TIME = 1.0 / FPS
time_accumulator = 0.0

# Retrieve player entity:
player = entity_manager.get_entity_by_id("player")

def _render():
    # Render and animate:
    player_animation_system.update()
    screen.fill((0, 0, 0))
    animation_system.animate(delta_time=delta_time)
    rendering_system.render()
    pygame.display.update()

while True:
    # Initialize rendering system inside the loop to allow switching between world and battle camera:
    screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT), fullscreen_mode)
    rendering_system = RenderingSystem(screen, entity_manager, camera_component)

    while state_manager.get_state() == "PLAYING":
        # Get elapsed time since last frame and limit to target FPS
        milliseconds_elapsed = clock.tick(FPS)
        delta_time = milliseconds_elapsed / 1000.0

        # Accumulate time
        time_accumulator += delta_time

        # Process input events
        event_handler_system.process_events(pygame.event.get())

        # Update movement with fixed timestep, using time_accumulator as a buffer
        # to prevent inconsistent moves during lag spikes
        while time_accumulator >= _FIXED_DELTA_TIME:
            battle_enemy_id = enemies_system.update(delta_time=_FIXED_DELTA_TIME)
            movement_system.update(delta_time=_FIXED_DELTA_TIME)
            time_accumulator -= _FIXED_DELTA_TIME

        # Get player position for camera
        if player:
            player_x = player["position"].x
            player_y = player["position"].y
            camera_system.update(target_x=player_x, target_y=player_y, delta_time=delta_time)
        
        _render()

    # When a battle start:
    # Generate battle grid based on the current camera position (visible tiles):
    if state_manager.get_state() == "BATTLE_BEGIN":
        state_manager.change_state("BATTLE_STARTED")
        # The battle grid will be generated based on player position, not camera, to ensure the battle area is centered around the player:
        battle_grid_x = int(player_x) - (camera_component.viewport_width // 4)  # Center battle grid around player
        battle_grid_y = int(player_y) - (camera_component.viewport_height // 4)
        battle_grid_width = camera_component.viewport_width // 2
        battle_grid_height = camera_component.viewport_height // 2
        battle_camera = CameraComponent(x=battle_grid_x, y=battle_grid_y, viewport_width=battle_grid_width, viewport_height=battle_grid_height, lerp_speed=CAMERA_LERP_SPEED)
        #@TODO: To implement the isometric grid in the future:
        #battle_grid = map_factory.generate_battle_grid(battle_grid_x, battle_grid_y, battle_grid_width, battle_grid_height, entity_manager)
        
        # Close up to the battle area:
        screen = pygame.display.set_mode((battle_grid_width, battle_grid_height), fullscreen_mode)
        rendering_system = RenderingSystem(screen, entity_manager, battle_camera)
        

    while state_manager.get_state() == "BATTLE_STARTED":
        # Process battle menu events
        event_handler_system.process_events(pygame.event.get())
        _render()

