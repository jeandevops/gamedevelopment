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

### 3. EventHandlerSystem

**Purpose**: Processes user input and updates player velocity accordingly

**Dependencies**:
- `EntityManager`: To access the player entity
- Constants: `SPEED`
- `pygame.key.get_pressed()`: For input detection

**How it works**:
```
1. Handle pygame events (QUIT, etc.)
2. Get player entity from EntityManager
3. Check which keys are currently pressed
4. Update player velocity based on input:
   - W → Move up (negative Y)
   - A → Move left (negative X)
   - S → Move down (positive Y)
   - D → Move right (positive X)
5. Set velocity on player's VelocityComponent
```

**Key Method**: `process_events(events)`
```python
def process_events(self, events):
    # Handle pygame events (like QUIT)
    for event in events:
        if event.type == QUIT:
            pygame.quit()
            exit()
    
    # Get player and velocity component
    player = self.entity_manager.get_entity_by_id("player")
    if player is None:
        return
    
    player_velocity = player["velocity"]
    keys = pygame.key.get_pressed()
    
    # Reset velocity
    vx = vy = 0
    
    # Update velocity based on pressed keys
    if keys[K_w]: vy -= SPEED
    if keys[K_s]: vy += SPEED
    if keys[K_a]: vx -= SPEED
    if keys[K_d]: vx += SPEED
    
    player_velocity.set_velocity(vx, vy)
```

**Design Note**: Uses `pygame.key.get_pressed()` instead of event-based input for smooth, continuous movement. Event-based input causes delays and jerky movement.

**Extension Points**:
- Add action buttons (space, enter for interactions)
- Add input buffering for smooth combat

---

### 4. MovementSystem

**Purpose**: Updates entity positions based on their velocities each frame

**Dependencies**:
- `EntityManager`: To query entities with position and velocity components

**How it works**:
```
1. Get all entities with both "position" and "velocity" components
2. For each entity:
   a. Get position and velocity components
   b. Update position: position += velocity * delta_time
   c. This creates smooth movement independent of frame rate
```

**Key Method**: `update(delta_time)`
```python
def update(self, delta_time):
    # Get all moving entities
    entities = self.entity_manager.get_entities_with_components(['position', 'velocity'])
    
    for entity_id, components in entities:
        position = components['position']
        velocity = components['velocity']
        
        # Update position based on velocity and time
        position.x += velocity.vx * delta_time
        position.y += velocity.vy * delta_time
```

**Delta Time**: Fixed timestep for deterministic physics

Delta time is the elapsed time between physics updates. Our game uses a **fixed timestep** approach:

```
FIXED_DELTA_TIME = 1 / FPS  (physics always updates at target FPS)
```

**The Problem with Variable Delta Time:**

If we use actual elapsed time (variable), movement becomes unpredictable:
- Frame 1: `position += 240 × 0.01667 = 4.0` → rounds to 4
- Frame 2: `position += 240 × 0.01662 = 3.99` → rounds to 4  (clock was slightly faster)
- Frame 3: `position += 240 × 0.01672 = 4.01` → rounds to 4  (clock was slightly slower)

The rounding is unpredictable, causing **inconsistent collision gaps**.

**The Solution: Fixed Timestep**

Decouple physics from rendering:
- **Physics runs at fixed 60 FPS** (always consistent)
- **Rendering runs at maximum FPS** (smooth but independent)
- **Time accumulator** buffers actual elapsed time

**How it works:**

```python
FIXED_DELTA_TIME = 1.0 / FPS  # Physics: always 1/FPS second
time_accumulator = 0.0

while True:
    # Rendering loop runs as fast as possible
    milliseconds_elapsed = clock.tick(FPS)  # Limit to target FPS
    delta_time = milliseconds_elapsed / 1000.0
    
    # Accumulate real time
    time_accumulator += delta_time
    
    # Physics loop: runs when enough time accumulated
    while time_accumulator >= FIXED_DELTA_TIME:
        movement_system.update(delta_time=FIXED_DELTA_TIME)  # Always 1/FPS
        time_accumulator -= FIXED_DELTA_TIME
    
    # Rendering always runs
    rendering_system.render()
```

**Visual Example at 120 FPS with FPS=60 (8.3ms per actual frame):**

```
Actual Frame Loop:        [8.3ms]  [8.3ms]  [8.3ms]  [8.3ms]  [8.3ms]
Accumulator grows:         8.3  →   16.6   →  24.9   →   8.3   → 16.6

Physics Update (1/60):              ✓ RUN           ✓ RUN
                       (accumulator = 0)  (accumulator = 8.3)
                       (+16.67ms)         (+16.67ms)

Movement per physics:                   4 px           4 px
```

**Benefits:**

| Aspect | Fixed Timestep | Variable Timestep |
|--------|---|---|
| Physics speed | Always consistent | Varies with FPS |
| Collision detection | Deterministic | Random gaps |
| Reproducibility | Same every run | Depends on frame rate |
| Debugging | Predictable behavior | Hard to reproduce bugs |

**Why velocity is in pixels/second:**

```python
SPEED = 240  # pixels per second (not per frame!)

# At any frame rate, physics always calculates:
movement = 240 × (1/60) = 4 pixels per physics update
```

**Important Notes:**

- `clock.tick(FPS)` **limits** the rendering loop to maximum FPS
  - If loop is fast (e.g., 500 FPS), it sleeps to slow down to FPS
  - If loop is slow (e.g., 30 FPS), it doesn't sleep (you get lower FPS)
  - Returns milliseconds elapsed since last call (varies slightly: 16.6, 16.7, 16.8 ms)
- Physics updates can happen 0, 1, or multiple times per frame
  - At 60 FPS: 1 physics update per frame
  - At 120 FPS: 1 physics update every 2 frames
  - At 30 FPS: 2 physics updates per frame (catches up)
- Tiny variations in elapsed time (±1-2 ms) are absorbed by accumulator
  - Without accumulator, rounding would cause inconsistent collision gaps
  - With fixed timestep, physics is always deterministic

**Extension Points**:
- Add acceleration/deceleration
- Add friction/drag
- Add collision responses
- Add gravity for platformers

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

### VelocityComponent
**Stores**: Velocity (speed) in x and y directions

```python
class VelocityComponent:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy
    
    def set_velocity(self, vx, vy):
        self.vx = vx
        self.vy = vy
```

**Usage**: Any entity that moves (player, enemies, projectiles)

---

### PlayerComponent
**Stores**: Player-specific state and input flags

```python
class PlayerComponent:
    def __init__(self):
        self.is_player = True
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
```

**Usage**: Marks an entity as the player and tracks input state

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
│
├─→ PlayerFactory.create_player(entity_manager, x=400, y=300)
│   └─→ entity_manager.add_entity(
│       entity_id="player",
│       components={
│           "position": PositionComponent(400, 300),
│           "velocity": VelocityComponent(0, 0),
│           "player_component": PlayerComponent(),
│           "tile": TileComponent(...)
│       }
│   )
│
└─→ Initialize systems and game loop starts
```

### Complete Game Loop Flow

```
while True:
│
├─→ event_handler_system.process_events(pygame.event.get())
│   └─→ Updates player velocity based on input
│
├─→ movement_system.update(delta_time=1/60)
│   └─→ Updates all entity positions based on velocity
│
├─→ Get player position for camera
│   └─→ player = entity_manager.get_entity_by_id("player")
│
├─→ camera_system.update(target_x=player.x, target_y=player.y)
│   └─→ Updates camera position to follow player
│
├─→ screen.fill(BLACK)
│   └─→ Clears the screen
│
├─→ rendering_system.render()
│   └─→ Draws all entities with camera offset applied
│
└─→ pygame.display.update()
    └─→ Shows the frame
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

### 2. Entity Factories Outside Entity Manager ✅

**Decision**: `PlayerFactory` and `MapFactory` exist outside the ECS core, creating entities separately

**Why**:
- **Separation of concerns**: Entity creation is distinct from entity management
- **Reusability**: Factories can be called multiple times (e.g., spawn enemies)
- **Testability**: Can test factory behavior independently
- **Clarity**: `run.py` shows explicitly what entities are created
- **Follows Single Responsibility**: EntityManager manages entities, factories create them

**Pattern**:
```python
# Factory only creates entities
class PlayerFactory:
    @staticmethod
    def create_player(entity_manager, x, y):
        # Create entity with all necessary components
        entity_manager.add_entity("player", components)

# In run.py - clear bootstrap flow
MapFactory.load_map(entity_manager, "forest")
PlayerFactory.create_player(entity_manager, 400, 300)
```

**When you'd change this**:
- Runtime entity spawning (enemies, items) - still use factories, pass entity_manager
- Dynamic entity pools - create a factory that manages a pool

---

### 3. MapFactory as Utility, Not System ✅

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

### 4. Screen-Based Camera Movement ✅

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

### 5. Constants in Separate Module ✅

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
- `SPEED`: Player movement speed

---

### 6. Input Handling with Key States ✅

**Decision**: `EventHandlerSystem` uses `pygame.key.get_pressed()` for continuous input detection

**Why**:
- **Smooth movement**: Player moves continuously while key is held
- **Frame-independent**: Works correctly at any frame rate
- **Multi-key support**: Can detect multiple keys pressed simultaneously (for diagonal movement)
- **Better feel**: No input lag or jerkiness

**Alternative (Event-Based - Avoided)**:
```python
# ❌ NOT RECOMMENDED - causes jerky movement
if event.type == KEYDOWN:
    player.move()  # Only moves once per key press
```

**Current Approach (State-Based)**:
```python
# ✅ RECOMMENDED - smooth continuous movement
keys = pygame.key.get_pressed()
if keys[K_w]:
    velocity.vy -= SPEED  # Moves every frame while held
```

**Future Enhancement**: Could add diagonal movement optimization (move_up + move_left = diagonal)

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
