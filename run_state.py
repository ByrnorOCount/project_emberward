def create_run_state():
    """Initializes core HP, gold, node map, player position, etc."""
    return {
        "core_hp": 10,
        "gold": 50,
        "current_node": 0,
        # nodes: for now a single start node
        "nodes": [
            {"id": 0, "name": "Start Node", "cleared": False}
        ],
        # helper fields used by renderer / fight scene (updated by fight)
        "wave_index": 0,
        "wave_total": 0,
        "phase": "map",
    }

def advance_to_next_node(run_state, node_id):
    """Moves player to the chosen node and loads its map layout."""
    run_state["current_node"] = node_id
    # mark as not yet cleared if not present
    for n in run_state["nodes"]:
        if n["id"] == node_id:
            n["cleared"] = False
            break
    run_state["phase"] = "fight"