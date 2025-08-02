from scipy.optimize import linprog
from typing import List, Dict
from .models import Conflict, Mission

def resolve_with_delay(primary: Mission, conflicts: List[Conflict], max_delay: float = 120.0) -> float:
    """
    Returns optimal delay (in seconds) for the primary mission that avoids conflicts.
    Minimizes total delay using LP (based on NASA formulation)
    """
    if not conflicts:
        return 0.0

    # Objective: Minimize delay (scalar)
    c = [1.0]

    # Constraints: delay >= required_gap - actual_gap for each conflict
    A = [[-1.0] for _ in conflicts]
    b = []
    for conflict in conflicts:
        gap_needed = conflict.required_gap - conflict.actual_gap
        b.append(-gap_needed)  # negative because of -1 coefficient in A

    # Bounds: delay ∈ [0, max_delay]
    bounds = [(0.0, max_delay)]

    result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

    if result.success:
        return result.x[0]  # optimal delay value
    else:
        return -1.0  # signal failure