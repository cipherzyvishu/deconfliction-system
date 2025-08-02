# app/conflict_detector.py

from typing import List
from .models import OVB, Conflict

def boxes_overlap_2d(a: OVB, b: OVB) -> bool:
    ax, ay = a.center[0], a.center[1]
    bx, by = b.center[0], b.center[1]
    half_w = (a.width + b.width) / 2
    half_l = (a.length + b.length) / 2
    return abs(ax - bx) <= half_w and abs(ay - by) <= half_l

def boxes_overlap_altitude(a: OVB, b: OVB) -> bool:
    az = a.center[2]
    bz = b.center[2]
    half_h = (a.height + b.height) / 2
    return abs(az - bz) <= half_h

def boxes_overlap_time(a: OVB, b: OVB) -> bool:
    return not (a.exit_time < b.entry_time or b.exit_time < a.entry_time)

def actual_time_gap(a: OVB, b: OVB) -> float:
    t_a = (a.entry_time + a.exit_time) / 2
    t_b = (b.entry_time + b.exit_time) / 2
    return abs(t_a - t_b)

def required_time_gap(a: OVB, b: OVB) -> float:
    return (2 * b.length) / max(0.1, b.length / (b.exit_time - b.entry_time))  # Avoid zero division

def detect_conflicts_between_ovbs(
    drone_a: str,
    drone_b: str,
    ovbs_a: List[OVB],
    ovbs_b: List[OVB]
) -> List[Conflict]:
    conflicts = []

    for box_a in ovbs_a:
        for box_b in ovbs_b:
            if boxes_overlap_2d(box_a, box_b) and \
               boxes_overlap_altitude(box_a, box_b) and \
               boxes_overlap_time(box_a, box_b):
                
                dt_actual = actual_time_gap(box_a, box_b)
                dt_required = required_time_gap(box_a, box_b)

                if dt_actual < dt_required:
                    severity = (dt_required - dt_actual) / dt_required
                    conflict = Conflict(
                        drone_a=drone_a,
                        drone_b=drone_b,
                        location=box_a.center,
                        time=(box_a.entry_time + box_a.exit_time) / 2,
                        actual_gap=dt_actual,
                        required_gap=dt_required,
                        severity=severity
                    )
                    conflicts.append(conflict)
    
    return conflicts
