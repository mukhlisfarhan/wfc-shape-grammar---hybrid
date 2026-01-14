# --- MICRO GRAMMAR: ARCHITECTURAL ARTICULATION ---

def apply_bedroom_rules(cell, grid):
    features = [
        {"type": "BED", "rect": (0.2, 0.2, 0.6, 0.4)}
    ]
    
    # Context-Aware Door Placement
    # Check neighbors: (dx, dy)
    directions = {"TOP": (0, -1), "BOTTOM": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
    
    for wall, (dx, dy) in directions.items():
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < 10 and 0 <= ny < 10: # Check boundaries
            neighbor = grid[ny][nx]
            if neighbor.collapsed and neighbor.options[0] == "HALLWAY":
                # If neighbor is a hallway, put a door on this wall!
                if wall == "TOP":    features.append({"type": "DOOR", "rect": (0.4, 0.0, 0.2, 0.05)})
                if wall == "BOTTOM": features.append({"type": "DOOR", "rect": (0.4, 0.95, 0.2, 0.05)})
                if wall == "LEFT":   features.append({"type": "DOOR", "rect": (0.0, 0.4, 0.05, 0.2)})
                if wall == "RIGHT":  features.append({"type": "DOOR", "rect": (0.95, 0.4, 0.05, 0.2)})
                
    return features


# Mapper to link WFC labels to Grammar functions
GRAMMAR_MAP = {
    "BEDROOM": apply_bedroom_rules,
    "KITCHEN": lambda cell, grid: [{"type": "STOVE", "rect": (0.1, 0.1, 0.2, 0.2)}], # Simplified for now
}
