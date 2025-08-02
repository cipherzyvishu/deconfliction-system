from .models import Mission, Waypoint, Conflict
from .trajectory_model import generate_ovbs
from .conflict_detector import detect_conflicts_between_ovbs
from .optimizer import resolve_with_delay
from typing import List, Dict
from app.utils.spatial_index import build_spatial_index, spatial_query
from app.trajectory_model import detect_conflicts

class DroneAgent:
    def __init__(self, mission: Mission, use_bezier: bool = False):
        self.mission = mission
        self.ovbs = generate_ovbs(mission.id, mission.waypoints, use_bezier=use_bezier)
        self.conflicts: List[Conflict] = []
        self.resolved = False
        self.delay = 0.0

    def check_conflict_against(self, rtree_index, id_map, exclude_ids: List[str]):
        if self.resolved:
            return
    
        self.conflicts.clear()
        for ovb in self.ovbs:
            candidate_ids = spatial_query(ovb, rtree_index)
            for cid in candidate_ids:
                ob = id_map[cid]
                if ob.drone_id in exclude_ids:  # skip self
                    continue
                
                if abs(ovb.center[2] - ob.center[2]) > 40:
                    continue
                if abs(ovb.entry_time - ob.exit_time) > 30:
                    continue
                
                results = detect_conflicts([ovb], [ob])
                self.conflicts.extend(results)
    
    
    def resolve_conflict(self):
        self.delay = resolve_with_delay(self.mission, self.conflicts)
        self.resolved = self.delay >= 0
        if self.resolved:
            # Apply delay to all waypoints
            for wp in self.mission.waypoints:
                wp.t += self.delay
            self.ovbs = generate_ovbs(self.mission.id, self.mission.waypoints)
        return self.resolved
