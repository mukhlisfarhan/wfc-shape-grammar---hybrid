import random

class Cell:
    def __init__(self, x, y, possible_types):
        self.x = x
        self.y = y
        self.options = list(possible_types)
        self.collapsed = False

    @property
    def entropy(self):
        """Higher entropy = more uncertainty."""
        return len(self.options)

    def collapse(self):
        """Force the cell to pick one specific room type using weighted probability."""
        if not self.collapsed and self.options:
            # --- WEIGHT CONFIGURATION ---
            # Increase HALLWAY to make the house more connected.
            # Decrease KITCHEN to make it a rare, special room.
            weights_map = {
                "HALLWAY": 15,
                "LIVING_ROOM": 6,
                "BEDROOM": 4,
                "KITCHEN": 4,
                "VOID": 2       # If you use VOID for exterior boundaries
            }

            # 1. Map weights to current available options
            # If a type isn't in the map, it defaults to weight 1
            current_weights = [weights_map.get(opt, 1) for opt in self.options]

            # 2. Perform a weighted random selection
            # random.choices returns a list, so we take the first [0] element
            selection = random.choices(self.options, weights=current_weights, k=1)[0]
            
            self.options = [selection]
            self.collapsed = True

        return self.options[0]