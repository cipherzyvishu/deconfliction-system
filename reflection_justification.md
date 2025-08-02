**Drone Deconfliction System - Reflection & Justification Document**

---

**1. Design Decisions & Architectural Choices**

Our architecture is inspired by the need for scalability, modularity, and real-time strategic deconfliction. The system is divided into core components:

- **Trajectory Modeling**: Generates Occupied Volume Boxes (OVBs) between drone waypoints, capturing 4D space-time occupancy.
- **Conflict Detection**: Performs spatial and temporal checks using both geometric overlap and timing constraints.
- **Agent-Based Layer**: Each drone is represented as an autonomous agent capable of detecting and resolving conflicts.
- **Conflict Resolution**: Currently uses a delay-based mechanism that minimally shifts drone launch times to resolve conflicts.
- **Spatial Indexing**: R-tree spatial filtering is used to reduce pairwise comparisons, significantly boosting performance.
- **Visualization Layer**: A 3D scene generator using matplotlib displays flight paths and conflict zones interactively.

All components are modular, allowing for integration with advanced techniques such as AI optimization, dynamic routing, or live telemetry ingestion.

---

**2. Spatial and Temporal Conflict Checks**

Each drone's mission is broken into segments. For each segment:
- A **3D cuboid (OVB)** is formed using:
  - Width: lateral buffer (e.g., 20 meters)
  - Height: vertical buffer (e.g., 20 meters)
  - Length: segment distance between two waypoints
  - Time window: entry and exit timestamps of the segment

**Conflict detection** involves:
- **Spatial Overlap**: Checking whether two OVBs intersect in 2D (x-y) and overlap in z-axis.
- **Temporal Overlap**: Validating overlapping time windows.
- **Separation Violation**: If actual time gap between OVBs < required time gap (2 × length / speed), a conflict is flagged.

Severity is calculated as a ratio between required and actual separation.

---

**3. AI Integration (if applicable)**

While core logic is rule-based and deterministic, the architecture is AI-ready. In future iterations:
- **Reinforcement Learning (RL)** agents can learn optimal delay/reroute policies.
- **Similarity Search with AI** can help find comparable trajectories and infer safe regions.
- **Clustering or prediction models** can aid in estimating future congestion zones or drone flow.

For now, a Bezier-based trajectory smoothing model is used to simulate real-world curves, improving realism.

---

**4. Testing Strategy & Edge Cases**

We implemented multiple test scenarios including:
- **No conflict case**: Two distant missions with sufficient altitude/time separation.
- **Direct conflict**: Two missions sharing the same air corridor at the same time.
- **Curved flight path**: To ensure that Bezier-sampled paths still lead to accurate OVB modeling.
- **Altitude-only conflict**: Drones crossing same x-y at different altitudes.
- **Temporal-only conflict**: Drones sharing same space but at different times.

Edge cases handled include:
- Zero-length segments (skipped)
- Waypoints with equal timestamps
- Skipping degenerate OVBs during sampling
- Sampling with Bezier smoothing to ensure continuity

---

**5. Scaling the System to Real-World Data (10,000+ drones)**

To scale this system:

- **Spatial Filtering Optimization**:
  - Use **R-tree indexing** to prefilter possible OVBs, already implemented.
  - Switch to 3D indexing (e.g., using Octrees or KD-Trees) for more precise pruning.

- **Batch Conflict Checking**:
  - Use **parallel processing (multiprocessing/threading)** to process OVB comparisons concurrently.
  - Divide agents into sectors (geofenced zones) to allow localized conflict detection.

- **Trajectory Simplification**:
  - Use **segment clustering** or **curve fitting** to reduce total number of OVBs per drone without losing fidelity.

- **Infrastructure Scaling**:
  - Host API/backend on cloud infrastructure with autoscaling (e.g., AWS Lambda/Fargate)
  - Use message queues for event-based deconfliction (e.g., Kafka + worker pool)

- **Future Ready Integrations**:
  - Connect to telemetry APIs (e.g., DJI Cloud API) for live mission ingest
  - Store missions and conflict logs in NoSQL DB for querying, auditing, and playback

With the current modular design and optimized data flow, this system can realistically be scaled to thousands of drones in strategic-level planning scenarios.

---

**Prepared by:** Garv Sharma  
**Project:** Drone Deconfliction System for FlytBase Assignment 2025

