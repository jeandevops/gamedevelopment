# Linear Interpolation (Lerp) & Delta Time

Quick reference for understanding the math behind smooth movement in your game engine.

---

## The Basic Lerp Formula

```
new_value = current + (target - current) * factor
```

Where `factor` is a decimal from 0 to 1.

### Factor Behavior

| Factor | Meaning | Example (0→100) |
|--------|---------|-----------------|
| 0.0 | No movement | Stays at 0 |
| 0.1 | 10% toward target | 0 + (100-0) × 0.1 = 10 |
| 0.5 | 50% toward target | 0 + (100-0) × 0.5 = 50 |
| 0.9 | 90% toward target | 0 + (100-0) × 0.9 = 90 |
| 1.0 | Reaches target | 0 + (100-0) × 1.0 = 100 |

---

## The Problem: Frame-Dependent Animation

### Without Delta Time (❌ Broken)

```python
position += (target - position) * 0.1  # Always 10% per frame
```

**At 30 FPS**:
- 10 frames to complete = 0.33 seconds

**At 60 FPS**:
- 10 frames to complete = 0.17 seconds (2x faster!)

**Result**: Animation runs at different speeds on different hardware.

---

## The Solution: Delta Time

**Delta time** = how many seconds passed since last frame

```python
lerp_speed = 5.0  # Units per SECOND
movement_factor = lerp_speed * delta_time
position = position + (target - position) * movement_factor
```

### Step-by-Step Example

**Setup**:
- Current position: 100
- Target position: 200
- lerp_speed: 5.0 (move 5 units per second)
- Distance: 100 pixels

---

### Scenario A: 30 FPS

**Frame 1** (delta_time ≈ 0.033 seconds):
```
movement_factor = 5.0 × 0.033 = 0.165
distance_to_move = 100 × 0.165 = 16.5 pixels
new_position = 100 + 16.5 = 116.5
```

**Frame 2** (delta_time ≈ 0.033 seconds):
```
movement_factor = 5.0 × 0.033 = 0.165
distance_to_move = 16.5 × 0.165 = 2.73 pixels  (remaining 83.5 pixels)
new_position = 116.5 + 2.73 = 119.23
```

**Frames 3-20**: Continue with diminishing movement
- Gets closer to 200 with each frame
- Never overshoots because factor is tiny (< 0.2)

---

### Scenario B: 60 FPS

**Frame 1** (delta_time ≈ 0.016 seconds):
```
movement_factor = 5.0 × 0.016 = 0.08
distance_to_move = 100 × 0.08 = 8 pixels
new_position = 100 + 8 = 108
```

**Frame 2** (delta_time ≈ 0.016 seconds):
```
movement_factor = 5.0 × 0.016 = 0.08
distance_to_move = 92 × 0.08 = 7.36 pixels (remaining 92 pixels)
new_position = 108 + 7.36 = 115.36
```

---

## The Key Insight: Same Total Speed!

**30 FPS calculation**:
- Per frame movement: 16.5 pixels/frame
- Frame rate: 30 frames/second
- **Total per second**: 16.5 × 30 = 495 pixels/second

**60 FPS calculation**:
- Per frame movement: 8 pixels/frame
- Frame rate: 60 frames/second
- **Total per second**: 8 × 60 = 480 pixels/second ≈ **Same speed!**

Both will reach the target in approximately **20 seconds**, regardless of FPS.

---

## Why Clamp to 1.0?

```python
clamped_factor = min(movement_factor, 1.0)
```

### Without Clamping (❌ Bug)

Imagine we're very close to the target:
```
Current: 199
Target: 200
Distance: 1 pixel

movement_factor = 5.0 × 0.5 = 2.5  (hypothetically large delta_time)
new_position = 199 + (200 - 199) × 2.5
             = 199 + 1 × 2.5
             = 201.5  ← OVERSHOOTS! Goes past target!
```

### With Clamping (✅ Correct)

```
clamped_factor = min(2.5, 1.0) = 1.0
new_position = 199 + (200 - 199) × 1.0
             = 199 + 1
             = 200  ← Stops exactly at target!
```

Clamping ensures the movement factor never exceeds 100%, preventing overshooting.

---

## Your Camera Implementation

```python
def follow_target(self, target_x, target_y, trigger_margin, delta_time):
    # Calculate movement factor (scaled by lerp_speed)
    movement_factor = self.lerp_speed * delta_time
    clamped_factor = min(movement_factor, 1.0)
    
    # Only lerp if beyond trigger margin
    if distance_x > trigger_margin:
        target_pos = target_x - self.viewport_width / 2
        self.x = self.x + (target_pos - self.x) * clamped_factor
```

**What happens**:
- `lerp_speed = 5.0` means "move 5 pixels per second"
- At 30 FPS: each frame moves ~0.165 of remaining distance
- At 60 FPS: each frame moves ~0.08 of remaining distance
- Both reach target in same real-world time ⏱️

---

## Exponential Decay (Why It Feels Smooth)

Unlike linear movement, lerp creates **exponential decay**:
```
Frame 1: 16.5 pixels moved (83.5 remaining)
Frame 2: 2.73 pixels moved (80.77 remaining)
Frame 3: 1.33 pixels moved (79.44 remaining)
Frame 4: 0.64 pixels moved (78.8 remaining)
...
```

Movement slows as you approach the target, creating a smooth, natural deceleration effect.

This is why camera lerp looks and feels great! 🎥

