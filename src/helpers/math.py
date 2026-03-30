"""Utility functions for mathematical operations"""


def lerp(start: float, end: float, factor: float) -> float:
    """
    Linearly interpolates between start and end by factor.
    
    Args:
        start: Starting value
        end: Ending value
        factor: Interpolation factor (0.0 = start, 1.0 = end)
                Values are clamped to [0.0, 1.0]
    
    Returns:
        Interpolated value between start and end
    """
    clamped_factor = min(factor, 1.0)  # Clamp to prevent overshoot
    return start + (end - start) * clamped_factor
