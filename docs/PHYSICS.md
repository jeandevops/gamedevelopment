# Physics & Movement Documentation

Understanding delta time, fixed timestep, and frame-rate independent physics.

## Table of Contents
1. [Delta Time Explained](#delta-time-explained)
2. [The Problem: Variable Delta Time](#the-problem-variable-delta-time)
3. [The Solution: Fixed Timestep](#the-solution-fixed-timestep)
4. [Implementation](#implementation)
5. [Understanding the Accumulator](#understanding-the-accumulator)

---

## Delta Time Explained

**What is Delta Time?**

Delta time is the elapsed time since the last frame, measured in **seconds**.

```
delta_time = milliseconds_elapsed / 1000.0
```

**Why Do We Need It?**

Movement speed should be **frame-rate independent**. Without delta time:
- Fast computer (500 FPS) → Player moves 8× faster
- Slow computer (60 FPS) → Player moves at normal speed
- This is unplayable!

**The Solution**:
```python
new_position = current_position + (velocity × delta_time)
```

With delta time, movement is **consistent** regardless of frame rate:

| FPS | Delta Time | Movement Per Frame | Movement Per Second |
|-----|------------|-------------------|-------------------|
| 30  | 1/30 = 0.0333 | 240 × 0.0333 = **8 px** | 240 px ✓ |
| 60  | 1/60 = 0.0167 | 240 × 0.0167 = **4 px** | 240 px ✓ |
| 120 | 1/120 = 0.0083 | 240 × 0.0083 = **2 px** | 240 px ✓ |
| 300 | 1/300 = 0.0033 | 240 × 0.0033 = **0.8 px** | 240 px ✓ |

**Same speed every time!**

---

## The Problem: Variable Delta Time

If we naively use actual elapsed time, **physics becomes unpredictable**.

**Why?**

`clock.tick(FPS)` returns milliseconds elapsed since last call. Even when targeting 60 FPS, the actual time varies slightly:

- Frame 1: 16.66 ms
- Frame 2: 16.68 ms
- Frame 3: 16.65 ms
- Frame 4: 16.70 ms

These microsecond variations cause **fractional movement**:

```
Frame 1: position = 0 + (240 × 0.01666) = 4.0 → rounds to 4
Frame 2: position = 4 + (240 × 0.01668) = 8.01 → rounds to 8
Frame 3: position = 8 + (240 × 0.01665) = 11.99 → rounds to 12
Frame 4: position = 12 + (240 × 0.01670) = 16.01 → rounds to 16
```

**The Result: Unpredictable Rounding**

Sometimes the player is 1 pixel away from a wall, sometimes 2. This causes:
- **Inconsistent collision gaps** between player and walls
- **Non-deterministic behavior** - bugs that only happen sometimes
- **Unpredictable physics** - hard to debug

**Example collision issue**:
```
Movement: 240 px/sec
At 60 FPS target:

Frame A: elapsed = 16.66ms → position = 100 + 4.0 = 104 (touches wall at 96? No)
Frame B: elapsed = 16.68ms → position = 104 + 4.01 = 108.01 → rounds to 108 (wall hit)

Movement: 240 px/sec
At different timing:

Frame A: elapsed = 16.68ms → position = 100 + 4.01 = 104.01 → rounds to 104
Frame B: elapsed = 16.66ms → position = 104 + 4.0 = 108 (wall hit)

Different results! Inconsistent collision gaps.
```

---

## The Solution: Fixed Timestep

**Concept**: Decouple physics from rendering.

- **Physics runs at fixed, predictable intervals** (always 1/FPS)
- **Rendering runs as fast as possible** (smooth but independent)
- **Time accumulator** bridges the gap between actual time and physics updates

**Benefits**:

| Aspect | Fixed Timestep | Variable Timestep |
|--------|---|---|
| Physics speed | Always 240 px/sec | Varies with minor FPS changes |
| Collision detection | Deterministic (always same) | Random gaps (varies) |
| Reproducibility | Same movement every run | Depends on frame timing |
| Debugging | Predictable, easy to debug | Hard to reproduce bugs |
| Performance | Consistent | Can spike |

---

## Implementation

### Code Structure

```python
# In run.py

from helpers.constants import FPS

clock = pygame.time.Clock()

# Fixed timestep - physics always updates at target FPS
FIXED_DELTA_TIME = 1.0 / FPS  # If FPS=60, this is 1/60 = 0.01667 seconds
time_accumulator = 0.0

while True:
    # Step 1: Measure actual elapsed time
    milliseconds_elapsed = clock.tick(FPS)  # Limit rendering to target FPS
    delta_time = milliseconds_elapsed / 1000.0  # Convert to seconds
    
    # Step 2: Accumulate real time
    time_accumulator += delta_time
    
    # Step 3: Process input
    event_handler_system.process_events(pygame.event.get())
    
    # Step 4: Physics loop - run fixed timestep updates
    while time_accumulator >= FIXED_DELTA_TIME:
        movement_system.update(delta_time=FIXED_DELTA_TIME)  # Always 1/FPS!
        time_accumulator -= FIXED_DELTA_TIME
    
    # Step 5: Camera follows player
    player = entity_manager.get_entity_by_id("player")
    if player:
        camera_system.update(target_x=player["position"].x, target_y=player["position"].y)
    
    # Step 6: Render (runs every loop iteration)
    screen.fill((0, 0, 0))
    rendering_system.render()
    pygame.display.update()
```

### How clock.tick() Works

```python
milliseconds_elapsed = clock.tick(FPS)
```

What this does:
1. **Limits loop to maximum FPS** - If loop runs too fast, sleeps to slow down
2. **Returns elapsed time** - Milliseconds since last call (usually ~16.67ms at 60 FPS)
3. **Varies slightly** - Real OS scheduling means it's not always exact (16.65, 16.68, 16.70, etc.)

```python
# At 60 FPS target:
# clock.tick(60) usually returns: 16, 17, or 16 ms
# Converted to seconds: 0.016, 0.017, 0.016

# At 30 FPS target:
# clock.tick(30) usually returns: 33, 34, or 33 ms
# Converted to seconds: 0.033, 0.034, 0.033
```

**Important**: `clock.tick(FPS)` still **limits rendering**, but physics gets fixed timestep through the accumulator!

---

## Understanding the Accumulator

The **time accumulator** is a counter that:
1. **Collects real elapsed time** from actual gameplay
2. **Triggers physics updates** when enough time accumulated
3. **Maintains consistent physics** by using fixed delta_time

### Visual Timeline

**At 60 FPS (16.67ms target per frame):**

```
Rendering Loop (runs every iteration):
  │
  ├─ Frame 1: elapsed=16.66ms, accumulator=16.66
  │   └─ Physics? 16.66 < 16.67, NO
  │
  ├─ Frame 2: elapsed=16.68ms, accumulator=33.34
  │   └─ Physics? 33.34 >= 16.67, YES ✓
  │       accumulator = 33.34 - 16.67 = 16.67
  │   └─ Physics? 16.67 >= 16.67, YES ✓
  │       accumulator = 16.67 - 16.67 = 0
  │
  ├─ Frame 3: elapsed=16.67ms, accumulator=16.67
  │   └─ Physics? 16.67 >= 16.67, YES ✓
  │       accumulator = 0
  │
  ├─ Frame 4: elapsed=16.66ms, accumulator=16.66
  │   └─ Physics? 16.66 < 16.67, NO
```

**At 120 FPS (8.33ms target per frame, but physics at 60 FPS):**

```
Rendering Loop (runs every iteration):
  │
  ├─ Frame 1: elapsed=8.33ms, accumulator=8.33
  │   └─ Physics? 8.33 < 16.67, NO
  │   └─ Render ✓
  │
  ├─ Frame 2: elapsed=8.34ms, accumulator=16.67
  │   └─ Physics? 16.67 >= 16.67, YES ✓
  │       accumulator = 0
  │   └─ Render ✓
  │
  ├─ Frame 3: elapsed=8.33ms, accumulator=8.33
  │   └─ Physics? 8.33 < 16.67, NO
  │   └─ Render ✓
  │
  ├─ Frame 4: elapsed=8.33ms, accumulator=16.66
  │   └─ Physics? 16.66 >= 16.67, YES ✓
  │       accumulator = -0.01 (small overshoot, next frame has less)
```

**At 30 FPS (33.33ms target per frame, but physics at 60 FPS):**

```
Rendering Loop (runs every iteration):
  │
  ├─ Frame 1: elapsed=33.33ms, accumulator=33.33
  │   └─ Physics? 33.33 >= 16.67, YES ✓
  │       accumulator = 16.66
  │   └─ Physics? 16.66 >= 16.67, NO
  │   └─ Render ✓
  │
  ├─ Frame 2: elapsed=33.33ms, accumulator=49.99
  │   └─ Physics? 49.99 >= 16.67, YES ✓ (run 1)
  │       accumulator = 33.32
  │   └─ Physics? 33.32 >= 16.67, YES ✓ (run 2)
  │       accumulator = 16.65
  │   └─ Physics? 16.65 >= 16.67, NO
  │   └─ Render ✓
```

**Key insight**: At slow FPS, physics runs **multiple times per frame** to catch up!

### Mathematics

```python
# Initial state
time_accumulator = 0.0
FIXED_DELTA_TIME = 1.0 / 60  # 0.01667 seconds

# Each frame
while time_accumulator >= FIXED_DELTA_TIME:
    movement_system.update(FIXED_DELTA_TIME)
    time_accumulator -= FIXED_DELTA_TIME
```

**Why subtract after update?**

Because we "used up" that time for physics. We track what's left for next frame.

Example:
```
Frame 1: accumulator=33.33
         33.33 >= 16.67? YES
         movement_system.update(16.67)
         accumulator = 33.33 - 16.67 = 16.66
         
         16.66 >= 16.67? NO (loop exits)
         accumulator = 16.66 (carried to next frame)

Frame 2: accumulator += 33.33
         accumulator = 16.66 + 33.33 = 49.99
         
         49.99 >= 16.67? YES
         movement_system.update(16.67)
         accumulator = 49.99 - 16.67 = 33.32
         
         33.32 >= 16.67? YES
         movement_system.update(16.67)
         accumulator = 33.32 - 16.67 = 16.65
         
         16.65 >= 16.67? NO (loop exits)
         accumulator = 16.65 (carried to next frame)
```

### When Does the Accumulator Matter?

**Important clarification**: The accumulator is only beneficial when actual FPS **deviates** from target FPS.

**At exact target FPS** (e.g., FPS=60, always hitting 60 FPS):

```python
FPS = 60
_FIXED_DELTA_TIME = 1/60 = 0.01667
clock.tick(60)  # Returns ~16.67ms

Frame 1:
  milliseconds_elapsed = 16.67
  delta_time = 0.01667
  time_accumulator = 0.01667
  
  while 0.01667 >= 0.01667: YES
    movement_system.update(0.01667)
    time_accumulator = 0 - 0.01667 = 0
  
  Result: Physics runs exactly once per frame
```

**This is the same as just calling `movement_system.update()` directly!**

The accumulator only shows its value when:

1. **FPS drops below target** (lag spike):
   ```python
   FPS target = 60
   Frame takes 33ms (lag spike) instead of 16.67ms
   
   time_accumulator = 0.033
   while 0.033 >= 0.01667: YES (run 1)
     time_accumulator = 0.01663
   while 0.01663 >= 0.01667: NO
   
   Result: Physics runs TWICE to catch up
   ```

2. **Rendering FPS is different from physics FPS**:
   ```python
   FPS = 60 (physics target)
   But rendering at 120 FPS (faster computer)
   
   Each frame: delta_time ≈ 8.33ms
   time_accumulator only triggers every 2 frames
   
   Result: Physics runs half as often as rendering
   ```

**Without the while loop accumulator**, if you just called `movement_system.update()` every frame with FPS=60:
- At 60 FPS: Physics runs 60 times/second ✓
- At lag spike (30 FPS): Physics runs 30 times/second ✗ (Physics should run 60 times to catch up!)
- At 120 FPS: Physics runs 120 times/second ✗ (2× too fast!)

**With the accumulator**, physics always targets the correct rate regardless of actual FPS.

**TL;DR**: If your game **always** hits exactly the target FPS with no variance, the accumulator doesn't change behavior. But in real-world conditions with lag spikes and performance variation, the accumulator ensures physics stays synchronized.

---

## Velocity Units

**Critical**: Velocity must be in **pixels per second**, not pixels per frame.

```python
# In constants.py
SPEED = 240  # pixels per second, NOT per frame!

# In EventHandlerSystem
if keys[K_w]:
    velocity.vy -= SPEED  # = -240 pixels/second
```

**Why?**

Because we multiply by delta_time (in seconds):
```python
# MovementSystem
new_x = position.x + velocity.vx * delta_time

# With SPEED = 240 pixels/second:
new_x = 100 + 240 × (1/60)
new_x = 100 + 240 × 0.01667
new_x = 100 + 4.0
new_x = 104  ← Exactly 4 pixels per physics update
```

If we used pixels per frame instead:
```python
SPEED = 4  # pixels per frame (BAD)

new_x = 100 + 4 × (1/60)
new_x = 100 + 0.0667  ← Jerky, fractional movement!
```

---

## Summary

| Concept | Explanation |
|---------|------------|
| **Delta Time** | Elapsed seconds since last frame |
| **Fixed Timestep** | Physics always runs with delta_time = 1/FPS |
| **Time Accumulator** | Buffers real time until enough for physics update |
| **clock.tick(FPS)** | Limits rendering, returns milliseconds elapsed |
| **Velocity Units** | Always pixels/second, multiplied by delta_time (seconds) |
| **Deterministic Physics** | Same movement every run, no random gaps |

