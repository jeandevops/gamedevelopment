# Game Development Project - Architecture Documentation

A tile-based game engine built with **Entity Component System (ECS)** architecture using Pygame.

## Quick Navigation

- **[SYSTEMS.md](SYSTEMS.md)** - How rendering, camera, input, movement, collision, and animation work
- **[COMPONENTS.md](COMPONENTS.md)** - Reference for Position, Tile, Camera, Velocity, Player, AnimatedSprite components
- **[PHYSICS.md](PHYSICS.md)** - Delta time, fixed timestep, and frame-rate independent movement
- **[ANIMATION.md](ANIMATION.md)** - Sprite pooling, frame-rate independent animation, and timing
- **[LERP_MATH.md](LERP_MATH.md)** - Linear interpolation math and delta time explained
- **[CULLING.md](CULLING.md)** - Viewport culling optimization technique
- **[ROADMAP.md](ROADMAP.md)** - Project phases and progress tracking

---

## Overview

### Key Features
- **Modular ECS architecture** for scalability
- **Camera system** with screen-based navigation (Zelda-style)
- **Map loading** from JSON files
- **Tile-based rendering** with configurable tile types
- **Collision detection** with AABB physics
- **Frame-rate independent movement** with fixed timestep

### Technology Stack
- **Pygame-CE 2.5.6** - Game library
- **Python 3.12.3** - Language
- **JSON** - Map format
- **SDL 2.32.10** - Graphics backend (via Pygame)

---

## ECS Architecture

### What is ECS?

**Entity, Component, System** is a data-driven architecture:

#### Entities
Game objects identified by unique IDs, containing a collection of components.

```python
entity_id = "player"
components = {
    "position": PositionComponent(x=100, y=100),
    "velocity": VelocityComponent(vx=0, vy=0),
    "player": PlayerComponent()
}
```

#### Components
Pure data holders describing entity properties. No logic, just state.

```python
class PositionComponent:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
```

#### Systems
Logic processors that operate on entities with specific components.

```python
class MovementSystem:
    def update(self, delta_time):
        # Get all entities with position and velocity
        entities = entity_manager.get_entities_with_components(['position', 'velocity'])
        
        for entity_id, components in entities:
            # Process movement
            position = components['position']
            velocity = components['velocity']
            position.x += velocity.vx * delta_time
```

### Why ECS?

| Benefit | Why It Matters |
|---------|----------------|
| **Modularity** | Easy to add features without touching existing code |
| **Reusability** | Components mix and match in any combination |
| **Performance** | Systems process only relevant entities |
| **Testability** | Systems are independent and easy to test |
| **Scalability** | Grows naturally with project complexity |

---

## Project Structure

```
src/
├── run.py                          # Main entry point
├── ecs/                            # ECS Core
│   ├── entity_manager.py           # Entity storage & queries
│   ├── components/                 # Component definitions
│   │   ├── position.py
│   │   ├── tile.py
│   │   ├── camera.py
│   │   ├── velocity.py
│   │   ├── player.py
│   │   └── sprite.py
│   └── systems/                    # System logic
│       ├── render_system.py
│       ├── camera_system.py
│       ├── event_handler_system.py
│       ├── movement_system.py
│       └── collision_system.py
├── world/                          # Game initialization
│   ├── map_loader.py
│   └── player_factory.py
├── helpers/
│   └── constants.py                # Configuration
└── assets/
    └── maps/
        └── forest.json
```

### Directory Roles

**`ecs/`** - Engine core
- Pure ECS infrastructure
- No game-specific knowledge
- Reusable for other games

**`world/`** - Game world setup
- Map loading from JSON
- Entity creation (factories)
- Bootstrap

**`helpers/`** - Utilities
- Constants (tile sizes, colors, speeds)
- Configuration

---

## System Overview

See **[SYSTEMS.md](SYSTEMS.md)** for detailed documentation.

### Core Systems

1. **RenderingSystem** - Draws all visible entities with camera offset
2. **CameraSystem** - Follows player with screen-based snapping
3. **EventHandlerSystem** - Converts keyboard input to player velocity
4. **MovementSystem** - Updates positions with collision checking
5. **CollisionSystem** - AABB collision detection between entities and tiles

### Data Flow

```
Main Loop
├─ Input: EventHandlerSystem
│  └─ Updates player velocity
│
├─ Physics: MovementSystem  
│  └─ Updates position with collision checking
│
├─ Camera: CameraSystem
│  └─ Follows player
│
└─ Render: RenderingSystem
   └─ Draws entities with camera offset
```

---

## Components

See **[COMPONENTS.md](COMPONENTS.md)** for detailed reference.

### Core Components

| Component | Purpose | Entities |
|-----------|---------|----------|
| **Position** | World coordinates (x, y) | Everything |
| **Tile** | Tile type and walkability | Ground tiles |
| **Velocity** | Movement speed (vx, vy) | Moving entities |
| **Player** | Player identification | Player only |
| **Sprite** | Visual dimensions | Visual entities |
| **Camera** | Viewport (position, size) | Camera only |

---

## Physics & Movement

See **[PHYSICS.md](PHYSICS.md)** for detailed explanation.

### Fixed Timestep

Physics runs at fixed `1/FPS` delta_time:
- Ensures deterministic, consistent movement
- Eliminates random collision gaps
- Physics independent of rendering FPS

### Time Accumulator

```python
# In run.py
FIXED_DELTA_TIME = 1.0 / FPS
time_accumulator = 0.0

while True:
    milliseconds = clock.tick(FPS)
    time_accumulator += milliseconds / 1000.0
    
    while time_accumulator >= FIXED_DELTA_TIME:
        movement_system.update(FIXED_DELTA_TIME)
        time_accumulator -= FIXED_DELTA_TIME
    
    rendering_system.render()
```

---

## Architecture Decisions

### 1. Camera as System, Not Entity ✅

Camera is managed by `CameraSystem`, not `EntityManager`. It's a singleton—simpler and more efficient than entity overhead.

**When to change**: Multi-camera support (split-screen, multiple viewports)

### 2. Entity Factories Outside ECS ✅

`MapFactory` and `PlayerFactory` exist outside core, creating entities separately.

**Benefits**:
- Clear separation: Factories create, EntityManager manages
- Reusable: Can spawn entities multiple times
- Testable: Factory behavior independent of manager

### 3. MapFactory as Utility, Not System ✅

`MapFactory` is a one-time loader, not a continuous system (systems run every frame).

### 4. Screen-Based Camera ✅

Camera snaps in discrete jumps (Zelda-style), not smooth movement.

**Benefits**:
- Classic game feel
- Simple implementation
- Interesting gameplay mechanic

### 5. Constants in Separate Module ✅

Configuration in `helpers/constants.py` for easy balancing.

### 6. State-Based Input ✅

Uses `pygame.key.get_pressed()` for smooth, continuous movement (not event-based).

**Benefits**:
- No input lag
- Multi-key support (diagonal movement)
- Smooth player control

---

## How to Extend

### Add a New Component

```python
# src/ecs/components/health.py
class HealthComponent:
    def __init__(self, max_hp=100):
        self.max_hp = max_hp
        self.current_hp = max_hp
    
    def take_damage(self, damage):
        self.current_hp -= damage

# Add to entity when creating
components = {
    "position": PositionComponent(...),
    "health": HealthComponent(max_hp=100)
}
```

### Add a New System

```python
# src/ecs/systems/damage_system.py
class DamageSystem:
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
    
    def update(self):
        entities = self.entity_manager.get_entities_with_components(['health'])
        for entity_id, components in entities:
            health = components['health']
            if not health.is_alive():
                # Process dead entities

# Initialize in run.py and call in game loop
```

### Add a New Tile Type

```python
# constants.py
FOREST = 4
TILE_COLORS[FOREST] = (139, 69, 19)

# map_loader.py
value_conversion = {
    '.': GRASS,
    '~': WATER,
    '#': SAND,
    'T': FOREST
}
```

---

## Game Loop Flow

```python
while True:
    # Step 1: Timing
    milliseconds_elapsed = clock.tick(FPS)
    time_accumulator += milliseconds_elapsed / 1000.0
    
    # Step 2: Input
    event_handler_system.process_events(pygame.event.get())
    
    # Step 3: Physics (fixed timestep)
    while time_accumulator >= FIXED_DELTA_TIME:
        movement_system.update(FIXED_DELTA_TIME)
        time_accumulator -= FIXED_DELTA_TIME
    
    # Step 4: Camera
    player = entity_manager.get_entity_by_id("player")
    camera_system.update(player["position"].x, player["position"].y)
    
    # Step 5: Rendering
    screen.fill((0, 0, 0))
    rendering_system.render()
    pygame.display.update()
```

---

## Debugging Tips

### Check Entity State
```python
# See what components an entity has
player = entity_manager.get_entity_by_id("player")
print(player.keys())  # ['position', 'velocity', 'player', 'sprite']
```

### Query Entities
```python
# Get all moving entities
moving = entity_manager.get_entities_with_components(['velocity'])

# Get all tiles
tiles = entity_manager.get_entities_with_components(['tile'])
```

### Collision Debug
- Look for collision detection messages (enabled in CollisionSystem)
- Check that non-walkable tiles have `is_walkable() = False`
- Verify collision box dimensions match sprite size

---

## Next Steps

See **[ROADMAP.md](ROADMAP.md)** for planned features and completed phases.

Current focus areas:
1. Sprite rendering (load PNG images)
2. Enemy AI
3. Inventory system
4. Combat mechanics
5. Audio system

---

## Key Concepts

- **Delta Time** - Elapsed seconds, ensures frame-rate independent movement
- **Fixed Timestep** - Physics always uses 1/FPS for deterministic behavior
- **AABB Collision** - Axis-Aligned Bounding Box, simple rectangle overlap test
- **Entity Composition** - Entities are collections of components, not class hierarchies
- **System-Driven** - Logic flows through systems, not objects

