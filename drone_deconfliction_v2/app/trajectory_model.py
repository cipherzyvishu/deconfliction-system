from shapely.geometry import LineString
from .models import Waypoint, OVB
from app.models import Waypoint, OVB
from typing import List
import math
from app.utils.bezier import bezier_sample
from app.models import Conflict


# app/trajectory_model.py

def compute_heading(dx, dy):
    return math.atan2(dy, dx)

def generate_ovbs(drone_id: str, waypoints: List[Waypoint], width: float = 20.0, height: float = 20.0, use_bezier: bool = False) -> List[OVB]:
    ovbs = []
    
    # Step 1: Apply Bezier sampling if enabled
    if use_bezier:
        new_wps = [waypoints[0]]
        for i in range(len(waypoints) - 1):
            curve = bezier_sample(waypoints[i], waypoints[i+1], control_offset=30, num_points=5)
            new_wps.extend(curve)
        waypoints = new_wps

    # Step 2: Build OVBs from updated waypoints
    for i in range(len(waypoints) - 1):
        wp1, wp2 = waypoints[i], waypoints[i+1]
        dx, dy = wp2.x - wp1.x, wp2.y - wp1.y
        length = math.hypot(dx, dy)
        dt = wp2.t - wp1.t
        if dt <= 0 or length == 0:
            continue  # skip bad segments
        speed = length / dt
        heading = math.atan2(dy, dx)

        # OVB center
        x_c = (wp1.x + wp2.x) / 2
        y_c = (wp1.y + wp2.y) / 2
        z_c = (wp1.z + wp2.z) / 2
        t_start = min(wp1.t, wp2.t)
        t_end = max(wp1.t, wp2.t)

        ovb = OVB(
            drone_id=drone_id,
            center=(x_c, y_c, z_c),
            length=length,
            width=width,
            height=height,
            heading=heading,
            speed=speed,
            entry_time=t_start,
            exit_time=t_end
        )
        ovbs.append(ovb)

    return ovbs


def overlap_2d(a: OVB, b: OVB) -> bool:
    ax, ay = a.center[0], a.center[1]
    bx, by = b.center[0], b.center[1]
    return abs(ax - bx) <= (a.length + b.length)/2 and abs(ay - by) <= (a.width + b.width)/2

def overlap_z(a: OVB, b: OVB) -> bool:
    az, bz = a.center[2], b.center[2]
    return abs(az - bz) <= (a.height + b.height)/2

def overlap_time(a: OVB, b: OVB) -> bool:
    return not (a.exit_time < b.entry_time or b.exit_time < a.entry_time)

def detect_conflicts(ovbs_a: List[OVB], ovbs_b: List[OVB]) -> List[Conflict]:
    """
    Detect spatial and temporal conflicts between two OVB lists.
    Returns list of Conflict objects.
    """
    conflicts = []
    for a in ovbs_a:
        for b in ovbs_b:
            if overlap_2d(a, b) and overlap_z(a, b) and overlap_time(a, b):
                t_a = (a.entry_time + a.exit_time) / 2
                t_b = (b.entry_time + b.exit_time) / 2
                dt_actual = abs(t_a - t_b)
                dt_required = 2 * b.length / b.speed
                if dt_actual < dt_required:
                    severity = (dt_required - dt_actual) / dt_required
                    conflicts.append(Conflict(
                        location=((a.center[0] + b.center[0])/2,
                                  (a.center[1] + b.center[1])/2,
                                  (a.center[2] + b.center[2])/2),
                        time_a=t_a,
                        time_b=t_b,
                        time=(t_a + t_b) / 2,               # ✅ midpoint time
                        actual_gap=dt_actual,
                        required_gap=dt_required,
                        with_id=b.drone_id,
                        severity=severity
                    ))
    return conflicts
    