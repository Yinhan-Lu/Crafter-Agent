#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState
from game.action_space import initialize_action_space
from agents.structured_prompts import build_complete_prompt
from utils.memory import Recent_Results
import numpy as np

def check_prompt_length():
    # Create a test game state
    game_state = GameState()
    game_state.health = 8
    game_state.food = 6
    game_state.drink = 7
    game_state.energy = 5
    game_state.inventory = {
        'wood': 3, 'stone': 1, 'coal': 0, 'iron': 0, 'diamond': 0, 'sapling': 0,
        'wood_pickaxe': 1, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
        'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
    }
    game_state._walkable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    game_state._turnable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    game_state.get_walkable_directions = lambda: game_state._walkable_directions
    game_state.get_turnable_directions = lambda: game_state._turnable_directions
    game_state.target_material = 'tree'
    game_state.text_local_view_mat = np.array([['grass', 'grass', 'grass'], ['grass', 'player', 'tree'], ['grass', 'stone', 'grass']])

    action_space = initialize_action_space()
    recent_results = Recent_Results(num_of_results=5)

    prompt = build_complete_prompt(game_state, action_space, recent_results)
    
    print("📏 Prompt Length Analysis")
    print("=" * 40)
    print(f"Characters: {len(prompt):,}")
    print(f"Words: {len(prompt.split()):,}")
    print(f"Lines: {len(prompt.splitlines()):,}")
    print(f"Estimated tokens: ~{len(prompt.split()) * 1.3:.0f}")
    
    # Check individual sections
    sections = [
        ("Basic Rules", "### Crafter Game Environment - Basic Rules", "### Material Properties"),
        ("Material Properties", "### Material Properties", "### Creature Properties"),
        ("Creature Properties", "### Creature Properties", "### Action Detailed Descriptions"),
        ("Action Descriptions", "### Action Detailed Descriptions", "### Tool Detailed Descriptions"),
        ("Tool Descriptions", "### Tool Detailed Descriptions", "### Game State Detailed Descriptions"),
        ("Game State Descriptions", "### Game State Detailed Descriptions", "### Current Game State"),
        ("Current State", "### Current Game State", "### ReAct Framework Instructions"),
        ("ReAct Framework", "### ReAct Framework Instructions", "### Recent History"),
        ("Recent History", "### Recent History", "### Answer Format Requirements"),
        ("Answer Format", "### Answer Format Requirements", "**Based on all")
    ]
    
    print("\n📊 Section Breakdown:")
    for name, start_marker, end_marker in sections:
        start_pos = prompt.find(start_marker)
        end_pos = prompt.find(end_marker)
        if start_pos != -1 and end_pos != -1:
            section_length = end_pos - start_pos
            print(f"  {name}: {section_length:,} chars")

if __name__ == "__main__":
    check_prompt_length() 