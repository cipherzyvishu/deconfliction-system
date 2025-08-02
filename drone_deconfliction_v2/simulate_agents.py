# simulate_agents.py

import random
import math
from app.models import Waypoint, Mission
from app.agent import DroneAgent
from app.visualizer import plot_3d_scene
from app.utils.spatial_index import build_spatial_index


def generate_random_mission(drone_id: str, x0=0, y0=0, z0=100, t0=0, num=8) -> Mission:
    """
    Generates missions with intentionally overlapping paths to simulate conflicts.
    All drones follow the same general direction with slight variations.
    """
    base_angle = math.radians(45)  # All drones move northeast
    spacing = 60  # Distance between waypoints
    waypoints = []

    for i in range(num):
        # Introduce small variation in path per drone
        angle_variation = random.uniform(-0.05, 0.05)
        angle = base_angle + angle_variation

        dx = spacing * math.cos(angle)
        dy = spacing * math.sin(angle)
        dz = random.uniform(-5, 5)  # Altitude variation
        dt = 8 + random.uniform(-1, 1)

        if i == 0:
            x, y, z, t = x0, y0, z0, t0
        else:
            prev = waypoints[-1]
            x = prev.x + dx
            y = prev.y + dy
            z = prev.z + dz
            t = prev.t + dt

        waypoints.append(Waypoint(x, y, z, t))

    return Mission(id=drone_id, waypoints=waypoints)

def run_simulation(num_drones=10):
    agents = {}

    # Step 1: Create agents
    for i in range(num_drones):
        mission = generate_random_mission(f"Drone_{i}")
        agent = DroneAgent(mission, use_bezier=True)
        agents[agent.mission.id] = agent

    # Build R-tree ONCE from all agents' OVBs
    all_ovbs = []
    for agent in agents.values():
        all_ovbs.extend(agent.ovbs)

    rtree_index, id_map = build_spatial_index(all_ovbs)

    # Now check each agent against the index (excluding itself)
    for agent_id, agent in agents.items():
        agent.check_conflict_against(
            rtree_index=rtree_index,
            id_map=id_map,
            exclude_ids=[agent_id]
        )

    # Step 3: Print final status
    print("\n🛩️ Simulation Results:")
    for aid, agent in agents.items():
        print(f"{aid}: Delay = {agent.delay:.2f}s | Resolved = {agent.resolved} | Conflicts = {len(agent.conflicts)}")

    primary_agent = agents["Drone_0"]
    others = {k: v.mission for k,v in agents.items() if k != "Drone_0"}

    plot_3d_scene(primary_agent.mission, others, primary_agent.conflicts)

if __name__ == "__main__":
    run_simulation(10)


