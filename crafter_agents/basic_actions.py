from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import crafter.objects
from game.game_state import GameState
from enum import Enum
import random
from typing import Dict, List, Tuple, Optional, Callable
from enum import Enum, auto
from PIL import Image
import base64
import io
import crafter
import openai
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import time
import agents.agents as agents
from game.game_state import *
from basic_actions import *



class Direction(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

def noop_condition(game_state: GameState) -> bool:
    return True  # Noop is always possible

def move_condition(game_state: GameState, direction: str) -> bool:
    walkable_dirs = game_state.get_walkable_directions()
    return walkable_dirs.get(direction.lower(), False)          

def turn_condition(game_state: GameState, direction: str) -> bool:
    turnable_dirs = game_state.get_turnable_directions()
    return turnable_dirs.get(direction.lower(), False)

def collect_wood_condition(game_state: GameState) -> bool:
    return game_state.target_material == "tree"

def collect_grass_condition(game_state: GameState) -> bool:
    return game_state.target_material == "grass"

def collect_water_condition(game_state: GameState) -> bool:
    return game_state.target_material == "water"

def collect_stone_condition(game_state: GameState) -> bool:
    return game_state.target_material == "stone" and game_state.inventory["wood_pickaxe"]>0

def collect_coal_condition(game_state: GameState) -> bool:
    return game_state.target_material == "coal" and game_state.inventory["wood_pickaxe"]>0

def collect_iron_condition(game_state: GameState) -> bool:
    return game_state.target_material == "iron" and  game_state.inventory["stone_pickaxe"]>0

def collect_diamond_condition(game_state: GameState) -> bool:
    return game_state.target_material == "diamond" and game_state.inventory["iron_pickaxe"]>0

def sleep_condition(game_state: GameState) -> bool:
    return game_state.energy < 9  # Can sleep if energy is not full

def place_stone_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 stone in the inventory
    if game_state.inventory['stone'] < 1:
        return False
    
    # Check if the target material is one of the allowed types
    allowed_materials = ['grass', 'sand', 'path', 'water', 'lava']
    if game_state.target_material not in allowed_materials:
        return False
    
    return True
    

def place_table_condition(game_state: GameState) -> bool:
    # Check if the player has at least 2 wood in the inventory
    if game_state.inventory['wood'] < 2:
        return False
    
    # Check if the target material is one of the allowed types
    allowed_materials = ['grass', 'sand', 'path']
    if game_state.target_material not in allowed_materials:
        return False
    
    return True

def place_furnace_condition(game_state: GameState) -> bool:
    # Check if the player has at least 4 stone in the inventory
    if game_state.inventory['stone'] < 4:
        return False
    
    # Check if the target material is one of the allowed types
    allowed_materials = ['grass', 'sand', 'path']
    if game_state.target_material not in allowed_materials:
        return False
    
    return True

def place_plant_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 sapling in the inventory
    if game_state.inventory['sapling'] < 1:
        return False
    
    # Check if the target material is grass
    if game_state.target_material != 'grass':
        return False
    
    return True

def make_wood_pickaxe_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood in the inventory
    if game_state.inventory['wood'] < 1:
        return False
    
    # Check if there's a table nearby
    if 'table' not in game_state.text_local_view_mat:
        return False
    
    return True

def make_stone_pickaxe_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood and 1 stone in the inventory
    if game_state.inventory['wood'] < 1 or game_state.inventory['stone'] < 1:
        return False
    
    # Check if there's a table nearby
    if 'table' not in game_state.text_local_view_mat:
        return False
    
    return True

def make_iron_pickaxe_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood, 1 coal, and 1 iron in the inventory
    if game_state.inventory['wood'] < 1 or game_state.inventory['coal'] < 1 or game_state.inventory['iron'] < 1:
        return False
    
    # Check if there's a table and a furnace nearby
    if 'table' not in game_state.text_local_view_mat or 'furnace' not in game_state.text_local_view_mat:
        return False
    
    return True

def make_wood_sword_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood in the inventory
    if game_state.inventory['wood'] < 1:
        return False
    
    # Check if there's a table nearby
    if 'table' not in game_state.text_local_view_mat:
        return False
    
    return True

def make_stone_sword_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood and 1 stone in the inventory
    if game_state.inventory['wood'] < 1 or game_state.inventory['stone'] < 1:
        return False
    
    # Check if there's a table nearby
    if 'table' not in game_state.text_local_view_mat:
        return False
    
    return True

def make_iron_sword_condition(game_state: GameState) -> bool:
    # Check if the player has at least 1 wood, 1 coal, and 1 iron in the inventory
    if game_state.inventory['wood'] < 1 or game_state.inventory['coal'] < 1 or game_state.inventory['iron'] < 1:
        return False
    
    # Check if there's a table and a furnace nearby
    if 'table' not in game_state.text_local_view_mat or 'furnace' not in game_state.text_local_view_mat:
        return False
    
    return True

def attach_cow_condition(game_state: GameState) -> bool:
    if isinstance(game_state.target_obj, crafter.objects.Cow):
        return True
    return False

# Dictionary mapping action names to their corresponding condition functions
action_conditions: Dict[str, Tuple[str, str, Callable[[GameState], bool]]] = {
    "noop": (
        "Do nothing",
        "Always possible",
        noop_condition
    ),
    "move_west": (
        "Move one step to the west",
        "Possible if there's no obstacle to the west",
        lambda gs: move_condition(gs, "west")
    ),
    "move_east": (
        "Move one step to the east",
        "Possible if there's no obstacle to the east",
        lambda gs: move_condition(gs, "east")
    ),
    "move_north": (
        "Move one step to the north",
        "Possible if there's no obstacle to the north",
        lambda gs: move_condition(gs, "north")
    ),
    "move_south": (
        "Move one step to the south",
        "Possible if there's no obstacle to the south",
        lambda gs: move_condition(gs, "south")
    ),
    "collect_wood": (
        "Try to collect the wood in front of player",
        "a tree material in front of the player ",
        lambda gs:collect_wood_condition(gs)
    ),
    "collect_stone": (
        "Try to collect the stone in front of player",
        "a stone material in front of the player and exist at least one wood pickaxe in the inventory",
        lambda gs:collect_stone_condition(gs)
    ),
    "collect_coal": (
        "Try to collect the coal in front of player",
        "a coal material in front of the player and exist at least one wood pickaxe in the inventory",
        lambda gs:collect_coal_condition(gs)
    ),
    "collect_iron": (
        "Try to collect the iron in front of player",
        "a iron material in front of the player and exist at least one stone pickaxe in the inventory",
        lambda gs:collect_iron_condition(gs)
    ),
    "collect_diamond": (
        "Try to collect the diamond in front of player",
        "a diamond material in front of the player and exist at least one iron pickaxe in the inventory",
        lambda gs:collect_diamond_condition(gs)
    ),
    "collect_water": (
        "try to increase the drink level of player",
        "a water material in front of the player ",
        lambda gs:collect_water_condition(gs)
    ),
    "collect_grass": (
        "try to collect a sapling from grass",
        "a water material in front of the player ",
        lambda gs:collect_grass_condition(gs)
    ),
    "sleep": (
        "Rest to recover energy",
        "Possible if energy is not at maximum",
        sleep_condition
    ),
    "place_stone": (
        "Place a stone block",
        "Possible if player has stone and is on grass, sand, path, water, or lava",
        place_stone_condition
    ),
    "place_table": (
        "Place a crafting table",
        "Possible if player has 2 wood and is on grass, sand, or path",
        place_table_condition
    ),
    "place_furnace": (
        "Place a furnace",
        "Possible if player has 4 stone and is on grass, sand, or path",
        place_furnace_condition
    ),
    "place_plant": (
        "Plant a sapling",
        "Possible if player has a sapling and is on grass",
        place_plant_condition
    ),
    "make_wood_pickaxe": (
        "Craft a wooden pickaxe",
        "Possible if player has 1 wood and is near a crafting table",
        make_wood_pickaxe_condition
    ),
    "make_stone_pickaxe": (
        "Craft a stone pickaxe",
        "Possible if player has 1 wood, 1 stone, and is near a crafting table",
        make_stone_pickaxe_condition
    ),
    "make_iron_pickaxe": (
        "Craft an iron pickaxe",
        "Possible if player has 1 wood, 1 coal, 1 iron, and is near both a crafting table and a furnace",
        make_iron_pickaxe_condition
    ),
    "make_wood_sword": (
        "Craft a wooden sword",
        "Possible if player has 1 wood and is near a crafting table",
        make_wood_sword_condition
    ),
    "make_stone_sword": (
        "Craft a stone sword",
        "Possible if player has 1 wood, 1 stone, and is near a crafting table",
        make_stone_sword_condition
    ),
    "make_iron_sword": (
        "Craft an iron sword",
        "Possible if player has 1 wood, 1 coal, 1 iron, and is near both a crafting table and a furnace",
        make_iron_sword_condition
    ),
    "attach_cow": (
        "Attach a cow to the player. If the cow is dead after attaching, a meat would be added to the inventory",
        "Possible if the player is facing a cow",
        attach_cow_condition
    ),
    "turn_west": (
        "change the player's direction to west when the west is obstacle(all materials except grass, sand, path, lava) rather than walkable or lava and the player is not facing west",
        "Possible if the player's direction is not west",
        lambda gs: turn_condition(gs, "west")
    ),
    "turn_east": (
        "change the player's direction to east when the east is obstacle(all materials except grass, sand, path, lava) rather than walkable or lava and the player is not facing east",
        "Possible if the player's direction is not east",
        lambda gs: turn_condition(gs, "east")
    ),
    "turn_north": (
        "change the player's direction to north when the north is obstacle(all materials except grass, sand, path, lava) rather than walkable or lava and the player is not facing north",
        "Possible if the player's direction is not north",
        lambda gs: turn_condition(gs, "north")
    ),
    "turn_south": (
        "change the player's direction to south when the south is obstacle(all materials except grass, sand, path, lava) rather than walkable or lava and the player is not facing south",
        "Possible if the player's direction is not south",
        lambda gs: turn_condition(gs, "south")
    ),
}
