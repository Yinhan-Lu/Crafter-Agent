"""
Structured prompt system for Crafter following the 10-part structure:
1. Basic Crafter rules
2. Material properties
3. Creature properties
4. Action descriptions (with dynamic valid/invalid actions)
5. Tool descriptions
6. Game state descriptions
7. Current state
8. Goal descriptions (fixed + dynamic subgoals)
9. ReAct framework
10. Recent history
11. Answer format requirements
"""

# Import only what's absolutely necessary at module level
from typing import Any, Dict, List
# from game.game_state import GameState
# from game.action_space import ActionSpace  
# from utils.memory import RecentResults

# ============================================================================
# 1. CRAFTER BASIC RULES (General game info, not specific actions/materials)
# ============================================================================

CRAFTER_BASIC_RULES = """
### Crafter Game Environment - Basic Rules

**Game Overview:**
Crafter is a 2D open-world survival sandbox game played on a 64x64 grid. Each game starts in a unique procedurally generated world containing grasslands, lakes, mountains with forests, caves, ores, and lava.

**Primary Objective:**
Your overarching goal is to **survive** as long as possible and eventually **find and collect a diamond**, which is the most challenging achievement in the game.

**Core Survival Mechanics:**
- You have four vital stats: Health, Food, Drink, and Energy (all max value 9)
- You must manage these stats to avoid death
- The game ends if your health reaches 0 or after 10000 steps
- Each episode presents different challenges and requires strategic decision-making

**Game World Structure:**
- 2D grid-based movement with cardinal directions (north, south, east, west)
- Different biomes: grasslands, caves, mountains, lakes
- Day/night cycle affects monster behavior
- Hostile creatures appear in dark areas or at night

**Basic Interaction Rules:**
- You can only perform one action per turn
- You must face a target to interact with it (collect, attack, etc.)
- Tools are required for advanced resource gathering
- Crafting requires specific workstations and materials
"""

# ============================================================================
# 2. MATERIAL PROPERTIES
# ============================================================================

MATERIAL_PROPERTIES = """
### Material Properties

**Walkable Surfaces (Can move on these):**
- **grass**: Common walkable surface, can occasionally yield saplings
- **path**: Walkable surface left behind after mining certain materials  
- **sand**: Walkable surface found in certain biomes

**Collectible Resources:**
- **tree**: Source of wood, can be collected without tools, leaves grass when collected
- **stone**: Used for crafting and building, requires wood_pickaxe to collect, leaves path when mined
- **coal**: Material for advanced crafting, requires wood_pickaxe to collect, leaves path when mined
- **iron**: Required for advanced tools, requires stone_pickaxe to collect, leaves path when mined
- **diamond**: Rarest material for strongest tools, requires iron_pickaxe to collect, leaves path when mined
- **water**: Found in lakes, used to restore drink meter, can be collected without tools

**Dangerous Materials:**
- **lava**: Causes damage if walked on, avoid contact

**Placed Structures:**
- **table**: Crafting workstation, can be placed on grass/sand/path
- **furnace**: Advanced crafting station, can be placed on grass/sand/path
"""

# ============================================================================
# 3. CREATURE PROPERTIES  
# ============================================================================

CREATURE_PROPERTIES = """
### Creature Properties

**Passive Creatures (Can be hunted for food):**
- **cow**: Peaceful animal that can be hunted for food
  - Requires wood_sword or better to hunt effectively
  - Provides +3 food when consumed
  - Disappears when killed, leaving walkable terrain

**Hostile Creatures (Will attack on sight):**
- **zombie**: Hostile monster that attacks players
  - Appears in dark areas or at night
  - Reduces health when it attacks you
  - Can be defeated with sword weapons
  - Disappears when defeated, leaving walkable terrain

- **skeleton**: Hostile monster that attacks players
  - Appears in dark areas or at night  
  - Reduces health when it attacks you
  - Can be defeated with sword weapons
  - May shoot arrows at range
  - Disappears when defeated, leaving walkable terrain

**Player:**
- **Player**: Your character in the game world, appears as "Player" in object descriptions
"""

# ============================================================================
# 4. ACTION DETAILED DESCRIPTIONS
# ============================================================================

ACTION_DESCRIPTIONS = """
### Action Detailed Descriptions

**Movement Actions:**
- **move_north/move_south/move_east/move_west**: Move one step in the specified direction
  - Precondition: Target location must be walkable (grass, path, sand)
  - Effect: Changes player position by one tile

**Turning Actions:**
- **turn_north/turn_south/turn_east/turn_west**: Change facing direction without moving
  - Precondition: Always possible
  - Effect: Changes facing direction, affects which objects/materials become targets. When you need to take an action in a object/material one step away but you are not facing it(e.g. you are facing north but the object is to the east), you need to turn to the direction of the object/material first to make sure it is your target.

**Collection Actions:**
- **collect_wood**: Collect wood from trees
  - Precondition: Must be facing a tree
  - Effect: +1 wood in inventory, tree becomes grass
  
- **collect_stone**: Mine stone deposits  
  - Precondition: Must be facing stone AND have wood_pickaxe in inventory
  - Effect: +1 stone in inventory, stone becomes path

- **collect_coal**: Mine coal deposits
  - Precondition: Must be facing coal AND have wood_pickaxe in inventory  
  - Effect: +1 coal in inventory, coal becomes path

- **collect_iron**: Mine iron deposits
  - Precondition: Must be facing iron AND have stone_pickaxe in inventory
  - Effect: +1 iron in inventory, iron becomes path

- **collect_diamond**: Mine diamond deposits
  - Precondition: Must be facing diamond AND have iron_pickaxe in inventory
  - Effect: +1 diamond in inventory, diamond becomes path

- **collect_water**: Collect water from lakes
  - Precondition: Must be facing water
  - Effect: +1 drink in inventory

- **collect_grass**: Collect saplings from grass
  - Precondition: Must be facing grass
  - Effect: +1 sapling in inventory (chance-based)

**Combat/Hunting Actions:**
- **attach_cow**: Hunt cows for food
  - Precondition: Must be facing cow AND have wood_sword in inventory
  - Effect: +3 food in inventory, cow disappears

**Crafting Actions:**
- **make_wood_pickaxe**: Craft basic mining tool
  - Precondition: Must be adjacent to table AND have 1+ wood in inventory
  - Effect: -1 wood, +1 wood_pickaxe in inventory

- **make_stone_pickaxe**: Craft advanced mining tool
  - Precondition: Must be adjacent to table AND have 1+ wood AND 2+ stone in inventory  
  - Effect: -1 wood, -2 stone, +1 stone_pickaxe in inventory

- **make_iron_pickaxe**: Craft highest tier mining tool
  - Precondition: Must be adjacent to table AND furnace AND have 1+ wood, 1+ coal, 1+ iron
  - Effect: -1 wood, -1 coal, -1 iron, +1 iron_pickaxe in inventory

- **make_wood_sword**: Craft basic weapon
  - Precondition: Must be adjacent to table AND have 1+ wood in inventory
  - Effect: -1 wood, +1 wood_sword in inventory

- **make_stone_sword**: Craft advanced weapon  
  - Precondition: Must be adjacent to table AND have 1+ wood AND 2+ stone in inventory
  - Effect: -1 wood, -2 stone, +1 stone_sword in inventory

- **make_iron_sword**: Craft highest tier weapon
  - Precondition: Must be adjacent to table AND furnace AND have 1+ wood, 1+ coal, 1+ iron
  - Effect: -1 wood, -1 coal, -1 iron, +1 iron_sword in inventory

**Placement Actions:**
- **place_table**: Place crafting workstation
  - Precondition: Must be facing walkable terrain (grass/sand/path) AND have 2+ wood
  - Effect: -2 wood, table appears at target location

- **place_furnace**: Place advanced crafting station
  - Precondition: Must be facing walkable terrain (grass/sand/path) AND have appropriate materials
  - Effect: Materials consumed, furnace appears at target location

- **place_stone**: Place stone block
  - Precondition: Must be facing placeable terrain AND have 1+ stone  
  - Effect: -1 stone, stone appears at target location

- **place_plant**: Plant sapling to grow trees
  - Precondition: Must be facing grass AND have 1+ sapling
  - Effect: -1 sapling, planted sapling at target location

**Utility Actions:**
- **sleep**: Rest to recover energy
  - Precondition: Energy not at maximum (less than 9)
  - Effect: Restores energy to maximum, passes time, may heal if not hungry/thirsty

"""

# ============================================================================
# 5. TOOL DETAILED DESCRIPTIONS
# ============================================================================

TOOL_DESCRIPTIONS = """
### Tool Detailed Descriptions

**Mining Tools (Pickaxes):**
- **wood_pickaxe**: Basic mining tool
  - Acquisition: Craft at table using 1 wood
  - Uses: Required to mine stone and coal
  - Duration: Permanent (doesn't break)

- **stone_pickaxe**: Advanced mining tool  
  - Acquisition: Craft at table using 1 wood + 2 stone
  - Uses: Required to mine iron (can also mine stone/coal)
  - Duration: Permanent (doesn't break)

- **iron_pickaxe**: Highest tier mining tool
  - Acquisition: Craft at table+furnace using 1 wood + 1 coal + 1 iron
  - Uses: Required to mine diamonds (can mine all materials)
  - Duration: Permanent (doesn't break)

**Combat Tools (Swords):**
- **wood_sword**: Basic weapon
  - Acquisition: Craft at table using 1 wood
  - Uses: Required to hunt cows effectively, fight monsters
  - Duration: Permanent (doesn't break)

- **stone_sword**: Advanced weapon
  - Acquisition: Craft at table using 1 wood + 2 stone  
  - Uses: More effective for combat than wood sword
  - Duration: Permanent (doesn't break)

- **iron_sword**: Highest tier weapon
  - Acquisition: Craft at table+furnace using 1 wood + 1 coal + 1 iron
  - Uses: Most effective weapon for combat
  - Duration: Permanent (doesn't break)

**Workstations:**
- **table** (Crafting Table): Basic crafting station
  - Acquisition: Place using 2 wood on walkable terrain
  - Uses: Required for crafting all tools and weapons
  - Placement: On grass, sand, or path surfaces

- **furnace**: Advanced crafting station
  - Acquisition: Place using appropriate materials on walkable terrain
  - Uses: Required for crafting iron-tier tools and weapons
  - Placement: On grass, sand, or path surfaces
  - Must be used together with table for iron crafting
"""

# ============================================================================
# 6. GAME STATE DETAILED DESCRIPTIONS
# ============================================================================

GAME_STATE_DESCRIPTIONS = """
### Game State Detailed Descriptions

**Health System (0-9):**
- **9-7**: Healthy condition, no immediate danger
- **6-4**: Injured but stable, consider healing
- **3-1**: Critical condition, prioritize survival  
- **0**: Death - game over
- Health regenerates slowly when food > 3, drink > 3, and energy > 3
- Health decreases when any vital stat reaches 0

**Food System (0-9):**
- **9-6**: Well fed, no food concerns
- **5-3**: Getting hungry, consider finding food soon
- **2-1**: Very hungry, health will start decreasing
- **0**: Starving, health decreases each turn
- Restore by hunting cows (+3 food) or eating plants
- Decreases naturally over time

**Drink System (0-9):**
- **9-6**: Well hydrated, no drink concerns  
- **5-3**: Getting thirsty, consider finding water soon
- **2-1**: Very thirsty, health will start decreasing
- **0**: Dehydrated, health decreases each turn
- Restore by collecting water from lakes
- Decreases naturally over time

**Energy System (0-9):**
- **9-6**: Well rested, no energy concerns
- **5-3**: Getting tired, consider sleeping soon
- **2-1**: Very tired, health will start decreasing  
- **0**: Exhausted, health decreases each turn
- Restore by sleeping (action: sleep)
- Decreases with activity

**Facing Direction:**
- Determines which material/object becomes your target
- Must face targets to interact with them (collect, attack, etc.)
- Can be changed using turn actions without moving
- Critical for efficient resource gathering and combat

**Environmental Awareness:**
- 9x9 grid around player shows nearby materials and objects
- Walkable directions indicate valid movement options
- Blocked directions show obstacles or dangerous terrain
- Distance matters for strategic planning and pathfinding

**Distance Terminology Explanation:**
The game uses specific distance terms in area descriptions:
- **"adjacent"**: Items exactly 1 tile away (immediately next to you)
- **"very near"**: Items 2-3 tiles away (very close vicinity)
- **"near"**: Items 4-5 tiles away (close but requires some movement)
- **"far"**: Items 6-20 tiles away (requires significant movement)
- **"very far"**: Items beyond 20 tiles away (distant, may require exploration)

**Direction Terminology Explanation:**
Directions are specified using:
- **Cardinal directions**: north, south, east, west (primary compass directions)
- **Intercardinal directions**: northeast, northwest, southeast, southwest (diagonal directions)
- **Intermediate directions**: northnortheast, eastnortheast, etc. (between cardinal and intercardinal)
"""

# ============================================================================
# 7. CURRENT STATE (Abstract - to be filled by function call)
# ============================================================================

def get_precise_3x3_area_description(game_state):
    """
    Generate precise 3x3 area description showing exact materials and objects
    in each of the 8 directions around the player.
    
    Args:
        game_state: The current game state
        
    Returns:
        str: Detailed description of the immediate 3x3 area around the player
    """
    if not hasattr(game_state, 'text_local_view_mat') or not game_state.text_local_view_mat:
        return "**3x3 Immediate Area:** No detailed area information available."
    
    if not hasattr(game_state, 'text_local_view_obj') or not game_state.text_local_view_obj:
        obj_matrix = [["Nothing" for _ in range(9)] for _ in range(9)]
    else:
        obj_matrix = game_state.text_local_view_obj
    
    mat_matrix = game_state.text_local_view_mat
    
    # Transpose matrices to match game coordinate system
    mat_transposed = list(zip(*mat_matrix))
    obj_transposed = list(zip(*obj_matrix))
    
    # Center position is (4, 4) in the 9x9 grid
    center_x, center_y = 4, 4
    
    # Define the 8 directions and their relative positions
    directions = {
        'north': (center_y - 1, center_x),
        'northeast': (center_y - 1, center_x + 1),
        'east': (center_y, center_x + 1),
        'southeast': (center_y + 1, center_x + 1),
        'south': (center_y + 1, center_x),
        'southwest': (center_y + 1, center_x - 1),
        'west': (center_y, center_x - 1),
        'northwest': (center_y - 1, center_x - 1)
    }
    
    descriptions = []
    
    for direction_name, (y, x) in directions.items():
        # Get material and object at this position
        material = mat_transposed[y][x] if 0 <= y < len(mat_transposed) and 0 <= x < len(mat_transposed[0]) else "unknown"
        obj = obj_transposed[y][x] if 0 <= y < len(obj_transposed) and 0 <= x < len(obj_transposed[0]) else "Nothing"
        
        # Clean up the values
        if material in ['None', 'Nothing', None]:
            material = "unknown"
        if obj in ['None', 'Nothing', None]:
            obj = None
        
        # Create description for this direction
        if obj and obj != "Nothing":
            descriptions.append(f"**{direction_name.capitalize()}**: {material} with {obj}")
        else:
            descriptions.append(f"**{direction_name.capitalize()}**: {material}")
    
    # Arrange descriptions in a logical order (clockwise from north)
    ordered_directions = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']
    direction_map = {desc.split(':')[0].replace('*', '').strip().lower(): desc for desc in descriptions}
    
    ordered_descriptions = []
    for direction in ordered_directions:
        if direction in direction_map:
            ordered_descriptions.append(direction_map[direction])
    
    description = "**3x3 Immediate Area (Exact Positions):**\n" + "\n".join(ordered_descriptions)
    
    return description

def get_current_state_prompt(game_state, action_space):
    """
    Function to generate current state description.
    This includes the current game state AND the valid/invalid actions for this turn.
    """
    # Enhanced inventory display to reduce AI hallucination
    materials = ['wood', 'stone', 'coal', 'iron', 'diamond', 'sapling']
    tools = ['wood_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'wood_sword', 'stone_sword', 'iron_sword']
    
    # Separate materials and tools
    material_items = [f"{item}: {game_state.inventory.get(item, 0)}" for item in materials if game_state.inventory.get(item, 0) > 0]
    tool_items = [f"{item}: {game_state.inventory.get(item, 0)}" for item in tools if game_state.inventory.get(item, 0) > 0]
    
    # Create clear inventory display
    if material_items and tool_items:
        inventory_str = f"Materials: {', '.join(material_items)} | Tools: {', '.join(tool_items)}"
    elif material_items:
        inventory_str = f"Materials: {', '.join(material_items)} | Tools: None"
    elif tool_items:
        inventory_str = f"Materials: None | Tools: {', '.join(tool_items)}"
    else:
        inventory_str = "Materials: None | Tools: None"
    
    # Get facing direction if available
    facing_direction = "Unknown"
    if hasattr(game_state, 'get_facing_direction'):
        try:
            facing_direction = game_state.get_facing_direction()
        except:
            facing_direction = "Unknown"
    
    # Get target material and object
    target_material = getattr(game_state, 'target_material', 'None')
    target_obj = getattr(game_state, 'target_obj', None)
    target_obj_str = str(type(target_obj).__name__) if target_obj else "None"
    
    # Get the natural language description of 9x9 area (section 7.2)
    area_description = getattr(game_state, 'lan_wrapper', 'No area description available')
    
    # Get precise 3x3 area description
    precise_3x3_description = get_precise_3x3_area_description(game_state)
    
    return f"""### Current Game State

**Player Status:**
- Health: {game_state.health}/9
- Food: {game_state.food}/9  
- Drink: {game_state.drink}/9
- Energy: {game_state.energy}/9

**Inventory:** {inventory_str}

**⚠️ IMPORTANT INVENTORY NOTE:**
- If you have ZERO wood, you CANNOT craft items that require wood
- Tools like "wood_pickaxe" are NOT the same as having "wood" material
- Always check the Materials section to see what you can actually use for crafting

**Environment:**
- Facing Direction: {facing_direction}
- Target Material: {target_material}
- Target Object: {target_obj_str}

{precise_3x3_description}

**9x9 Area Description (Natural Language):**
{area_description}

**📍 ACTIONS AVAILABLE THIS TURN:**
{action_space.get_valid_action_prompt(game_state)}

**🚫 ACTIONS NOT AVAILABLE THIS TURN:**
{action_space.get_invalid_action_prompt(game_state)}

**Note:** Only the actions listed as "AVAILABLE THIS TURN" can be executed right now. The invalid actions show you what requirements are needed to unlock them."""

# ============================================================================
# 8. REACT FRAMEWORK DESCRIPTION
# ============================================================================

REACT_FRAMEWORK_DESCRIPTION = """
### ReAct Framework Instructions

You are an AI agent using the **ReAct (Reasoning + Acting)** framework to play Crafter. This means you alternate between reasoning about the situation and taking actions based on your analysis.

**For each step, follow this structure:**

1. **Observation**: Analyze the current environment, inventory, and game state
2. **Reasoning**: Think step by step about:
   - What your immediate needs are (health, food, drink, energy)
   - What resources you need to progress
   - What actions are available vs unavailable and why
   - What the best next action would be to achieve your goals
3. **Action**: Choose one specific action from the available legal actions

**Example ReAct Cycle:**

**Observation**: "The player is standing near trees with no wood in inventory. Health is good but no tools are available for advanced resource gathering."

**Reasoning**: "I need wood to craft basic tools. There are trees nearby that I can collect from without any tools required. Collecting wood should be my first priority to enable crafting a wood pickaxe, which will let me mine stone and coal for more advanced tools."

**Action**: "collect_wood"

**Key Principles:**
- Always observe before reasoning
- Reason through your priorities and constraints  
- Choose actions that progress toward your survival and diamond collection goals
- Consider both immediate needs (survival) and long-term goals (diamond)
- Plan ahead but stay flexible based on environmental changes
"""

# ============================================================================
# 9. RECENT RESULTS (Abstract - to be filled by memory system)
# ============================================================================

def get_recent_results_prompt(recent_results):
    """
    Function to format recent step results.
    This works with the Recent_Results class from memory.py
    """
    if not recent_results or len(recent_results.result_buffer) == 0:
        return "### Recent History\n\nNo previous actions recorded."
    
    prompt = "### Recent History\n\n"
    for i, result in enumerate(list(recent_results.result_buffer)[-5:], 1):  # Last 5 steps
        k = result.current_step
        prompt += f"**Step {result.current_step}:**\n"
        prompt += f"- Observation: {result.observation}\n" 
        prompt += f"- Reasoning: {result.reasoning}\n"
        prompt += f"- Action: {result.action}\n\n"
    prompt+=f"now, you need to do decision for step {k} based on the recent history."
    return prompt

# ============================================================================
# 10. ANSWER FORMAT REQUIREMENTS
# ============================================================================
def get_answer_format_requirements(action_space, game_state):
    ANSWER_FORMAT_REQUIREMENTS = f"""
### Answer Format Requirements

**You MUST return your response in valid JSON format with exactly these keys:**

```json
{{
  "observation": "Your observation of the current situation",
  "reasoning": "Your step-by-step reasoning process", 
  "action": "Your chosen action"
}}
```

**Critical Requirements:**
1. **JSON Validity**: Your response must be parseable by `json.loads()` function
2. **Required Keys**: Must include "observation", "reasoning", and "action" 
3. **Action Constraint**: The "action" value must be EXACTLY one of these valid actions this turn::
   ```
   {action_space.get_valid_action_prompt(game_state)}
   ```
   the reason why you can't use the invalid actions is that the precondition is not met.
   the precondition can be found in Action Detailed Descriptions above.

4. **No Extra Actions**: Do NOT use "do" action or any action not in the above list
5. **String Format**: All values should be strings, properly escaped for JSON
6. **No Comments**: Do not include any text outside the JSON object

**Example Valid Response:**
```json
{{
  "observation": "I see trees nearby and my inventory is empty. I need wood to start crafting.",
  "reasoning": "Wood is essential for making basic tools. I can collect wood from trees without any requirements. This should be my first priority.",
  "action": "collect_wood"
}}
```
"""
    return ANSWER_FORMAT_REQUIREMENTS

# ============================================================================
# MASTER PROMPT BUILDER  
# ============================================================================

def get_goal_descriptions(game_state) -> str:
    """
    Section 8: Goal descriptions including fixed goals and dynamic subgoals.
    
    Fixed goal: Find diamond
    Dynamic subgoal: Generated by subgoal manager based on current inventory, condition, and environment
    """
    # Import here to avoid circular imports
    try:
        from planning.sub_goal_manager import SubgoalManager
        subgoal_manager = SubgoalManager()
        subgoal_manager.update_plan(game_state)
        current_subgoal = subgoal_manager.get_current_subgoal()
    except Exception as e:
        current_subgoal = f"Error getting subgoal: {str(e)}"
    
    return f"""
### Goal Descriptions

**Main Objective (Fixed Goal):**
Your ultimate goal is to find and collect a diamond. This is the primary objective that all your actions should work towards. Diamonds are rare resources found deep underground, typically near iron, coal, stone, lava, and paths. You will need advanced tools (iron pickaxe) to mine diamonds.

**Current Subgoal (Dynamic):**
{current_subgoal}

This subgoal is automatically determined based on your current inventory, health status, surrounding environment, and progress towards the main goal. Focus on completing this subgoal as it represents the most important immediate action to advance towards finding the diamond.

**Goal Hierarchy:**
1. **Immediate survival needs** (health, food, water, energy) - Always highest priority
2. **Current dynamic subgoal** - Focus on this for progression
3. **Main objective** - Find diamond (long-term goal)

Remember: The subgoal will automatically update as your situation changes. Always prioritize survival, then follow the current subgoal to make optimal progress towards the diamond.
"""

def build_complete_prompt(game_state, action_space, recent_results=None):
    """
    Build the complete prompt following the 10-part structure specified in the comment:
    1. Basic Crafter rules
    2. Material properties  
    3. Creature properties
    4. Action descriptions
    5. Tool descriptions
    6. Game state descriptions
    7. Current state
    8. Goal descriptions (fixed + dynamic subgoals)
    9. ReAct framework
    10. Recent history
    11. Answer format requirements
    """
    
    prompt_parts = [
        CRAFTER_BASIC_RULES,
        MATERIAL_PROPERTIES, 
        CREATURE_PROPERTIES,
        ACTION_DESCRIPTIONS,
        TOOL_DESCRIPTIONS,
        GAME_STATE_DESCRIPTIONS,
        get_current_state_prompt(game_state, action_space),
        get_goal_descriptions(game_state),
        REACT_FRAMEWORK_DESCRIPTION,
        get_recent_results_prompt(recent_results) if recent_results else "### Recent History\n\nNo previous actions recorded.",
        get_answer_format_requirements(action_space, game_state)
    ]
    print(get_recent_results_prompt(recent_results))
    return "\n".join(prompt_parts) 