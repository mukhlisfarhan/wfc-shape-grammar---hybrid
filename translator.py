def scale_to_world(feature_rect, cell_x, cell_y, tile_size):
    """Translates normalized 0-1 grammar coordinates to Pygame pixels."""
    fx, fy, fw, fh = feature_rect
    world_x = (cell_x * tile_size) + (fx * tile_size)
    world_y = (cell_y * tile_size) + (fy * tile_size)
    world_w = fw * tile_size
    world_h = fh * tile_size
    return (world_x, world_y, world_w, world_h)