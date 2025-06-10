#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import crafter
from game.game_state import *
from game.action_space import *
from agents.structured_prompts import build_complete_prompt
from utils.memory import Recent_Results

def test_lan_wrapper():
    print("🔍 Testing lan_wrapper Population")
    print("=" * 50)
    
    # Initialize environment
    env = crafter.Env(reward=True)
    env = crafter.Recorder(env, './path/to/logdir', save_stats=True, save_video=False, save_episode=False)
    
    obs = env.reset()
    world = env._sem_view
    player = env._player
    
    # Create game state
    current_state = GameState()
    current_updater = GameStateUpdater(game_state=current_state, player=player, world=world, env=env)
    current_updater.update()
    
    print(f"✅ Game state created")
    print(f"📍 Player position: {current_state.pos}")
    print(f"🧭 Facing direction: {current_state.get_facing_direction()}")
    print(f"🎯 Target material: {current_state.target_material}")
    
    print(f"\n🔍 Checking lan_wrapper:")
    print("-" * 30)
    if hasattr(current_state, 'lan_wrapper') and current_state.lan_wrapper:
        print(f"✅ lan_wrapper exists and has content:")
        print(f"📝 Content preview: {current_state.lan_wrapper[:200]}...")
        print(f"📏 Total length: {len(current_state.lan_wrapper)} characters")
    else:
        print(f"❌ lan_wrapper is empty or missing!")
        print(f"🔍 current_state.lan_wrapper = {getattr(current_state, 'lan_wrapper', 'MISSING')}")
    
    # Test the prompt generation
    print(f"\n🔍 Testing prompt generation:")
    print("-" * 30)
    action_space = initialize_action_space()
    recent_results = Recent_Results(num_of_results=5)
    
    try:
        prompt = build_complete_prompt(current_state, action_space, recent_results)
        if "9x9 Area Description:" in prompt:
            print("✅ 9x9 Area Description section found in prompt")
            # Extract just the area description part
            start = prompt.find("**9x9 Area Description:**")
            end = prompt.find("**📍 ACTIONS AVAILABLE", start)
            area_section = prompt[start:end] if end != -1 else prompt[start:start+300]
            print(f"📝 Area section preview:\n{area_section[:300]}...")
        else:
            print("❌ 9x9 Area Description section NOT found in prompt")
            
    except Exception as e:
        print(f"❌ Error generating prompt: {e}")

if __name__ == "__main__":
    test_lan_wrapper() 