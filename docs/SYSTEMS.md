# Systems Documentation

Detailed reference for all game systems.

## Table of Contents
1. [RenderingSystem](#renderingsystem)
2. [CameraSystem](#camerasystem)
3. [EventHandlerSystem](#eventhandlersystem)
4. [MovementSystem](#movementsystem)
5. [CollisionSystem](#collisionsystem)

---

## RenderingSystem

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

## CameraSystem

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

## EventHandlerSystem

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

## MovementSystem

**Purpose**: Updates entity positions based on their velocities with collision checking

**Dependencies**:
- `EntityManager`: To query entities with position and velocity components
- `CollisionSystem`: To detect collisions before movement

**How it works**:
```
1. Get all entities with both "position" and "velocity" components
2. For each entity:
   a. Get position and velocity components
   b. Calculate new position: new_x = x + vx * delta_time
   c. Check collision at new position
   d. If no collision, update to new position
   e. If collision, keep old position (blocked)
```

**Key Method**: `update(delta_time)`
```python
def update(self, delta_time: float) -> None:
    """Updates the position of all entities based on their velocity, checking for collisions"""
    for entity_id, components in self.entity_manager.get_entities_with_components(['position', 'velocity']):
        position = components['position']
        velocity = components['velocity']

        # Update position based on velocity and delta_time
        new_x = position.x + velocity.vx * delta_time
        new_y = position.y + velocity.vy * delta_time

        if self.collision_system.check_collision_with_tiles(entity_id, new_x, new_y):
            continue  # Collision detected, don't move

        position.x = round(new_x)
        position.y = round(new_y)
```

**Extension Points**:
- Add acceleration/deceleration
- Add friction/drag
- Add gravity for platformers
- Add sliding movement along walls

---

## CollisionSystem

**Purpose**: Detects collisions between moving entities and static tiles using AABB

**Dependencies**:
- `EntityManager`: To query tile entities

**How it works**:
```
1. Called before moving an entity to new_x, new_y
2. Get all non-walkable tiles
3. For each non-walkable tile:
   a. Check if entity's bounding box overlaps with tile
   b. If overlap found, return True (collision)
4. If no collisions found, return False
```

**AABB Collision Detection**:

AABB = Axis-Aligned Bounding Box. Two rectangles overlap if:
```
rect1.left < rect2.right AND
rect1.right > rect2.left AND
rect1.top < rect2.bottom AND
rect1.bottom > rect2.top
```

**Key Method**: `check_collision_with_tiles(entity_id, new_x, new_y)`
```python
def check_collision_with_tiles(self, entity_id: str, new_x: float, new_y: float) -> bool:
    """Checks if the entity at new_x and new_y collides with any non-walkable tiles"""
    tiles = self.entity_manager.get_entities_with_components(["tile", "position", "sprite"])
    moving_entity = self.entity_manager.get_entity_by_id(entity_id)
    moving_sprite = moving_entity["sprite"]

    for tile_entity_id, tile_components in tiles:
        tile_component = tile_components["tile"]
        if not tile_component.is_walkable:
            # Check if this specific tile actually collides
            if self._calculate_collision(tile_components["position"], tile_components["sprite"], moving_sprite, new_x, new_y):
                return True  # Collision detected!
    
    return False  # No collision
```

**AABB Calculation** (`_calculate_collision`):
```python
def _calculate_collision(self, tile_position, tile_sprite, collider_sprite, collider_new_x, collider_new_y) -> bool:
    """Check if entity at collider_new_x, collider_new_y collides with tile using AABB"""
    # Moving entity bounds
    entity_right = collider_new_x + collider_sprite.width
    entity_bottom = collider_new_y + collider_sprite.height
    
    # Tile bounds
    tile_right = tile_position.x + tile_sprite.width
    tile_bottom = tile_position.y + tile_sprite.height
    
    # AABB collision: check if rectangles overlap
    if (collider_new_x < tile_right and 
        entity_right > tile_position.x and
        collider_new_y < tile_bottom and 
        entity_bottom > tile_position.y):
        return True
    return False
```

**Visual Example**:
```
Player moving right hits water tile:

World:
┌────────────────────────┐
│ GRASS  WATER  GRASS    │
│ x=0    x=32   x=64     │
│ ┌──────────────┐       │
│ │ PLAYER(96,0) │       │
│ └──────────────┘       │
└────────────────────────┘

Collision check for new_x=100:
- Player right = 100 + 32 = 132
- Water left = 32
- 132 > 32? YES
- Player left = 100
- Water right = 32 + 32 = 64
- 100 < 64? NO → No collision yet

Collision check for new_x=96:
- Player right = 96 + 32 = 128
- Water left = 32
- 128 > 32? YES
- Player left = 96
- Water right = 64
- 96 < 64? NO → Still no collision

Collision check for new_x=64:
- Player right = 64 + 32 = 96
- Water left = 32
- 96 > 32? YES
- Player left = 64
- Water right = 64
- 64 < 64? NO → Still no collision

At exact touch (player_right == water_left):
- Player at x=32, right = 64
- Water at x=64
- 64 > 64? NO → Movement allowed
```

**Design Notes**:
- Uses `>` instead of `>=` to allow exact touching without overlap
- Checks all non-walkable tiles (even if one blocks, returns True)
- Operates on new position, doesn't modify actual position (MovementSystem does that)
- Collision is checked before movement happens

**Tile Walkability**:
```python
# In TileComponent
def is_walkable(self):
    return self.tile_type == GRASS  # Only grass is walkable
```

**Extension Points**:
- Add different collision layers (ground, walls, air)
- Add entity-to-entity collision
- Add trigger zones (damage, healing, level exit)
- Add slope collision for movement on angles
- Add collision response (bounce, slide along walls)
- Add debug visualization of collision boxes

