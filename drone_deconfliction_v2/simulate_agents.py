# simulate_agents.py

import random
from app.models import Waypoint, Mission
from app.agent import DroneAgent
from app.visualizer import plot_3d_scene
from app.utils.spatial_index import build_spatial_index


def generate_random_mission(drone_id: str, x0=0, y0=0, z0=100, t0=0, num=8) -> Mission:
    waypoints = []
    for i in range(num):
        wp = Waypoint(
            x = x0 + random.uniform(-100, 100),
            y = y0 + random.uniform(-100, 100),
            z = z0 + random.uniform(-10, 10),
            t = t0 + i * random.uniform(5, 10)
        )
        waypoints.append(wp)
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
    run_simulation(1000)


