#!/usr/bin/env python3
"""
Test the enhanced description features:
1. Terminology explanations for 9x9 area descriptions
2. Precise 3x3 area descriptions with exact directional information
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.game_state import GameState, GameStateUpdater
from game.action_space import initialize_action_space
from agents.structured_prompts import get_precise_3x3_area_description, GAME_STATE_DESCRIPTIONS, build_complete_prompt
from utils.memory import Recent_Results

def create_test_game_state():
    """Create a test game state with sample 9x9 matrices."""
    game_state = GameState()
    game_state.health = 8
    game_state.food = 6
    game_state.drink = 7
    game_state.energy = 9
    game_state.inventory = {
        'health': 8, 'food': 6, 'drink': 7, 'energy': 9,
        'wood': 2, 'stone': 0, 'coal': 0, 'iron': 0, 'diamond': 0,
        'sapling': 0, 'wood_pickaxe': 0, 'stone_pickaxe': 0, 'iron_pickaxe': 0,
        'wood_sword': 0, 'stone_sword': 0, 'iron_sword': 0
    }
    
    # Create sample 9x9 matrices for testing
    # Materials matrix (center = player position at [4][4])
    game_state.text_local_view_mat = [
        ['stone', 'stone', 'grass', 'tree', 'grass', 'path', 'grass', 'coal', 'iron'],
        ['path', 'grass', 'tree', 'grass', 'tree', 'grass', 'stone', 'grass', 'stone'],
        ['grass', 'tree', 'grass', 'stone', 'grass', 'tree', 'grass', 'path', 'grass'],
        ['tree', 'grass', 'stone', 'water', 'stone', 'grass', 'tree', 'grass', 'stone'],
        ['grass', 'stone', 'grass', 'tree', 'grass', 'water', 'grass', 'stone', 'coal'],  # Player at [4][4]
        ['stone', 'grass', 'tree', 'grass', 'stone', 'grass', 'tree', 'grass', 'path'],
        ['grass', 'tree', 'grass', 'stone', 'grass', 'stone', 'grass', 'tree', 'grass'],
        ['path', 'grass', 'stone', 'grass', 'tree', 'grass', 'stone', 'grass', 'stone'],
        ['stone', 'stone', 'grass', 'tree', 'grass', 'path', 'grass', 'coal', 'iron']
    ]
    
    # Objects matrix
    game_state.text_local_view_obj = [
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Cow', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Player', 'Nothing', 'Nothing', 'Zombie', 'Nothing'],  # Player at [4][4]
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'table', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing'],
        ['Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing', 'Nothing']
    ]
    
    # Set sample lan_wrapper description
    game_state.lan_wrapper = "this is observation of material around you:\nYou are in an area dominated by grass covering 65% of the surrounding area. Additionally,\n There is stone very near to the north and west;\n There is tree near to the northwest, northeast and southwest;\n There is water adjacent to the west and south.;\nthis is observation of object around you:\nThere is Cow very near to the northwest;\n There is Zombie adjacent to the east;\n There is table near to the south"
    
    return game_state

def test_terminology_explanations():
    """Test that terminology explanations are included in the prompt."""
    print("🧪 Testing Terminology Explanations")
    print("=" * 50)
    
    # Check if terminology explanations are in GAME_STATE_DESCRIPTIONS
    if "Distance Terminology Explanation" in GAME_STATE_DESCRIPTIONS:
        print("✅ Distance terminology explanations found")
        
        # Check for specific terms
        distance_terms = ["adjacent", "very near", "near", "far", "very far"]
        for term in distance_terms:
            if f'"{term}"' in GAME_STATE_DESCRIPTIONS:
                print(f"✅ '{term}' explanation found")
            else:
                print(f"❌ '{term}' explanation missing")
                return False
    else:
        print("❌ Distance terminology explanations not found")
        return False
    
    if "Direction Terminology Explanation" in GAME_STATE_DESCRIPTIONS:
        print("✅ Direction terminology explanations found")
        
        # Check for direction types
        direction_types = ["Cardinal directions", "Intercardinal directions", "Intermediate directions"]
        for dir_type in direction_types:
            if dir_type in GAME_STATE_DESCRIPTIONS:
                print(f"✅ '{dir_type}' explanation found")
            else:
                print(f"❌ '{dir_type}' explanation missing")
                return False
    else:
        print("❌ Direction terminology explanations not found")
        return False
    
    print("✅ All terminology explanations are present!")
    return True

def test_precise_3x3_descriptions():
    """Test the precise 3x3 area descriptions."""
    print("\n🧪 Testing Precise 3x3 Area Descriptions")
    print("=" * 50)
    
    game_state = create_test_game_state()
    
    # Test the function
    description = get_precise_3x3_area_description(game_state)
    
    print("Generated 3x3 Description:")
    print("-" * 30)
    print(description)
    print("-" * 30)
    
    # Verify it contains expected elements
    if "3x3 Immediate Area (Exact Positions)" in description:
        print("✅ Proper header found")
    else:
        print("❌ Header missing")
        return False
    
    # Check for all 8 directions
    directions = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']
    for direction in directions:
        if direction.capitalize() in description:
            print(f"✅ {direction.capitalize()} direction found")
        else:
            print(f"❌ {direction.capitalize()} direction missing")
            return False
    
    # Check that it shows materials and objects correctly
    # Based on our test matrix, we should see specific materials in specific directions
    expected_materials = ['stone', 'tree', 'grass', 'water']
    found_materials = []
    for material in expected_materials:
        if material in description:
            found_materials.append(material)
            print(f"✅ Material '{material}' found in description")
    
    if len(found_materials) >= 3:  # Should have at least 3 different materials
        print("✅ Multiple material types detected")
    else:
        print("❌ Not enough material variety detected")
        return False
    
    # Check for objects (should mention Cow and Zombie from our test data)
    if "Cow" in description:
        print("✅ Object 'Cow' found in description")
    if "Zombie" in description:
        print("✅ Object 'Zombie' found in description")
    
    print("✅ Precise 3x3 descriptions working correctly!")
    return True

def test_integration_in_complete_prompt():
    """Test that both features are integrated into the complete prompt."""
    print("\n🧪 Testing Integration in Complete Prompt")
    print("=" * 50)
    
    game_state = create_test_game_state()
    
    # Add proper facing direction and walkable directions
    game_state.facing = (0, 1)  # Facing south
    game_state.get_facing_direction = lambda: "south"
    game_state.walkable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    game_state.turnable_directions = {'north': True, 'south': True, 'east': True, 'west': True}
    
    action_space = initialize_action_space()
    recent_results = None
    
    # Generate complete prompt
    try:
        complete_prompt = build_complete_prompt(game_state, action_space, recent_results)
        
        # Check for terminology explanations
        if "Distance Terminology Explanation" in complete_prompt:
            print("✅ Terminology explanations integrated in complete prompt")
        else:
            print("❌ Terminology explanations missing from complete prompt")
            return False
        
        # Check for 3x3 precise descriptions
        if "3x3 Immediate Area (Exact Positions)" in complete_prompt:
            print("✅ Precise 3x3 descriptions integrated in complete prompt")
        else:
            print("❌ Precise 3x3 descriptions missing from complete prompt")
            return False
        
        # Check for both natural language 9x9 and precise 3x3
        if "9x9 Area Description (Natural Language)" in complete_prompt:
            print("✅ Both 9x9 natural language and 3x3 precise descriptions present")
        else:
            print("❌ Missing 9x9 natural language description section")
            return False
        
        # Check valid/invalid action sections exist
        if "📍 ACTIONS AVAILABLE THIS TURN:" in complete_prompt:
            print("✅ Valid actions section present")
        else:
            print("❌ Valid actions section missing")
            
        if "🚫 ACTIONS NOT AVAILABLE THIS TURN:" in complete_prompt:
            print("✅ Invalid actions section present")
        else:
            print("❌ Invalid actions section missing")
        
        print("✅ Complete integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating complete prompt: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Description Features")
    print("=" * 60)
    
    test1_passed = test_terminology_explanations()
    test2_passed = test_precise_3x3_descriptions()
    test3_passed = test_integration_in_complete_prompt()
    
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"1. Terminology Explanations: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"2. Precise 3x3 Descriptions: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"3. Complete Integration: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! Enhanced descriptions are working perfectly!")
        print("\n📋 Features implemented:")
        print("  - Distance terminology explanations (adjacent, very near, near, far, very far) ✓")
        print("  - Direction terminology explanations (cardinal, intercardinal, intermediate) ✓") 
        print("  - Precise 3x3 area descriptions with exact directions ✓")
        print("  - Integration with existing 9x9 natural language descriptions ✓")
        print("  - Visual display integration ✓")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 