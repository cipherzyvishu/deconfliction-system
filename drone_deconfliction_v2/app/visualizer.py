# --------------------------
# STEP 10: app/visualizer.py
# --------------------------

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from .models import OVB, Mission, Conflict
from typing import Dict, List
import numpy as np
from .trajectory_model import generate_ovbs

def draw_3d_box(ax, ovb: OVB, color='blue', alpha=0.15):
    x, y, z = ovb.center
    dx = ovb.length
    dy = ovb.width
    dz = ovb.height

    x -= dx / 2
    y -= dy / 2
    z -= dz / 2

    corners = np.array([
        [x, y, z],
        [x + dx, y, z],
        [x + dx, y + dy, z],
        [x, y + dy, z],
        [x, y, z + dz],
        [x + dx, y, z + dz],
        [x + dx, y + dy, z + dz],
        [x, y + dy, z + dz]
    ])

    faces = [
        [corners[i] for i in [0, 1, 2, 3]],  # bottom
        [corners[i] for i in [4, 5, 6, 7]],  # top
        [corners[i] for i in [0, 1, 5, 4]],
        [corners[i] for i in [2, 3, 7, 6]],
        [corners[i] for i in [1, 2, 6, 5]],
        [corners[i] for i in [0, 3, 7, 4]],
    ]

    box = Poly3DCollection(faces, alpha=alpha, facecolors=color, edgecolors='gray')
    ax.add_collection3d(box)

def plot_3d_scene(primary: Mission, simulated: Dict[str, Mission], conflicts: List[Conflict]):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Plot primary
    px = [wp.x for wp in primary.waypoints]
    py = [wp.y for wp in primary.waypoints]
    pz = [wp.z for wp in primary.waypoints]
    ax.plot(px, py, pz, label=primary.id, color='blue', linewidth=2, marker='o')
    for ovb in generate_ovbs(primary.id, primary.waypoints):
        draw_3d_box(ax, ovb, color='blue', alpha=0.2)

    # Plot simulated drones
    cmap = plt.get_cmap("tab20")
    for i, (drone_id, mission) in enumerate(simulated.items()):
        sx = [wp.x for wp in mission.waypoints]
        sy = [wp.y for wp in mission.waypoints]
        sz = [wp.z for wp in mission.waypoints]
        color = cmap(i % 20)
        ax.plot(sx, sy, sz, label=drone_id, color=color, linestyle='--', marker='x')
        for ovb in generate_ovbs(drone_id, mission.waypoints):
            draw_3d_box(ax, ovb, color=color, alpha=0.15)

    # Plot conflicts
    for i, c in enumerate(conflicts):
        x, y, z = c.location
        ax.scatter(x, y, z, color='red', s=80, marker='x')
        ax.text(x + 2, y + 2, z + 2, f"C{i+1}", color='red', fontsize=8)

    ax.set_title("🛩️ 3D Drone Conflict Visualization")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.legend()
    plt.tight_layout()
    plt.show()