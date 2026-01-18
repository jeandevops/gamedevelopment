# Game Development Project - Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [ECS Architecture Explained](#ecs-architecture-explained)
3. [Project Structure](#project-structure)
4. [Systems](#systems)
5. [Components](#components)
6. [Data Flow](#data-flow)
7. [Architecture Decisions](#architecture-decisions)
8. [How to Extend](#how-to-extend)

---

## Overview

This project is a tile-based game engine built with **Entity Component System (ECS)** architecture using Pygame. It demonstrates game development best practices with a clean separation of concerns.

### Key Features
- **Modular ECS architecture** for scalability
- **Camera system** with screen-based navigation
- **Map loading** from JSON files
- **Tile-based rendering** with configurable tile types

---

## ECS Architecture Explained

### What is ECS?

ECS stands for **Entity, Component, System**:

#### Entities
- **What**: Game objects (tiles, player, enemies, etc.)
- **How**: Unique identifiers that hold collections of components
- **Example**: A tile at position (5, 3) is an entity with Position and Tile components

```python
# Entity ID: "tile_3_5"
# Components:
{
    "position": PositionComponent(x=160, y=96),
    "tile": TileComponent(width=32, height=32, tile_type=GRASS)
}
```

#### Components
- **What**: Data containers that describe entity properties
- **How**: Plain objects storing state (no logic)
- **Example**: `PositionComponent` holds x, y coordinates

```python
class PositionComponent:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
```

#### Systems
- **What**: Logic processors that operate on entities with specific components
- **How**: Iterate through entities, read/modify components, perform actions
- **Example**: `RenderingSystem` finds all entities with Tile components and draws them

```python
class RenderingSystem:
    def render(self):
        tiles = self.entity_manager.get_entities_with_component("tile")
        for entity_id, tile_component in tiles:
            # Draw tile...
```

### Why ECS?

| Benefit | Why it matters |
|---------|----------------|
| **Modularity** | Easy to add new features without touching existing code |
| **Reusability** | Components can be mixed and matched in any combination |
| **Performance** | Systems can process only relevant entities |
| **Testability** | Systems are independent and easy to unit test |
| **Scalability** | Grows naturally with project complexity |

---

## Project Structure

```
src/
├── run.py                          # Main entry point
├── ecs/                            # ECS Core
│   ├── entity_manager.py           # Manages all entities
│   ├── components/                 # Component definitions
│   │   ├── position.py             # Position data
│   │   ├── tile.py                 # Tile type data
│   │   └── camera.py               # Camera data
│   └── systems/                    # System logic
│       ├── render_system.py        # Rendering logic
│       └── camera_system.py        # Camera update logic
├── world/                          # Game world setup
│   └── map_loader.py               # Map file parsing
├── helpers/                        # Utilities
│   └── constants.py                # Game configuration
└── assets/
    └── maps/
        └── forest.json             # Map data
```

### Directory Roles

**`ecs/`** - The heart of the engine
- Contains all ECS infrastructure
- Pure logic, no game-specific knowledge
- Reusable for other games

**`world/`** - Game world initialization
- Loads maps from files
- Creates initial entities
- Bootstraps the game state

**`helpers/`** - Shared utilities
- Global constants (tile sizes, colors, paths)
- Configuration values
- Non-ECS helper functions

---

## Systems

### 1. RenderingSystem

**Purpose**: Draws all visible tiles on screen based on camera position

**Dependencies**:
- `EntityManager`: To query entities with tile components
- `Camera`: To calculate drawing offsets
- `pygame`: For drawing primitives

**How it works**:
```
1. Get all entities with "tile" component
2. For each tile entity:
   a. Get its position and tile type
   b. Calculate screen position (position - camera.position)
   c. Draw a rectangle with appropriate color
```

**Key Method**: `render()`
```python
def render(self):
    tiles = self._retrieve_tiles()
    for entity_id, tile_component in tiles:
        # Get world position
        position = self.entity_manager.get_entity_by_id(entity_id)["position"]
        
        # Get tile color
        tile_color = self._get_tile_color(tile_component.tile_type)
        
        # Apply camera offset and draw
        screen_x = position.x - self.camera.x
        screen_y = position.y - self.camera.y
        pygame.draw.rect(self.screen, tile_color, 
                        pygame.Rect(screen_x, screen_y, TILE_SIZE["width"], TILE_SIZE["height"]))
```

**Extension Points**:
- Add sprite rendering instead of colored rectangles
- Implement layer-based rendering (background, objects, UI)
- Add animation support

---

### 2. CameraSystem

**Purpose**: Updates camera position to follow a target with screen-based snapping

**Dependencies**:
- `CameraComponent`: The camera to update
- Constants: `CAMERA_TRIGGER_MARGIN`

**How it works**:
```
1. Called each frame with target position
2. Checks if target is beyond trigger margin from screen center
3. If yes, snaps camera to center target on screen
4. Camera follows in discrete jumps (not smooth)
```

**Key Method**: `update(target_x, target_y)`
```python
def update(self, target_x, target_y):
    # Camera.follow_target() implements the snapping logic
    self.camera.follow_target(target_x, target_y, self.trigger_margin)
```

**Camera Logic**:
```python
# Current screen center
screen_center_x = camera.x + viewport_width / 2

# Distance from center
distance = abs(screen_center_x - target_x)

# If target is beyond margin, snap camera
if distance > trigger_margin:
    camera.x = target_x - viewport_width / 2
```

**Extension Points**:
- Add smooth camera movement (lerp)
- Add camera bounds (don't show beyond map edges)
- Add camera shake effects
- Support multiple targets (split-screen)

---

## Components

### PositionComponent
**Stores**: x, y coordinates in world space

```python
class PositionComponent:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
```

**Usage**: Any entity that has a location

---

### TileComponent
**Stores**: Tile dimensions and type

```python
class TileComponent:
    def __init__(self, width, height, tile_type):
        self.width = width
        self.height = height
        self.tile_type = tile_type  # GRASS, SAND, WATER
```

**Usage**: Ground tiles that should be rendered

**Tile Types** (from `constants.py`):
- `GRASS = 1` → Green
- `SAND = 2` → Brown
- `WATER = 3` → Blue

---

### CameraComponent
**Stores**: Camera position and viewport

```python
class CameraComponent:
    def __init__(self, x, y, viewport_width, viewport_height):
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
```

**Usage**: Manages what portion of the world is visible

---

## Data Flow

### Game Loop Flow

```
run.py (main loop)
│
├─→ pygame event handling
│   └─→ Quit on QUIT event
│
├─→ screen.fill(BLACK)  // Clear screen
│
├─→ camera_system.update(target_x, target_y)
│   └─→ camera.follow_target()  // Update camera position
│
├─→ rendering_system.render()
│   ├─→ Get all tile entities
│   ├─→ For each tile:
│   │   ├─→ Calculate screen position (world pos - camera pos)
│   │   └─→ pygame.draw.rect()
│   └─→ Returns
│
└─→ pygame.display.update()  // Show frame
```

### Entity Creation Flow (Startup)

```
run.py
│
├─→ MapFactory.load_map("forest")
│   ├─→ Read forest.json
│   ├─→ Parse tile characters ("#", ".", "~")
│   └─→ For each tile character:
│       └─→ entity_manager.add_entity(
│           entity_id="tile_row_col",
│           components={
│               "position": PositionComponent(...),
│               "tile": TileComponent(...)
│           }
│       )
└─→ Game loop starts
```

---

## Architecture Decisions

### 1. Camera as System, Not Entity ✅

**Decision**: Camera is managed directly by `CameraSystem`, not added to `EntityManager`

**Why**:
- Camera is a **singleton** - only one per game
- Simpler to manage globally
- Avoids unnecessary entity overhead
- Still follows ECS principles (system manages component)

**Alternative**: Camera could be an entity with components, but that's overkill for a single camera

**When you'd change this**:
- Split-screen multiplayer (multiple cameras)
- Multiple camera modes (zoom, rotation)

---

### 2. MapFactory as Utility, Not System ✅

**Decision**: `MapFactory` exists outside ECS core

**Why**:
- It's a **one-time initialization tool**, not a continuous system
- Doesn't need to run every frame
- Doesn't read/modify runtime components

**What it does**:
- Reads files (IO operation)
- Creates entities in batch
- Then it's done

**Why it's not a system**:
- Systems process entities each frame
- MapFactory is more of a **factory/loader pattern**

---

### 3. Screen-Based Camera Movement ✅

**Decision**: Camera snaps in discrete jumps when target exceeds trigger margin

**Why**:
- Classic game feel (Zelda-style)
- Simple to implement
- Performance-friendly
- Interesting gameplay mechanic

**Trigger Margin Logic**:
```
If distance from screen center > margin:
    Snap camera to new position
Else:
    Keep camera still
```

**Future Evolution**: Could add smooth lerp movement while maintaining this screen-based behavior

---

### 4. Constants in Separate Module ✅

**Decision**: Game configuration lives in `helpers/constants.py`

**Why**:
- Single source of truth
- Easy to balance game (tweak values without code changes)
- Can load from JSON later
- Follows DRY principle

**Config Examples**:
- `TILE_SIZE`: Affects all rendering
- `CAMERA_TRIGGER_MARGIN`: Controls camera behavior
- `TILE_COLORS`: Visual style

---

## How to Extend

### Adding a New Component

```python
# 1. Create file: ecs/components/velocity.py
class VelocityComponent:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy

# 2. Add to entity when creating it
components = {
    "position": PositionComponent(...),
    "velocity": VelocityComponent(vx=5.0, vy=0.0)
}
entity_manager.add_entity(entity_id, components)
```

### Adding a New System

```python
# 1. Create file: ecs/systems/movement_system.py
class MovementSystem:
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
    
    def update(self, delta_time):
        # Get all entities with position and velocity
        moving_entities = self.entity_manager.get_entities_with_component("velocity")
        
        for entity_id, velocity in moving_entities:
            position = self.entity_manager.get_entity_by_id(entity_id)["position"]
            
            # Update position based on velocity
            position.x += velocity.vx * delta_time
            position.y += velocity.vy * delta_time

# 2. Initialize in run.py
movement_system = MovementSystem(entity_manager)

# 3. Call each frame
movement_system.update(delta_time)
```

### Adding a New Tile Type

```python
# 1. Update helpers/constants.py
FOREST = 4  # New tile type
TILE_COLORS[FOREST] = (139, 69, 19)  # Brown

# 2. Update map_loader.py conversion
value_conversion = {
    '.': GRASS,
    '~': WATER,
    '#': SAND,
    'T': FOREST  # New character in maps
}

# 3. Use in map JSON
"# # # T T T #"
```

### Adding a New System to Game Loop

```python
# In run.py

# Initialize
my_system = MySystem(...)

# In game loop
while True:
    # ... event handling ...
    
    my_system.update(...)  # ← Add here
    rendering_system.render()
    
    pygame.display.update()
```

---

## Key Takeaways

1. **ECS separates data from logic** - components store data, systems process it
2. **EntityManager is the hub** - all systems go through it to access entities
3. **Systems run every frame** - utilities like MapFactory don't
4. **Camera is special** - it's a singleton, not an entity
5. **Extend by adding components + systems** - don't modify existing ones

---

## Next Steps

Suggested features to implement:
1. **Player entity** with Position and Tile components
2. **Input system** to move player based on keyboard
3. **Collision system** to prevent player from walking through walls
4. **Animation system** for sprite animation
5. **Audio system** for sound effects
6. **Inventory system** for game items

Good luck! 🚀
