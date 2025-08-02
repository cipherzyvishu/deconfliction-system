# app/utils/spatial_index.py

from rtree import index
from app.models import OVB
from typing import List, Tuple, Dict

def build_spatial_index(all_ovbs: List[OVB]) -> Tuple[index.Index, Dict[int, OVB]]:
    idx = index.Index()
    id_to_ovb = {}

    for i, ovb in enumerate(all_ovbs):
        x, y, z = ovb.center
        dx = ovb.length / 2
        dy = ovb.width / 2
        # Only use 2D bounds for R-tree
        idx.insert(i, (x - dx, y - dy, x + dx, y + dy))
        id_to_ovb[i] = ovb  # map id to actual object

    return idx, id_to_ovb

def spatial_query(ovb: OVB, idx: index.Index) -> List[int]:
    x, y, z = ovb.center
    dx = ovb.length / 2
    dy = ovb.width / 2
    return list(idx.intersection((x - dx, y - dy, x + dx, y + dy)))
