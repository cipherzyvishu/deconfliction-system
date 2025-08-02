# app/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.models import Waypoint, Mission, Conflict
from app.agent import DroneAgent
from app.trajectory_model import generate_ovbs
from app.utils.spatial_index import build_spatial_index, spatial_query
from app.trajectory_model import detect_conflicts
import traceback

app = FastAPI()


class WaypointIn(BaseModel):
    x: float
    y: float
    z: float
    t: float


class MissionInput(BaseModel):
    waypoints: List[WaypointIn]
    buffer: float


class AnalyzeRequest(BaseModel):
    mission: MissionInput
    simulated_drones: Dict[str, List[WaypointIn]]


class ConflictOut(BaseModel):
    with_: str
    location: List[float]
    time: float
    actual_gap: float
    required_gap: float


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        # Convert primary mission
        primary_mission = Mission(
            id="Primary",
            waypoints=[Waypoint(**wp.dict()) for wp in req.mission.waypoints]
        )
        primary_ovbs = generate_ovbs("Primary", primary_mission.waypoints, width=req.mission.buffer)

        # Convert simulated drones
        all_sim_ovbs = []
        drone_id_map = {}
        for drone_id, wp_list in req.simulated_drones.items():
            mission = Mission(
                id=drone_id,
                waypoints=[Waypoint(**wp.dict()) for wp in wp_list]
            )
            ovbs = generate_ovbs(drone_id, mission.waypoints, width=req.mission.buffer)
            for ovb in ovbs:
                drone_id_map[id(ovb)] = drone_id
            all_sim_ovbs.extend(ovbs)

        rtree_index, id_map = build_spatial_index(all_sim_ovbs)

        # Run conflict detection
        conflicts = []
        for ovb in primary_ovbs:
            for cid in spatial_query(ovb, rtree_index):
                ob = id_map[cid]
                if abs(ovb.center[2] - ob.center[2]) > 40:
                    continue
                if abs(ovb.entry_time - ob.exit_time) > 30:
                    continue
                for c in detect_conflicts([ovb], [ob]):
                    conflicts.append({
                        "with_": ob.drone_id,
                        "location": list(c.location),
                        "time": c.entry_time,
                        "actual_gap": c.actual_gap,
                        "required_gap": c.required_gap
                    })

        return {
            "status": "conflict detected" if conflicts else "clear",
            "conflicts": conflicts
        }

    except Exception as e:
        print("⚠️ Exception in /analyze:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
