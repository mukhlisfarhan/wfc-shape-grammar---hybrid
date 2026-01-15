class MacroCell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.type = "UNASSIGNED" # e.g., "BEDROOM", "KITCHEN", "HALLWAY"
        self.is_fixed = False
        # The Micro-grid lives inside here
        self.micro_grid = [] 
        
    def assign_type(self, room_type, is_fixed=True):
        self.type = room_type
        self.is_fixed = is_fixed

class HouseGrid:
    def __init__(self, macro_width, macro_height, micro_res=4):
        self.w = macro_width
        self.h = macro_height
        self.res = micro_res # How many micro-tiles per room
        self.grid = [[MacroCell(x, y, micro_res) for x in range(w)] for y in range(h)]

    def get_unassigned_cells(self):
        return [c for row in self.grid for c in row if c.type == "UNASSIGNED"]

    def dictate_layout(self, config):
        """
        This is where the Grammar acts as the Global Controller.
        """
        # 1. Force Bedrooms based on config count
        unassigned = self.get_unassigned_cells()
        random.shuffle(unassigned)
        
        for _ in range(config['min_bedrooms']):
            if unassigned:
                cell = unassigned.pop()
                cell.assign_type("BEDROOM")