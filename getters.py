import bpy
import bmesh

from . import utils

def get_pairs_candidates(threshold=1e-4):
    print("=== Get Pairs Candidates ===")
    obj, mesh, bm, ml_layer, objmode = utils.get_bmesh_stuff()
    if not ml_layer: return

    tree = utils.build_tree(bm)
    exact = dict()
    near = dict()
    for v in bm.verts:
        co = utils.mirror(v.co)
        res = tree.find_range(co, threshold)
        exact_ = 0
        near_ = 0
        for _co, idx, dst in res:
            if idx != v.index:
                if dst == 0.0:
                    exact_ += 1
                else:
                    near_ += 1
        if exact_:
            exact.setdefault(exact_, set()).add(v)
        if near_:
            near.setdefault(near_, set()).add(v)
    return {0.0: exact, threshold: near}

