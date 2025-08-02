# app/utils/bezier.py

from app.models import Waypoint
from typing import List
import numpy as np

def bezier_curve(p0, p1, p2, t):
    return (1 - t)**2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2

def bezier_sample(wp1: Waypoint, wp2: Waypoint, control_offset: float = 30.0, num_points: int = 10) -> List[Waypoint]:
    """
    Generate intermediate waypoints between wp1 and wp2 using a quadratic Bezier curve.
    The control point is offset perpendicular to the direction of motion.
    """
    # Direction vector
    dx, dy = wp2.x - wp1.x, wp2.y - wp1.y
    length = np.hypot(dx, dy)

    # Unit perpendicular direction (left turn)
    perp_x, perp_y = -dy / length, dx / length

    # Control point is offset perpendicular to segment
    ctrl_x = (wp1.x + wp2.x) / 2 + perp_x * control_offset
    ctrl_y = (wp1.y + wp2.y) / 2 + perp_y * control_offset
    ctrl_z = (wp1.z + wp2.z) / 2

    bezier_points = []
    for i in range(1, num_points):  # exclude wp1 to avoid duplication
        t = i / num_points
        x = bezier_curve(wp1.x, ctrl_x, wp2.x, t)
        y = bezier_curve(wp1.y, ctrl_y, wp2.y, t)
        z = bezier_curve(wp1.z, ctrl_z, wp2.z, t)
        t_time = (1 - t) * wp1.t + t * wp2.t
        bezier_points.append(Waypoint(x=x, y=y, z=z, t=t_time))

    return bezier_points
