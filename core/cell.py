import random

class Cell:
    def __init__(self, x, y, possible_types):
        self.x = x
        self.y = y
        # The list of all potential tile types (e.g., ["WALL", "FLOOR", "DOOR"])
        self.options = list(possible_types)
        self.collapsed = False
        
        # GRAMMAR CONTROL
        self.is_fixed = False  # If True, WFC cannot change this (used for Spine/Seeds)
        self.room_tag = None   # The 'Zone' assigned by the Grammar (e.g., "KITCHEN")

    @property
    def entropy(self):
        """Entropy is the number of remaining possibilities."""
        if self.collapsed:
            return 0
        return len(self.options)

    def force_type(self, tile_type):
        """Used by the Grammar to 'dictate' a tile before WFC runs."""
        self.options = [tile_type]
        self.collapsed = True
        self.is_fixed = True

    def reset(self, initial_options):
        """Resets the cell for regeneration, unless it's a fixed Grammar tile."""
        if not self.is_fixed:
            self.options = list(initial_options)
            self.collapsed = False

    def collapse(self, weights):
        """Standard WFC weighted selection."""
        if self.collapsed or not self.options:
            return None

        # Filter weights to only include what's currently available in self.options
        current_weights = [weights.get(opt, 1) for opt in self.options]
        
        selection = random.choices(self.options, weights=current_weights, k=1)[0]
        self.options = [selection]
        self.collapsed = True
        return selection