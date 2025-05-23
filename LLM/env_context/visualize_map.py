import numpy as np
from PIL import Image, ImageDraw
import os
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')

def load_map_data(file_path):
    """Load map data from a numpy file."""
    return np.load(file_path)

def get_text_map(map_array, mapping_dict):
    """Convert map array to text map using a mapping dictionary."""
    size = map_array.shape
    print(size)
    return [[mapping_dict[map_array[i, j]] for j in range(size[1])] for i in range(size[0])]

def load_assets(assets_directory):
    """Load image assets from a directory."""
    assets = {}
    for asset_file in os.listdir(assets_directory):
        asset_name = asset_file.removesuffix('.png')
        assets[asset_name] = Image.open(os.path.join(assets_directory, asset_file))
    return assets

def create_canvas(text_map, assets, tile_size, edge=12):
    """Create a canvas by pasting images according to the text map."""
    rows, cols = len(text_map), len(text_map[0])
    canvas = Image.new('RGBA', (cols * tile_size, rows * tile_size))
    canvas_width, canvas_height = cols * tile_size, rows * tile_size
    draw = ImageDraw.Draw(canvas)
    for y, row in enumerate(text_map):
        for x, element in enumerate(row):
            if element in assets:
                canvas.paste(assets[element], (x * tile_size, y * tile_size))
    
    for y, row in enumerate(text_map):
        for x, element in enumerate(row):
            if element == 'diamond':
                top_left = (x * tile_size, y * tile_size)
                bottom_right = (top_left[0] + tile_size, top_left[1] + tile_size)
                top_left = (max(0, top_left[0] - edge), max(0, top_left[1] - edge))
                bottom_right = (min(canvas_width, bottom_right[0] + edge), min(canvas_height, bottom_right[1] + edge))
                draw.rectangle([top_left, bottom_right], outline='red', width=8)

    draw.rectangle([(32 * tile_size -12, 32 * tile_size-12), (32 * tile_size +12, 32 * tile_size+12)], outline='red', width=8)
    return canvas

def display_and_save_canvas(canvas, figsize, save_path):
    """Display and save the canvas."""
    plt.figure(figsize=figsize)
    # plt.imshow(canvas)
    plt.axis('off')
    # plt.show()
    canvas.save(save_path)

# Mapping dictionary
mapping = {
    0: None,
    1: 'water',
    2: 'grass',
    3: 'stone',
    4: 'path',
    5: 'sand',
    6: 'tree',
    7: 'lava',
    8: 'coal',
    9: 'iron',
    10: 'diamond',
    11: 'table',
    12: 'furnace',
    13: 'player', 
    14: 'cow',
    15: 'zombie',
    16: 'skeleton',
    17: 'arrow',
    18: 'plant'
}

# Main process
for seed_i in range(21):
    map_data = load_map_data(f'./map/map_seed_{seed_i}.npy')
    text_map = get_text_map(map_data, mapping)
    assets = load_assets('./assets')
    canvas = create_canvas(text_map, assets, 16)
    display_and_save_canvas(canvas, (16, 16), f'./map_seed_{seed_i}.png')
