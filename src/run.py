import pygame

# Utils
from helpers.constants import CAMERA_WIDTH, CAMERA_HEIGHT, FPS, CAMERA_LERP_SPEED
from world.map_loader import MapFactory
from world.player_factory import PlayerFactory

# Components:
from ecs.components.camera import CameraComponent

# Systems:
from ecs.systems.render_system import RenderingSystem
from ecs.systems.camera_system import CameraSystem
from ecs.systems.event_handler_system import EventHandlerSystem
from ecs.systems.movement_system import MovementSystem
from ecs.systems.animation_system import AnimationSystem
from ecs.systems.player_animation_system import PlayerAnimationSystem

# Entity Manager
from ecs.entity_manager import EntityManager

pygame.init()
pygame.display.set_caption("World of Tiles")

entity_manager = EntityManager()

# Load map
map_factory = MapFactory()
map_factory.load_map(entity_manager, "forest")

# Create player
PlayerFactory.create_player(entity_manager, x=32, y=32)

# Initialize camera
camera_component = CameraComponent(x=0, y=0, viewport_width=CAMERA_WIDTH, viewport_height=CAMERA_HEIGHT, lerp_speed=CAMERA_LERP_SPEED)
camera_system = CameraSystem(camera_component)

# Initialize systems
event_handler_system = EventHandlerSystem(entity_manager)
movement_system = MovementSystem(entity_manager)
animation_system = AnimationSystem(entity_manager)
player_animation_system = PlayerAnimationSystem(entity_manager)

# Initialize rendering
screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
rendering_system = RenderingSystem(screen, entity_manager, camera_component)

# Object that will defines the FPS dinamically:
clock = pygame.time.Clock()

# Fixed timestep for physics (always 1/FPS, regardless of actual rendering FPS)
_FIXED_DELTA_TIME = 1.0 / FPS
time_accumulator = 0.0

while True:
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
        movement_system.update(delta_time=_FIXED_DELTA_TIME)
        time_accumulator -= _FIXED_DELTA_TIME
    
    # Get player position for camera
    player = entity_manager.get_entity_by_id("player")
    if player:
        player_x = player["position"].x
        player_y = player["position"].y
        camera_system.update(target_x=player_x, target_y=player_y, delta_time=delta_time)

    player_animation_system.update()
    
    # Render
    screen.fill((0, 0, 0))
    animation_system.animate(delta_time=delta_time)
    rendering_system.render()
    pygame.display.update()