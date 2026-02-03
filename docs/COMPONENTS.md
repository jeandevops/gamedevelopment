# Components Reference

Detailed documentation for all entity components.

## Table of Contents
1. [PositionComponent](#positioncomponent)
2. [TileComponent](#tilecomponent)
3. [CameraComponent](#cameracomponent)
4. [VelocityComponent](#velocitycomponent)
5. [PlayerComponent](#playercomponent)
6. [SpriteComponent](#spritecomponent)
7. [AnimatedSpriteComponent](#animatedspritecomponent)

---

## PositionComponent

**Purpose**: Stores an entity's position in world space

**File**: `src/ecs/components/position.py`

**Properties**:
- `x` (float) - X coordinate in world space
- `y` (float) - Y coordinate in world space

**Code**:
```python
class PositionComponent:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
```

**Usage**: Every entity that exists in the world needs this
- Tiles
- Player
- Enemies
- Items
- Projectiles

**Example**:
```python
position = PositionComponent(x=160, y=96)  # Position in pixels
print(position.x, position.y)  # 160, 96

# Update position
position.x += 4  # Move right 4 pixels
position.y -= 2  # Move up 2 pixels
```

**Related Systems**:
- `RenderingSystem` - reads position to draw on screen (with camera offset)
- `MovementSystem` - updates position based on velocity
- `CameraSystem` - reads player position to follow with camera

---

## TileComponent

**Purpose**: Defines what type of tile this entity is

**File**: `src/ecs/components/tile.py`

**Properties**:
- `tile_type` (int) - Type of tile (GRASS, SAND, WATER)
- `width` (int) - Tile width in pixels
- `height` (int) - Tile height in pixels

**Methods**:
- `is_walkable()` - Returns True if entity can walk on this tile

**Code**:
```python
class TileComponent:
    def __init__(self, width, height, tile_type):
        self.width = width
        self.height = height
        self.tile_type = tile_type
    
    def is_walkable(self):
        return self.tile_type == GRASS
```

**Tile Types** (from `constants.py`):
```python
GRASS = 1   # Walkable, green
SAND = 2    # Non-walkable, brown
WATER = 3   # Non-walkable, blue
```

**Usage**: Every tile entity needs this
- Ground tiles (grass, sand, water)
- Walls
- Obstacles

**Example**:
```python
grass_tile = TileComponent(width=32, height=32, tile_type=GRASS)
print(grass_tile.is_walkable())  # True

water_tile = TileComponent(width=32, height=32, tile_type=WATER)
print(water_tile.is_walkable())  # False
```

**Related Systems**:
- `RenderingSystem` - reads tile_type to determine color
- `CollisionSystem` - checks is_walkable() before allowing movement

---

## CameraComponent

**Purpose**: Stores camera position and viewport dimensions

**File**: `src/ecs/components/camera.py`

**Properties**:
- `x` (float) - Camera position X
- `y` (float) - Camera position Y
- `viewport_width` (int) - Width of visible area
- `viewport_height` (int) - Height of visible area

**Methods**:
- `follow_target(target_x, target_y, trigger_margin)` - Snaps camera to follow target

**Code**:
```python
class CameraComponent:
    def __init__(self, x, y, viewport_width, viewport_height):
        self.x = x
        self.y = y
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
    
    def follow_target(self, target_x, target_y, trigger_margin):
        # Calculate screen center
        screen_center_x = self.x + self.viewport_width / 2
        screen_center_y = self.y + self.viewport_height / 2
        
        # Distance from center
        distance_x = abs(screen_center_x - target_x)
        distance_y = abs(screen_center_y - target_y)
        
        # Snap camera if target exceeds margin
        if distance_x > trigger_margin:
            self.x = target_x - self.viewport_width / 2
        
        if distance_y > trigger_margin:
            self.y = target_y - self.viewport_height / 2
```

**Usage**: There's typically one camera per game (singleton)

**Example**:
```python
camera = CameraComponent(
    x=0, 
    y=0, 
    viewport_width=800, 
    viewport_height=600
)

# Follow player with 200px margin
camera.follow_target(
    target_x=player_x,
    target_y=player_y,
    trigger_margin=200
)
```

**Camera Behavior** (Zelda-style):
```
When target is near screen center (within margin):
- Camera doesn't move

When target moves beyond margin:
- Camera snaps to re-center target
- Creates "room-like" camera movement
```

**Related Systems**:
- `CameraSystem` - calls follow_target() each frame
- `RenderingSystem` - uses camera.x and camera.y to offset drawing

---

## VelocityComponent

**Purpose**: Stores movement speed in X and Y directions

**File**: `src/ecs/components/velocity.py`

**Properties**:
- `vx` (float) - Velocity in X direction (pixels per second)
- `vy` (float) - Velocity in Y direction (pixels per second)

**Methods**:
- `set_velocity(vx, vy)` - Sets both velocity components

**Code**:
```python
class VelocityComponent:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy
    
    def set_velocity(self, vx, vy):
        self.vx = vx
        self.vy = vy
```

**Units**: pixels per second (not per frame!)

**Example**:
```python
# Player moving right at 240 pixels/second
velocity = VelocityComponent(vx=240, vy=0)

# Movement per physics update (at 60 FPS):
# distance = 240 × (1/60) = 4 pixels
```

**Direction Convention**:
```
       y
       ↑
       |  -vy (up)
       |
─vx ←──┼──→ +vx (right)
       |
       |  +vy (down)
       ↓
```

**Typical Values**:
```python
# Standing still
velocity.set_velocity(0, 0)

# Moving right
velocity.set_velocity(240, 0)  # 240 pixels/second

# Moving up-left (diagonal)
velocity.set_velocity(-240, -240)  # Diagonal movement
```

**Related Systems**:
- `EventHandlerSystem` - sets velocity based on input
- `MovementSystem` - reads velocity to update position

---

## PlayerComponent

**Purpose**: Marks an entity as the player and stores input state

**File**: `src/ecs/components/player.py`

**Properties**:
- `is_player` (bool) - Always True, used to identify player
- `moving_up` (bool) - Is moving up?
- `moving_down` (bool) - Is moving down?
- `moving_left` (bool) - Is moving left?
- `moving_right` (bool) - Is moving right?

**Code**:
```python
class PlayerComponent:
    def __init__(self):
        self.is_player = True
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
```

**Usage**: The player entity has this (only one player)

**Example**:
```python
# Create player
player_component = PlayerComponent()
print(player_component.is_player)  # True

# Track input state
player_component.moving_right = True
player_component.moving_up = True
```

**Why Separate Component?**

Makes the player easy to identify:
```python
# Find player by looking for this component
player = entity_manager.get_entities_with_components(["player"])
```

**Related Systems**:
- `EventHandlerSystem` - could update moving_* flags based on input
- `CameraSystem` - uses player component to know what to follow

---

## SpriteComponent

**Purpose**: Stores sprite dimensions and image path for rendering

**File**: `src/ecs/components/sprite.py`

**Properties**:
- `width` (int) - Sprite width in pixels
- `height` (int) - Sprite height in pixels
- `image_path` (str) - Path to image file (optional)

**Methods**:
- `get_dimensions()` - Returns (width, height) tuple
- `set_image(image_path)` - Sets image path

**Code**:
```python
class SpriteComponent:
    def __init__(self, width, height, image_path=None):
        self.width = width
        self.height = height
        self.image_path = image_path
    
    def get_dimensions(self):
        return (self.width, self.height)
    
    def set_image(self, image_path):
        self.image_path = image_path
```

**Usage**: Any entity that needs collision detection or sprite rendering

**Example**:
```python
# Tile sprite
sprite = SpriteComponent(width=32, height=32, image_path=None)

# Player sprite with image
player_sprite = SpriteComponent(
    width=32, 
    height=32, 
    image_path="assets/sprites/player.png"
)

# Get dimensions for collision
width, height = player_sprite.get_dimensions()
```

**Related Systems**:
- `RenderingSystem` - uses width, height to draw; could use image_path for sprite rendering
- `CollisionSystem` - uses width, height to calculate bounding box

---

## AnimatedSpriteComponent

```python
class AnimatedSpriteComponent:
    sprite: AnimatedSprite          # Shared sprite (images)
    frame_index: int                # Current frame
    elapsed_time: float             # Time since last frame change (ms)
    frame_duration: int             # Time per frame (ms, default 150)
    animate: bool                   # Animation enabled?
```

**Key**: `sprite` is shared, `frame_index` is unique per tile

### AnimatedSprite

```python
class AnimatedSprite(pygame.sprite.Sprite):
    images: list[pygame.Surface]    # All frames
    image: pygame.Surface           # Current frame (updated by AnimationSystem)

    def get_frame(self, frame_index: int) -> pygame.Surface:
        return self.images[frame_index % len(self.images)]
```

**Key**: Stateless (no animation logic)

---

## Component Relationships

### Entity Composition Examples

**A Tile Entity** (non-walkable):
```python
{
    "position": PositionComponent(x=96, y=128),
    "tile": TileComponent(width=32, height=32, tile_type=WATER),
    "sprite": SpriteComponent(width=32, height=32)
}
```

**The Player Entity**:
```python
{
    "position": PositionComponent(x=100, y=100),
    "velocity": VelocityComponent(vx=0, vy=0),
    "player": PlayerComponent(),
    "sprite": SpriteComponent(width=32, height=32)
}
```

**The Camera Entity** (managed by CameraSystem):
```python
{
    "camera": CameraComponent(x=0, y=0, viewport_width=800, viewport_height=600)
}
```

### Component Dependency Graph

```
PositionComponent
    ↓
Used by: RenderingSystem, MovementSystem, CameraSystem

VelocityComponent
    ↓
Used by: EventHandlerSystem (writes), MovementSystem (reads)

TileComponent
    ↓
Used by: RenderingSystem, CollisionSystem

SpriteComponent
    ↓
Used by: RenderingSystem, CollisionSystem

PlayerComponent
    ↓
Used by: EventHandlerSystem (identifies player)

CameraComponent
    ↓
Used by: CameraSystem, RenderingSystem
```

---

## Creating Custom Components

To add a new component:

1. **Create file** in `src/ecs/components/`
```python
# src/ecs/components/health.py
class HealthComponent:
    def __init__(self, max_hp=100):
        self.max_hp = max_hp
        self.current_hp = max_hp
    
    def take_damage(self, damage):
        self.current_hp -= damage
    
    def is_alive(self):
        return self.current_hp > 0
```

2. **Add to entities** when creating them
```python
components = {
    "position": PositionComponent(...),
    "health": HealthComponent(max_hp=100)
}
entity_manager.add_entity(entity_id, components)
```

3. **Query in systems**
```python
# In a damage system
entities = entity_manager.get_entities_with_components(["health", "position"])
for entity_id, components in entities:
    health = components["health"]
    if health.is_alive():
        # Process alive entities
```

