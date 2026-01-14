import pygame
import sys
from macro_logic import ROOM_TYPES
from cell import Cell
from micro_grammar.rules import GRAMMAR_MAP
from translator import scale_to_world

TILE_SIZE = 64
GRID_SIZE = 10

def propagate(x, y, grid):
    # A simple stack to keep track of cells we need to check
    stack = [(x, y)]

    while stack:
        curr_x, curr_y = stack.pop()
        current_cell = grid[curr_y][curr_x]
        
        # Get current allowed types based on this cell's remaining options
        # If collapsed, this is just one room. If not, it's a set of possibilities.
        current_allowed_neighbors = set()
        for opt in current_cell.options:
            current_allowed_neighbors.update(ROOM_TYPES[opt].allowed_neighbors)

        # Check all 4 neighbors (Up, Down, Left, Right)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = curr_x + dx, curr_y + dy

            # Stay inside grid boundaries
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbor = grid[ny][nx]
                
                # If neighbor isn't collapsed, filter its options
                if not neighbor.collapsed:
                    # Keep only options that are valid neighbors of our current cell
                    start_count = len(neighbor.options)
                    neighbor.options = [opt for opt in neighbor.options if opt in current_allowed_neighbors]
                    
                    # If the neighbor's options changed, we need to check ITS neighbors too
                    if len(neighbor.options) < start_count:
                        if (nx, ny) not in stack:
                            stack.append((nx, ny))
                            
# --- ADD THIS FUNCTION ABOVE main() ---
def get_lowest_entropy_cell(grid):
    """Finds the uncollapsed cell with the fewest possible room types."""
    best_cell = None
    min_entropy = float('inf')

    for row in grid:
        for cell in row:
            if not cell.collapsed:
                # We target cells with at least 2 options (entropy > 1)
                if 1 < cell.entropy < min_entropy:
                    min_entropy = cell.entropy
                    best_cell = cell
    return best_cell

def grammar_negotiation(grid):
    """
    The Grammar looks at the current state of the WFC 
    and 'prunes' options to enforce architectural order.
    """
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = grid[y][x]
            if cell.collapsed: continue
            
            # 1. THE HALLWAY SPINE
            # if a cell is surrounded by 3 rooms, the Grammar 'forces' 
            # it to be a Hallway to ensure the house is traversable.
            if not cell.collapsed and len(cell.options) > 1: # Only negotiate if there's a choice
                room_neighbors = 0
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if grid[ny][nx].collapsed and grid[ny][nx].options[0] != "HALLWAY":
                            room_neighbors += 1
                
                if room_neighbors >= 3:
                    # Grammar 'intervenes' and limits WFC's choices
                    if "HALLWAY" in cell.options:
                        cell.options = ["HALLWAY"]
            
            # 2. THE STRAIGHTENER (New)
                # If the cell is between two Hallways horizontally or vertically, 
                # force it to be a Hallway to create a straight corridor.
                if x > 0 and x < GRID_SIZE - 1:
                    left = grid[y][x-1]
                    right = grid[y][x+1]
                    if left.collapsed and right.collapsed:
                        if left.options[0] == "HALLWAY" and right.options[0] == "HALLWAY":
                            cell.options = ["HALLWAY"]

                if y > 0 and y < GRID_SIZE - 1:
                    up = grid[y-1][x]
                    down = grid[y+1][x]
                    if up.collapsed and down.collapsed:
                        if up.options[0] == "HALLWAY" and down.options[0] == "HALLWAY":
                            cell.options = ["HALLWAY"]
                            
            # --- THE BOXER RULE (Clumping) ---
            # If two perpendicular neighbors are the same room type,
            # force this cell to match them to complete a 2x2 block.
            directions = [((0, -1), (1, 0)),  # Up and Right
                          ((1, 0), (0, 1)),   # Right and Down
                          ((0, 1), (-1, 0)),  # Down and Left
                          ((-1, 0), (0, -1))] # Left and Up

            for (d1x, d1y), (d2x, d2y) in directions:
                n1x, n1y = x + d1x, y + d1y
                n2x, n2y = x + d2x, y + d2y
                
                if (0 <= n1x < GRID_SIZE and 0 <= n1y < GRID_SIZE and 
                    0 <= n2x < GRID_SIZE and 0 <= n2y < GRID_SIZE):
                    
                    c1, c2 = grid[n1y][n1x], grid[n2y][n2x]
                    
                    if c1.collapsed and c2.collapsed:
                        type1, type2 = c1.options[0], c2.options[0]
                        
                        # If both neighbors are the same (and not a Hallway), clump!
                        if type1 == type2 and type1 != "HALLWAY":
                            if type1 in cell.options:
                                cell.options = [opt for opt in cell.options if opt == type1 or opt == "HALLWAY"]
                                
            # --- THE ANTI-SINGLETON RULE ---
            # If a cell is surrounded by Hallways, it shouldn't be a 1x1 Room.
            if not cell.collapsed:
                hallway_count = 0
                for dx, dy in [(0, 1), (0, -1), (1, 0
                                                 ), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if grid[ny][nx].collapsed and grid[ny][nx].options[0] == "HALLWAY":
                            hallway_count += 1
                
                if hallway_count >= 3:
                    # If it's almost surrounded by hallways, don't let it be a tiny room
                    if "HALLWAY" in cell.options:
                        cell.options = ["HALLWAY"]

def main():
    pygame.init()
    screen = pygame.display.set_mode((TILE_SIZE * GRID_SIZE, TILE_SIZE * GRID_SIZE))
    pygame.display.set_caption("Thesis Stage 1: Auto-Solving WFC")

    # Initialize Grid
    grid = [[Cell(x, y, ROOM_TYPES.keys()) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
    
    # State variable for the Auto-Solver
    is_running = False 

    while True:
        # --- 1. EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Press SPACE to toggle Auto-Solve
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_running = not is_running
                    print(f"Auto-Solve: {'ON' if is_running else 'OFF'}")

            # Manual override via mouse click
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                grid[gy][gx].collapse()
                propagate(gx, gy, grid)

        # --- 2. THE WAVE FUNCTION COLLAPSE LOGIC ---
        if is_running:
            next_cell = get_lowest_entropy_cell(grid)
            
            if next_cell:
                next_cell.collapse()
                propagate(next_cell.x, next_cell.y, grid)
                
                # --- NEW: THE COMMUNICATION STEP ---
                grammar_negotiation(grid) # Grammar reviews the WFC's work
                
                pygame.time.delay(30)
            else:
                # No more cells to collapse, solve finished!
                is_running = False
                print("Synthesis Complete.")

        # --- 3. DRAWING ---
        screen.fill((50, 50, 50))
        for row in grid:
            for cell in row:
                # Calculate the main tile rectangle
                rect = pygame.Rect(cell.x * TILE_SIZE, cell.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # STEP A: Determine the background color
                if cell.collapsed:
                    base_color = ROOM_TYPES[cell.options[0]].color
                else:
                    # Gray based on entropy
                    gray = min(255, 50 + (cell.entropy * 25))
                    base_color = (gray, gray, gray)
                
                # STEP B: Draw the solid background tile FIRST
                pygame.draw.rect(screen, base_color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1) # Black outline for the tile
                
                # STEP C: If collapsed, draw the furniture/doors ON TOP
                if cell.collapsed:
                    room_label = cell.options[0]
                    if room_label in GRAMMAR_MAP:
                        features = GRAMMAR_MAP[room_label](cell, grid)
                        for feat in features:
                            if "rect" in feat:
                                world_rect = scale_to_world(feat["rect"], cell.x, cell.y, TILE_SIZE)
                                # Yellow for doors, White for furniture
                                feat_color = (255, 255, 0) if feat["type"] == "DOOR" else (255, 255, 255)
                                pygame.draw.rect(screen, feat_color, world_rect, 2)

        pygame.display.flip()

if __name__ == "__main__":

    main() 