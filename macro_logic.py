# --- MACRO LOGIC: TILE & ADJACENCY DEFINITIONS ---
class RoomType:
    def __init__(self, name, color, allowed_neighbors):
        self.name = name
        self.color = color
        self.allowed_neighbors = allowed_neighbors

# Define your 2D "Semantic Sockets"
ROOM_TYPES = {
    "HALLWAY": RoomType("HALLWAY", (150, 150, 150), 
        ["HALLWAY", "BEDROOM", "KITCHEN", "LIVING_ROOM"]), # Hallways connect to everything
    
    "BEDROOM": RoomType("BEDROOM", (200, 100, 255), 
        ["BEDROOM", "HALLWAY"]), # ALLOWS touching itself to grow larger!
    
    "KITCHEN": RoomType("KITCHEN", (255, 100, 100), 
        ["KITCHEN", "HALLWAY", "LIVING_ROOM"]), # Clusters with Kitchen/Living
        
    "LIVING_ROOM": RoomType("LIVING_ROOM", (100, 255, 100), 
        ["LIVING_ROOM", "HALLWAY", "KITCHEN"])
}