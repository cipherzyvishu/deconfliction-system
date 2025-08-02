from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class Waypoint:
    x: float
    y: float
    z: float
    t: float

@dataclass
class OVB:
    drone_id: str
    center: Tuple[float, float, float]
    length: float
    width: float
    height: float
    heading: float
    speed: float
    entry_time: float
    exit_time: float


@dataclass
class Conflict:
    location: Tuple[float, float, float]
    time_a: float
    time_b: float
    actual_gap: float
    required_gap: float
    time: float  # ✅ Add this line
    with_id: str                   # ✅ ID of conflicting drone
    severity: float = 0.0
    

@dataclass
class Mission:
    id: str
    waypoints: List[Waypoint]
    priority: int = 1
    delay: float = 0.0
