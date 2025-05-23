import numpy as np
from typing import Any, Dict, Tuple, List

import numpy as np
from typing import Any, Dict, Tuple, List
import crafter
from math import atan2, degrees, sqrt
from typing import List, Dict, Tuple
from collections import defaultdict
class GameState:
    def __init__(self):
        # Player position and orientation
        self.pos: np.ndarray = np.array([32, 32])
        self.facing: Tuple[int, int] = (0, 1)  # Represents facing down
        self.all_dirs: Tuple[Tuple[int, int], ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))

        # Player stats
        self.health: int = 9
        self.food: int = 9
        self.drink: int = 9
        self.energy: int = 9

        # Inventory
        self.inventory: Dict[str, int] = {
            'health': 9, 'food': 9, 'drink': 9, 'energy': 9,
            'sapling': 0, 'wood': 0, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
            'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
            'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
        }

        # Achievements
        self.achievements: Dict[str, int] = {
            'collect_coal': 0, 'collect_diamond': 0, 'collect_drink': 0,
            'collect_iron': 0, 'collect_sapling': 0, 'collect_stone': 0,
            'collect_wood': 0, 'defeat_skeleton': 0, 'defeat_zombie': 0,
            'eat_cow': 0, 'eat_plant': 0, 'make_iron_pickaxe': 0,
            'make_iron_sword': 0, 'make_stone_pickaxe': 0, 'make_stone_sword': 0,
            'make_wood_pickaxe': 0, 'make_wood_sword': 0, 'place_furnace': 0,
            'place_plant': 0, 'place_stone': 0, 'place_table': 0, 'wake_up': 0
        }

        # Player state
        self.action: str = 'do'
        self.sleeping: bool = False
        self.texture: str = 'player-down'
        self.walkable: List[str] = ['grass', 'path', 'sand', 'lava']

        # Internal state
        self._fatigue: int = 1
        self._hunger: int = 1
        self._thirst: int = 1
        self._recover: int = 1
        self._last_health: int = 9

        # World reference (this would typically be a separate object)
        self.world: Any = None  # Placeholder for the world object

        # current target of the player
        self.target_material: str = None
        self.target_obj:str = None
        
        #local_view
        self.text_local_view_mat = None
        self.text_local_view_obj = None

        self.closest_wood = None
        self.closest_cows = None
        self.walkable_view_string = None
        self.walkable_description = None
        self.walkable_directions = None
        self.turnable_directions = None
        self.lan_wrapper = None
        self.local_view_mat = None
        self.local_view_obj = None
    def update(self, player: Any = None, **kwargs):
        """
        Update the game state with new values.
        If a player object is provided, update from the player.
        Otherwise, update individual attributes from kwargs.
        """
        if player is not None:
            # Update from player object
            self.pos = player.pos
            self.facing = tuple(player.facing)
            self.all_dirs = player.all_dirs
            self.health = player.health
            self.food = player.inventory['food']
            self.drink = player.inventory['drink']
            self.energy = player.inventory['energy']
            self.inventory = player.inventory.copy()
            self.achievements = player.achievements.copy()
            self.action = player.action
            self.sleeping = player.sleeping
            self.texture = player.texture
            self.walkable = player.walkable.copy()
            self._fatigue = player._fatigue
            self._hunger = player._hunger
            self._thirst = player._thirst
            self._recover = player._recover
            self._last_health = player._last_health
            self.world = player.world
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    def get_inventory(self) -> Dict[str, int]:
        """Return the current inventory."""
        return self.inventory
    
    def get_inventory_string(self) -> str:
        """Return the current inventory as a formatted string."""
        inventory = self.get_inventory()
        inventory_items = []
        for item, count in inventory.items():
            inventory_items.append(f"{item}: {count} ")
        return "\n".join(inventory_items).strip()

    def get_achievements(self) -> Dict[str, int]:
        """Return the current achievements."""
        return self.achievements

    def get_position(self) -> Tuple[int, int]:
        """Return the current position as a tuple."""
        return tuple(self.pos)
    def get_walkable_directions(self) -> Dict[str, bool]:
        """Return the current walkable directions as a dictionary."""
        return self.walkable_directions
    def get_turnable_directions(self) -> Dict[str, bool]:
        """Return the current turnable directions as a dictionary."""
        return self.turnable_directions
    def get_facing_direction(self) -> str:
        """Return the current facing direction as a string."""
        direction_map = {(0, 1): 'south', (0, -1): 'north', (1, 0): 'east', (-1, 0): 'west'}
        return direction_map.get(self.facing, 'unknown')

    def is_sleeping(self) -> bool:
        """Return whether the player is currently sleeping."""
        return self.sleeping

    def get_health_stats(self) -> Dict[str, int]:
        """Return the current health-related stats."""
        return {
            'health': self.health,
            'food': self.food,
            'drink': self.drink,
            'energy': self.energy
        }

    def __str__(self) -> str:
        """Return a string representation of the game state."""
        return f"Player at {self.get_position()}, facing {self.get_facing_direction()}, " \
                f"health: {self.health}, energy: {self.energy}, " \
                f"inventory: {self.get_inventory()}"
class GameStateUpdater:
    def __init__(self, game_state: GameState,
                player: crafter.objects.Player,
                world: crafter.engine.SemanticView,
                env:crafter.recorder.Recorder
):
        self.game_state = game_state
        self.player = player
        self.world = world
        self.env = env
        self.closest_wood = None
        self.closest_cows = None
        self.walkable_directions = None
        self.walkable_view_string = None
        self.walkable_description = None
        self.walkable_directions = None
        self.trunable_directions = None
        self.text_local_view_mat = None
        self.text_local_view_obj = None
        self.lan_wrapper = None
        self.local_view_mat = None
        self.local_view_obj = None
    def extract_subarray(self,big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
    def local_view_number_matrix_constructor(self):
        wbarr_mat = self.env._sem_view._world._mat_map
        wx, wy = self.env._player.pos[0], self.env._player.pos[1]
        self.local_view_mat = self.extract_subarray(wbarr_mat, wx, wy)

        # Get the object map and objects
        wbarr_obj = self.env._sem_view._world._obj_map
        world_objects = self.env._sem_view._world._objects
        
        # Create a new matrix for objects that includes arrow directions
        obj_matrix = np.zeros_like(wbarr_obj)
        
        # First copy the original object map
        obj_matrix[:] = wbarr_obj[:]
        
        # Now check for arrows and add direction information
        for y in range(wbarr_obj.shape[0]):
            for x in range(wbarr_obj.shape[1]):
                obj_idx = wbarr_obj[y, x]
                if obj_idx != 0:  # If there's an object
                    obj = world_objects[obj_idx - 1]  # Get the actual object
                    if int(obj_matrix[y, x]) == 0:
                        print(obj)
                    if int(obj_matrix[y, x]) == 17:
                        print(obj)
                    if isinstance(obj, crafter.objects.Arrow):
                        # Map arrow directions to specific numbers
                        # We'll use 17 as base (original Arrow number) plus direction modifier
                        direction_mapping = {
                            (-1, 0): 17,    # left
                            (1, 0): 18,     # right
                            (0, -1): 19,    # up
                            (0, 1): 20      # down
                        }
                        obj_matrix[y, x] = direction_mapping[tuple(obj.facing)]
        
        # Extract the local view
        self.local_view_obj = self.extract_subarray(obj_matrix, wx, wy)
    def local_view_info_transformer(self):
        
        
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = self.env._sem_view._world._mat_map
        wx, wy  = self.env._player.pos[0], self.env._player.pos[1]
        local_view_mat = self.extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = self.env._sem_view._world._obj_map
        wx, wy  = self.env._player.pos[0], self.env._player.pos[1]
        local_view_obj = self.extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = self.env._sem_view._mat_ids
        mapping_obj_objform = self.env._sem_view._obj_ids           
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow-toward-west":17,
            "Arrow-toward-east":18,
            "Arrow-toward-north":19,
            "Arrow-toward-south":20,
            "Plant": 21
        }

        world_objs = self.env._sem_view._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
            
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj = self.extract_subarray(world_objs_numform,wx,wy)
        self.text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        self.text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return self


    def matrices_to_language(self, material_matrix: List[List[str]], object_matrix: List[List[str]], 
                      center_x: int = 4, center_y: int = 4) -> Tuple[str, str]:
        """
        Convert material and object matrices to language descriptions.
        
        Args:
            material_matrix: 9x9 list of lists containing material names
            object_matrix: 9x9 list of lists containing object names
            center_x: x-coordinate of player (default 4)
            center_y: y-coordinate of player (default 4)
        
        Returns:
            Tuple of (material_description, object_description)
        """
        # Define distance buckets
        distance_buckets = [
            (1, "adjacent"),
            (3, "very near"),
            (5, "near"),
            (20, "far"),
            (float('inf'), "very far")
        ]
        
        # Define direction mappings
        directions = [
            (0, "east"),
            (45, "northeast"),
            (90, "north"),
            (135, "northwest"),
            (180, "west"),
            (225, "southwest"),
            (270, "south"),
            (315, "southeast")
        ]
        def transpose_matrix(matrix):
            return list(map(list, zip(*matrix)))
        object_matrix = transpose_matrix(object_matrix)
        material_matrix = transpose_matrix(material_matrix)
        def get_distance_bucket(dx: int, dy: int) -> str:
            """Determine the distance bucket for given dx, dy."""
            distance = sqrt(dx*dx + dy*dy)
            for max_dist, bucket_name in distance_buckets:
                if distance <= max_dist:
                    return bucket_name
            return "very far"

        def get_direction(dx: int, dy: int) -> str:
            """Calculate direction from dx, dy."""
            if dx == 0 and dy == 0:
                return ""
                
            # Calculate angle in degrees
            angle = degrees(atan2(dy, dx))
            angle = (angle + 360) % 360
            
            # Find closest direction
            closest_dir = min(directions, 
                            key=lambda x: abs(angle - x[0]))
            return closest_dir[1]

        def describe_matrix(matrix: List[List[str]], matrix_type: str) -> str:
            descriptions = []
            
            if not matrix or not matrix[0]:
                return f"Empty {matrix_type} description"
            
            rows = len(matrix)
            cols = len(matrix[0])
            
            for y in range(rows):
                for x in range(cols):
                    if x == center_x and y == center_y:
                        continue  # Skip center (player position)
                    
                    value = matrix[y][x]
                    if value in ['None', 'Nothing']:
                        continue  # Skip empty spaces
                    
                    # Calculate relative position
                    dx = x - center_x
                    dy = center_y - y  # Invert y to match game coordinates
                    
                    distance = get_distance_bucket(dx, dy)
                    direction = get_direction(dx, dy)
                    
                    if direction:
                        descriptions.append({
                            'value': value,
                            'distance': distance,
                            'direction': direction
                        })
            
            # Group by value and distance
            groups = {}
            for desc in descriptions:
                key = f"{desc['value']}_{desc['distance']}"
                if key not in groups:
                    groups[key] = {
                        'value': desc['value'],
                        'distance': desc['distance'],
                        'directions': []
                    }
                groups[key]['directions'].append(desc['direction'])
            
            # Convert to sentences
            sentences = []
            for group in groups.values():
                dirs = list(set(group['directions']))
                
                if len(dirs) > 1:
                    last_dir = dirs.pop()
                    dir_str = f"{', '.join(dirs)} and {last_dir}"
                else:
                    dir_str = dirs[0]
                
                sentences.append(
                    f"There is {group['value']} {group['distance']} to the {dir_str}")
            
            return ";\n ".join(sentences)

        # Generate descriptions for both matrices
        material_desc = describe_matrix(material_matrix, "material")
        object_desc = describe_matrix(object_matrix, "object")
        self.lan_wrapper = "this is observation of material around you:\n " + material_desc + ";\n this is observation of object around you:\n " + object_desc
        return self

    def get_walkable_directions(self) -> Dict[str, bool]:
        """
        Returns a dictionary indicating whether each cardinal direction is walkable.
        
        Returns:
            Dict[str, bool]: Dictionary with keys 'north', 'east', 'south', 'west' 
                            and boolean values indicating if that direction is walkable
        """
        if self.text_local_view_mat is None:
            return {
                'north': False,
                'east': False,
                'south': False,
                'west': False
            }

        walkable = {'grass', 'path', 'sand'}
        # Get the transposed matrix as used in get_walkable_view_string
        transposed_matrix = list(zip(*self.text_local_view_mat))
        center_y, center_x = 4, 4  # Player position

        # Check each cardinal direction
        self.walkable_directions = {
            'north': transposed_matrix[center_y - 1][center_x] in walkable,
            'south': transposed_matrix[center_y + 1][center_x] in walkable,
            'east': transposed_matrix[center_y][center_x + 1] in walkable,
            'west': transposed_matrix[center_y][center_x - 1] in walkable
        }
        return self
    
    def get_walkable_view_string(self):
        """
        Convert the text_local_view_mat into a human-readable string representation 
        highlighting walkable areas.
        
        Returns:
            str: A formatted string showing the 9x9 grid with walkable/unwalkable areas.
        """
        if self.text_local_view_mat is None:
            return "No local view available"

        # Define walkable materials from data.yaml
        walkable = {'grass', 'path', 'sand'}

        # Header
        output = "Walkable Areas Map (9x9 Grid):\n"

        # Convert matrix to grid representation
        for y, row in enumerate(list(zip(*self.text_local_view_mat))):# self.text_local_view_mat's row is the transposed column of the matrix
            line = []
            for x, cell in enumerate(row):
                if (y, x) == (4, 4):  # Center position is always the player
                    symbol = 'P'
                elif cell in walkable:

                    symbol = 'Y'
                else:
                    symbol = 'N'
                line.append(symbol)
            output += "".join(line) + "\n"

        # Add key/legend
        output += "\nKey:\n"
        output += "P = Player (center)\n"
        # output += "░ = Walkable Area (grass, path, sand)\n"
        # output += "█ = Unwalkable Area\n"
        output += "Y = Walkable Area\n"
        output += "N = Unwalkable Area\n"
        self.walkable_view_string = output
        return self
    def get_walkable_description(self) -> str:
        """
        Provide a text description of walkable areas in the 3x3 grid around the player,
        including all eight directions (cardinal and diagonal).
        
        Returns:
            str: A textual description of walkable areas in each direction.
        """
        if self.text_local_view_mat is None:
            return "No local view available"

        walkable = {'grass', 'path', 'sand'}
        transposed_matrix = list(zip(*self.text_local_view_mat))
        
        # Check all eight surrounding cells
        directions = {
            'north': (0, 1),      # y-1, x
            'northeast': (0, 2),  # y-1, x+1
            'east': (1, 2),       # y, x+1
            'southeast': (2, 2),  # y+1, x+1
            'south': (2, 1),      # y+1, x
            'southwest': (2, 0),  # y+1, x-1
            'west': (1, 0),       # y, x-1
            'northwest': (0, 0)   # y-1, x-1
        }
        
        walkable_dirs = []
        blocked_dirs = []
        
        for direction, (y, x) in directions.items():
            cell = transposed_matrix[y + 3][x + 3]
            if cell in walkable:
                walkable_dirs.append(direction)
            else:
                blocked_dirs.append(direction)
        
        # Organize directions by cardinal and diagonal
        cardinal_walkable = [d for d in walkable_dirs if d in ['north', 'south', 'east', 'west']]
        diagonal_walkable = [d for d in walkable_dirs if d not in ['north', 'south', 'east', 'west']]
        
        cardinal_blocked = [d for d in blocked_dirs if d in ['north', 'south', 'east', 'west']]
        diagonal_blocked = [d for d in blocked_dirs if d not in ['north', 'south', 'east', 'west']]
        
        # Construct the description
        description = "From your position:\n"
        
        # Walkable directions
        if walkable_dirs:
            if cardinal_walkable:
                description += "- You can walk in these cardinal directions: " + ", ".join(cardinal_walkable) + "\n"
            if diagonal_walkable:
                description += "- You can walk in these diagonal directions: " + ", ".join(diagonal_walkable) + "\n"
        else:
            description += "- You cannot walk in any direction!\n"
            
        # Blocked directions
        if blocked_dirs:
            if cardinal_blocked:
                description += "- Movement is blocked in these cardinal directions: " + ", ".join(cardinal_blocked) + "\n"
            if diagonal_blocked:
                description += "- Movement is blocked in these diagonal directions: " + ", ".join(diagonal_blocked)
        self.walkable_description = description
        return self
    def get_turnable_directions(self):
        """
        Returns a dictionary indicating whether each cardinal direction is turnable.
        A direction is turnable if:
        1. There's an obstacle in that direction (not grass/sand/path/lava)
        2. The player is not already facing that direction
        
        Returns:
            Dict[str, bool]: Dictionary with keys 'north', 'east', 'south', 'west' 
                            and boolean values indicating if that direction is turnable
        """
        if self.text_local_view_mat is None:
            return {
                'north': False,
                'east': False,
                'south': False,
                'west': False
            }

        # Define non-obstacle materials
        walkable_or_lava = {'grass', 'path', 'sand', 'lava'}
        
        # Get the transposed matrix as used in get_walkable_view_string
        transposed_matrix = list(zip(*self.text_local_view_mat))
        center_y, center_x = 4, 4  # Player position

        # Check each cardinal direction
        self.turnable_directions = {
            'north': (transposed_matrix[center_y - 1][center_x] not in walkable_or_lava) and (self.game_state.get_facing_direction() != "north"),
            'south': (transposed_matrix[center_y + 1][center_x] not in walkable_or_lava) and (self.game_state.get_facing_direction() != "south"),
            'east': (transposed_matrix[center_y][center_x + 1] not in walkable_or_lava) and (self.game_state.get_facing_direction() != "east"),
            'west': (transposed_matrix[center_y][center_x - 1] not in walkable_or_lava) and (self.game_state.get_facing_direction() != "west")
        }
        return self
    def get_walkable_view_string(self) -> str:
        """
        Convert the text_local_view_mat into a human-readable string representation 
        highlighting walkable areas in a 3x3 grid around the player.
        
        Returns:
            str: A formatted string showing the 3x3 grid with walkable/unwalkable areas.
        """
        if self.text_local_view_mat is None:
            return "No local view available"

        # Define walkable materials from data.yaml
        walkable = {'grass', 'path', 'sand'}

        # Header
        output = "Walkable Areas Map (3x3 Grid):\n"

        # Transpose the matrix to align with the game screen orientation
        transposed_matrix = list(zip(*self.text_local_view_mat))

        # Convert matrix to grid representation
        for y in range(3):
            line = []
            for x in range(3):
                # Adjust indices to center the 3x3 grid around the player
                cell = transposed_matrix[y + 3][x + 3]
                if (y, x) == (1, 1):  # Center position is always the player
                    symbol = 'P'
                elif cell in walkable:
                    symbol = 'Y'
                else:
                    symbol = 'N'
                line.append(symbol)
            output += "".join(line) + "\n"

        # Add key/legend
        output += "\nKey:\n"
        output += "P = Player (center)\n"
        output += "Y = Walkable Area\n"
        output += "N = Unwalkable Area\n"
        self.walkable_view_string = output
        return self
    

    def filter_matrix_to_trees_and_player(self, matrix):
        """
        Convert the input matrix to a new matrix containing only 'tree' and 'player' at the center.
        All other positions are set to an empty string.

        Args:
            matrix (List[List[str]]): A 9x9 matrix representing the materials around the player.

        Returns:
            List[List[str]]: A new 9x9 matrix with only 'tree' and 'player' at the center.
        """
        # Validate the input matrix
        if not matrix or len(matrix) != 9 or any(len(row) != 9 for row in matrix):
            raise ValueError("Input matrix must be a 9x9 list of lists.")
        
        # Initialize a new matrix filled with empty strings
        new_matrix = [['' for _ in range(9)] for _ in range(9)]
        center = (4, 4)  # Player's position at the center of the 9x9 grid
        
        for y in range(9):
            for x in range(9):
                if (x, y) == center:
                    new_matrix[y][x] = 'player'
                elif matrix[y][x] == 'tree':
                    new_matrix[y][x] = 'tree'
                # No else clause needed since the cell is already empty
        
        self.wood_matrix = new_matrix
        return self
    def describe_closest_cows(self, matrix):
        """
        Describe the top 5 closest cows relative to the player's position.

        Args:
            matrix (List[List[Optional[str]]]): A 9x9 matrix containing only 'Cow', 'Player', and None.

        Returns:
            str: A descriptive string of the closest cow locations.
        """
        center = (4, 4)  # Player's position at the center of the 9x9 grid
        cows = []

        for y, row in enumerate(matrix):
            for x, tile in enumerate(row):
                if tile == 'Cow':
                    dx = x - center[0]
                    dy = y - center[1]
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    cows.append((distance, dx, dy))

        # Sort cows by distance, then by dx and dy for consistent ordering
        cows.sort(key=lambda loc: (loc[0], loc[1], loc[2]))
        closest_cows = cows[:5]

        if not closest_cows:
            return "There are no cows visible in your immediate surroundings."

        description = "The closest cow locations are:\n"
        for i, (distance, dx, dy) in enumerate(closest_cows, 1):
            parts = []
            if dx < 0:
                parts.append(f"{abs(dx)} block{'s' if abs(dx) !=1 else ''} north")
            elif dx > 0:
                parts.append(f"{abs(dx)} block{'s' if abs(dx) !=1 else ''} south")

            if dy < 0:
                parts.append(f"{abs(dy)} block{'s' if abs(dy) !=1 else ''} west")
            elif dy > 0:
                parts.append(f"{abs(dy)} block{'s' if abs(dy) !=1 else ''} east")

            if not parts:
                location = "at your current position"
            else:
                location = " and ".join(parts)

            description += f"{i}. {location}\n"

        self.closest_cows = description.strip()
        return self
    def describe_closest_wood(self, matrix):
        """
        Describe the top 5 closest wood (tree) locations relative to the player's position.

        Args:
            matrix (List[List[str]]): A 9x9 matrix representing the materials around the player.

        Returns:
            str: A descriptive string of the closest wood locations.
        """
        center = (4, 4)  # Player's position at the center of the 9x9 grid
        wood_locations = []

        for y, row in enumerate(matrix):
            for x, tile in enumerate(row):
                if tile == 'tree':
                    dx = x - center[0]
                    dy = y - center[1]
                    distance = abs(dx) + abs(dy)  # Manhattan distance
                    wood_locations.append((distance, dx, dy))

        # Sort by distance, then by dx and dy to ensure consistent ordering
        wood_locations.sort(key=lambda loc: (loc[0], loc[1], loc[2]))
        closest_wood = wood_locations[:5]

        if not closest_wood:
            return "There is no wood visible in your immediate surroundings."

        description = "The closest wood locations are:\n"
        for i, (distance, dx, dy) in enumerate(closest_wood, 1):
            parts = []
            if dx < 0:
                parts.append(f"{abs(dx)} block{'s' if abs(dx) !=1 else ''} north")
            elif dx > 0:
                parts.append(f"{abs(dx)} block{'s' if abs(dx) !=1 else ''} south")

            if dy < 0:
                parts.append(f"{abs(dy)} block{'s' if abs(dy) !=1 else ''} west")
            elif dy > 0:
                parts.append(f"{abs(dy)} block{'s' if abs(dy) !=1 else ''} east")

            if not parts:
                location = "at your current position"
            else:
                location = " and ".join(parts)

            description += f"{i}. {location}\n"

        self.closest_wood = description.strip()
        return self
    def initialize(self):
        self.game_state.update(self.player)

    # def local_view_wrapper(self):

    def update(self):
        self.local_view_info_transformer()
        self.get_walkable_view_string()
        self.get_walkable_description()
        self.get_walkable_directions()
        self.get_turnable_directions()
        self.local_view_number_matrix_constructor()

        self.matrices_to_language(self.text_local_view_mat, self.text_local_view_obj)
        self.describe_closest_wood(self.text_local_view_mat)
        self.describe_closest_cows(self.text_local_view_obj)
        target = (self.player.pos[0] + self.player.facing[0], self.player.pos[1] + self.player.facing[1])
        self.game_state.update(self.player,
                            target_material = self.player.world[target][0],
                            target_obj = self.player.world[target][1],
                            text_local_view_mat = self.text_local_view_mat,
                            text_local_view_obj = self.text_local_view_obj,
                            closest_wood = self.closest_wood,
                            closest_cows = self.closest_cows,
                            walkable_view_string = self.walkable_view_string,
                            walkable_description = self.walkable_description,
                            walkable_directions = self.walkable_directions,
                            turnable_directions = self.turnable_directions,
                            lan_wrapper = self.lan_wrapper,
                            local_view_mat = self.local_view_mat,
                            local_view_obj = self.local_view_obj
                            )

    def get_game_state(self) -> GameState:
        return self.game_state
