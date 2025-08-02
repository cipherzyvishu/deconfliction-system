# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from .models import Waypoint, Mission
from .trajectory_model import generate_ovbs
from .conflict_detector import detect_conflicts_between_ovbs
from .optimizer import resolve_with_delay

app = FastAPI(title="Strategic UAV Deconfliction API", version="2.0")

class WaypointInput(BaseModel):
    x: float
    y: float
    z: float
    t: float

class MissionInput(BaseModel):
    id: str
    waypoints: List[WaypointInput]

class ConflictResult(BaseModel):
    drone_a: str
    drone_b: str
    location: List[float]
    time: float
    actual_gap: float
    required_gap: float
    severity: float

@app.post("/check_conflicts", response_model=List[ConflictResult])
def check_conflicts(primary: MissionInput, simulated: MissionInput):
    try:
        wp_primary = [Waypoint(**wp.dict()) for wp in primary.waypoints]
        wp_sim = [Waypoint(**wp.dict()) for wp in simulated.waypoints]

        ovbs_primary = generate_ovbs(primary.id, wp_primary)
        ovbs_sim = generate_ovbs(simulated.id, wp_sim)

        conflicts = detect_conflicts_between_ovbs(primary.id, simulated.id, ovbs_primary, ovbs_sim)

        # Create Mission object for primary drone
        primary_mission = Mission(id=primary.id, waypoints=wp_primary)
        delay = resolve_with_delay(primary_mission, conflicts)

        return [
            ConflictResult(
                drone_a=c.drone_a,
                drone_b=c.drone_b,
                location=list(c.location),
                time=c.time,
                actual_gap=c.actual_gap,
                required_gap=c.required_gap,
                severity=c.severity
            ) for c in conflicts
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
