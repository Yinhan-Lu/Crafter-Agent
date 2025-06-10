
env_description_prompt = """
        You are an agent in a procedurally generated 2D survival world called Crafter. Your goal is to explore, collect resources, 
        craft tools, place objects, fight monsters, and survive. Each episode, you face different challenges, and your task is to
        unlock as many achievements as possible by making the right decisions. Below are the detailed descriptions of the environment,
        your available actions, and the mechanics you need to know to succeed.
        """

actions_prompt = """
        
        # ### Actions:
        # - noop: Do nothing.
        # - move_left, move_right, move_up, move_down: Move in the respective direction.
        # - do: Interact with the object in front of you (e.g., collect resources, attack enemies).
        # - sleep: Rest to restore energy. Use when your energy is low.
        # - place_stone, place_table, place_furnace, place_plant: Place items in the environment.
        # - place_stone: Place a stone on walkable terrain (grass, sand, path, water, lava).
        # - place_table: Place a crafting table to craft tools.
        # - place_furnace: Place a furnace to smelt resources.
        # - place_plant: Place a sapling to grow trees.
        # - make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe: Craft different levels of pickaxes.
        # - wood_pickaxe: Used for collecting basic resources like stone and coal.
        # - stone_pickaxe: Allows mining of harder materials like iron.
        # - iron_pickaxe: Necessary for mining diamonds.
        # - make_wood_sword, make_stone_sword, make_iron_sword: Craft different levels of swords for combat.

        # ### Materials:
        # - water: Found in lakes, used to drink and restore the thirst meter.
        # - grass: A common walkable surface that can yield saplings for planting.
        # - stone: Used for crafting and placing objects like furnaces.
        # - path: A walkable surface left behind after mining certain materials.
        # - sand: A walkable surface found in certain biomes.
        # - tree: Chop down to collect wood, essential for crafting.
        # - lava: Dangerous, causes damage if walked on.
        # - coal: A material used for crafting advanced items, mined with a pickaxe.
        # - iron: Required for crafting advanced tools like iron pickaxes and swords.
        # - diamond: The rarest material, used for the strongest tools, mined with an iron pickaxe.
        # - table: A crafting table, placed to craft tools.
        # - furnace: Used for smelting iron and crafting advanced items.

        # ### Walkable Surfaces:
        # - grass, path, sand: These surfaces can be walked on safely.

        # ### Items:
        # - health (max: 9): Your health points. If they reach zero, you die. 
        # - food (max: 9): Eat cows or plants to restore food.
        # - drink (max: 9): Drink water to restore thirst.
        # - energy (max: 9): Sleep to restore energy.
        # - sapling, wood, stone, coal, iron, diamond: Collect these resources for crafting and building.
        # - wood_pickaxe, stone_pickaxe, iron_pickaxe: Tools for mining.
        # - wood_sword, stone_sword, iron_sword: Weapons for combat.

        # ### Collecting Resources:
        # - tree: No tool required, provides wood. 
        # - stone: Requires wood_pickaxe, provides stone.
        # - coal: Requires wood_pickaxe, provides coal.
        # - iron: Requires stone_pickaxe, provides iron.
        # - diamond: Requires iron_pickaxe, provides diamonds.
        # - water: Collect from lakes to restore drink.
        # - grass: Occasionally yields saplings for planting.

        # ### Crafting Items:
        # - wood_pickaxe: Requires wood and a nearby crafting table.
        # - stone_pickaxe: Requires wood, stone, and a nearby crafting table.
        # - iron_pickaxe: Requires wood, coal, iron, and both a table and furnace.
        # - wood_sword: Requires wood and a nearby crafting table.
        # - stone_sword: Requires wood, stone, and a nearby crafting table.
        # - iron_sword: Requires wood, coal, iron, and both a table and furnace.

        # ### Placing Objects:
        # - stone: Place on grass, sand, path, water, or lava.
        # - table: Place on grass, sand, or path.
        # - furnace: Place on grass, sand, or path.
        # - plant: Place saplings on grass to grow trees.

        # ### Achievements:
        # Unlock achievements by completing tasks:
        # - collect_coal: Collect coal by mining with a wood_pickaxe.
        # - collect_diamond: Collect diamond with an iron_pickaxe.
        # - collect_drink: Drink water from a lake.
        # - collect_iron: Collect iron with a stone_pickaxe.
        # - collect_sapling: Collect saplings from grass.
        # - collect_stone: Collect stone with a wood_pickaxe.
        # - collect_wood: Collect wood from trees.
        # - defeat_skeleton: Defeat a skeleton in combat.
        # - defeat_zombie: Defeat a zombie in combat.
        # - eat_cow: Eat meat from a cow.
        # - eat_plant: Eat a plant.
        # - make_iron_pickaxe: Craft an iron_pickaxe.
        # - make_iron_sword: Craft an iron_sword.
        # - make_stone_pickaxe: Craft a stone_pickaxe.
        # - make_stone_sword: Craft a stone_sword.
        # - make_wood_pickaxe: Craft a wood_pickaxe.
        # - make_wood_sword: Craft a wood_sword.
        # - place_furnace: Place a furnace.
        # - place_plant: Plant a sapling.
        # - place_stone: Place a stone.
        # - place_table: Place a crafting table.
        # - wake_up: Wake up after sleeping.

        # Use the available actions, manage your resources effectively, and survive as long as possible. Unlock as many achievements as you can by making strategic decisions based on the environment and your current state.
        # """



def reasoning_way_prompt_creator(action_space):
    reasoning_way_prompt = f"""
            You are an AI agent that uses the ReAct (Reasoning + Acting). Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 
    
        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be either:
            2.1. one exact word in the list: {action_space}  that reflects your next move.
            2.2. or you can do "read document". In this case, you would read document module in which you can select a chapter from a documentation book to read, and then do the action. 
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.
    
        ### Example:
        #### Step 1:
        - **Observation**: The player is standing near a forest of trees. There is no wood in the player's inventory, 
        but they need wood to craft basic tools.
        - **Reasoning**: Wood is essential for crafting basic tools such as pickaxes. The trees nearby are a good 
        source of wood.
        - **Action**: do

        #### Step 2:
        - **Observation**: The player has collected wood from the trees and now stands near a crafting table.
        - **Reasoning**: The collected wood can now be used to craft a wood pickaxe at the crafting table, which will 
        enable the collection of stone for advanced tools.
        - **Action**: make_wood_pickaxe
        """
    return reasoning_way_prompt

def language_wrapper_description_prompt_creator(lan_wrapper):
        language_wrapper_prompt = f"""
             environment uses a specialized language wrapper to communicate the game state. Here are the key rules for understanding the observations:
                1. Distance Rules
                Objects are described using distance buckets relative to your position:

                "adjacent" for items 1 tile away
                "very near" for items up to 3 tiles away
                "near" for items up to 5 tiles away
                "far" for items up to 20 tiles away
                "very far" for items beyond 20 tiles

                2. Direction Rules
                Directions are specified using cardinal and intercardinal points:

                Cardinal: north, south, east, west
                Intercardinal: northeast, northwest, southeast, southwest
                Intermediate directions like "northnortheast" for positions between cardinal and intercardinal points

                3. Observation Format

                Each object is described as: "[object name] [distance] [direction]"
                Multiple objects in the same distance/direction are grouped together
                When multiples of the same object exist, they are pluralized
                Observations are joined with semicolons
                Objects are listed by distance (closest to farthest)

                the language description of the local view are:{lan_wrapper}\n"""
        return language_wrapper_prompt
format_prompt="""
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
      "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
      "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
      "action": "place_plant"
    }.
        """



# class PromptBuilder:
#     """
#     Integrates GameRules, GameStateParser, SubgoalManager, and optionally ReActManager to build the final prompt for the LLM.
#     """
#     def __init__(self, 
#                  game_rules: CrafterGameRules, 
#                  state_parser: Optional[GameStateParser] = None, 
#                  subgoal_manager: Optional[SubgoalManager] = None, 
#                  react_manager: Optional[ReActManager] = None):
#         # Accept instances of the components (or create default ones if not provided).
#         self.game_rules = game_rules
#         self.state_parser = state_parser or GameStateParser()
#         self.subgoal_manager = subgoal_manager or SubgoalManager()
#         self.react_manager = react_manager or ReActManager()
    
#     def state_text_creator(self, state: dict) -> str:
#         """
#         Create the state text for the prompt.
#         state: the state of the game
#         return: the state text
#         """


#         state_text = ""
#         stats_line = ""
#         if 'health' in state:
#             # Assuming health is out of 10.
#             stats_line += f"Health: {state['health']}/10, "
#         if 'hunger' in state:
#             stats_line += f"Hunger: {state['hunger']}/10, "
#         if 'thirst' in state:
#             stats_line += f"Thirst: {state['thirst']}/10, "
#         if 'energy' in state:
#             stats_line += f"Energy: {state['energy']}/10"
#         # Remove trailing comma if any:
#         stats_line = stats_line.strip().strip(',')
#         inventory_line = ""
#         inv = state.get('inventory', {})
#         if inv:
#             inv_items = ", ".join(f"{item}={count}" for item, count in inv.items())
#             inventory_line = f"Inventory: {inv_items}"
#         # Nearby entities:
#         nearby_line = ""
#         res_list = state.get('resources', [])
#         enemy_list = state.get('enemies', [])
#         if res_list or enemy_list:
#             desc = []
#             for r in res_list:
#                 desc.append(r)
#             for enemy in enemy_list:
#                 desc.append(enemy)
#             nearby_line = "Visible: " + ", ".join(desc)
#         # Combine lines
#         state_lines = [stats_line, inventory_line, nearby_line]
#         state_text = "\n".join([line for line in state_lines if line])
#         return state_text
#     def build_prompt(self, raw_state_text: str) -> str:
#         """
#         Construct the prompt string by combining the game rules, current state, subgoal, and instructions.
#         raw_state_text: the raw state text from the game state parser
#         """
#         # 1. Always include the game rules reference:
#         rules_text = self.game_rules.get_rules_text()
        
#         # 2. Parse the raw state text into structured data (if parser is available)
#         try:
#             state = self.state_parser.parse(raw_state_text)
#             state_text = self.state_text_creator(state)
#         except Exception as e:
#             state = {}
#             state_text = raw_state_text.strip()
#         # If parsing failed or is not implemented, we could fall back to using raw text in the prompt.
        
#         # 3. Update the SubgoalManager with the current state to get the latest subgoal.
#         self.subgoal_manager.update_plan(state)
#         current_goal = self.subgoal_manager.get_current_subgoal()
        
       
        
#         # 4. Construct the prompt sections.
#         prompt_sections: List[str] = []
#         # Game rules section
#         prompt_sections.append(rules_text)

#         # Current state section (label it for clarity)
#         prompt_sections.append("### Current Game State\n" + (state_text or "(No state description available)\n"))
#         # Current goals/subgoal section

#         # prompt_sections.append("### Current Objective\n" 
#         #                         f"Main Goal: {self.subgoal_manager.main_objective}\n"
#         #                         f"Current Sub-Goal: {current_goal}\n")
        

#         # Instruction/Reasoning section
#         reasoning_instruction = ("### Instructions to Agent\n"
#             "You are the Crafter agent. Based on the above game rules and the current state, determine the best next action to achieve the sub-goal. "
#             "First, **think step by step** about what you should do (you can refer to the game rules and consider your inventory and surroundings). "
#             "Then, provide your decision as an action.\n"
#             "Format:\nThought: (your reasoning here)\nAction: (the single next action to take)\n"
#             "Remember: only choose valid actions from the list, and try to accomplish the sub-goal.\n")
#         prompt_sections.append(reasoning_instruction)
        
#         # Join all sections with blank lines between for clarity.
#         final_prompt = "\n\n".join(prompt_sections)
#         return final_prompt
