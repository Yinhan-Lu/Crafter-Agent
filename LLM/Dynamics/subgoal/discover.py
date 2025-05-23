import sys
sys.path.append('./')
from __init__ import *
from descriptor import *


env_dynamics = {
    "grass": "grass can be found near ['tree', 'water', 'path'], but it is not associated with ['diamond', 'coal', 'iron'] \n You can walk directly through grass. \n grass can only be used for: ['collect_sapling', 'eat_plant'] \n ",
    "coal": "coal can be found near ['stone', 'iron', 'diamond'], but it is not associated with ['grass', 'cow', 'skeleton'] \n You cannot walk directly through coal.coal turn into path after collect_coal \n coal can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'collect_coal'] \n coal can be collected by ['wood_pickaxe'] \n ",
    "cow": "cow can be found near ['grass', 'tree', 'water'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through cow.cow turn into grass after eat_cow \n cow can only be used for: ['eat_cow'] \n ",
    "diamond": "diamond can be found near ['stone', 'iron', 'coal'], but it is not associated with ['grass', 'cow', 'tree'] \n You cannot walk directly through diamond.diamond turn into path after collect_diamond \n diamond can only be used for: ['collect_diamond'] \n diamond can be collected by ['iron_pickaxe'] \n ",
    "iron": "iron can be found near ['coal', 'diamond', 'stone'], but it is not associated with ['grass', 'cow', 'skeleton'] \n You cannot walk directly through iron.iron turn into path after collect_iron \n iron can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'collect_iron'] \n iron can be collected by ['stone_pickaxe'] \n ",
    "lava": "lava can be found near ['stone', 'water', 'sand'], but it is not associated with ['cow', 'tree', 'zombie'] \n You cannot walk directly through lava.",
    "skeleton": "skeleton can be found near ['zombie', 'lava', 'grass'], but it is not associated with ['cow', 'grass', 'coal'] \n You cannot walk directly through skeleton.skeleton turn into path after defeat_skeleton \n skeleton can only be used for: ['defeat_skeleton'] \n ",
    "stone": "stone can be found near ['iron', 'coal', 'diamond'], but it is not associated with ['cow', 'zombie', 'skeleton'] \n You cannot walk directly through stone.stone turn into path after collect_stone \n stone can be placed after place_stone\n stone can only be used for: ['make_stone_pickaxe', 'make_stone_sword', 'place_furnace', 'place_stone', 'collect_stone', 'eat_plant', 'sleep'] \n stone can be collected by ['wood_pickaxe'] \n ",
    "tree": "tree can be found near ['grass', 'path', 'water'], but it is not associated with ['coal', 'cow', 'diamond'] \n You cannot walk directly through tree.tree can only be used for: ['make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 'make_wood_sword', 'place_table', 'collect_wood'] \n ",
    "water": "water can be found near ['sand', 'grass', 'tree'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through water.water can only be used for: ['collect_drink'] \n ",
    "zombie": "zombie can be found near ['skeleton', 'grass', 'cow'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through zombie.zombie turn into grass after defeat_zombie \n zombie can only be used for: ['defeat_zombie'] \n ",
    "plant": "plant can be found near ['grass', 'tree', 'water'], but it is not associated with ['coal', 'diamond', 'iron'] \n You cannot walk directly through plant.plant turn into plant after eat_plant \n plant can be placed after place_plant\n ",
    "path": "path can be found near ['grass', 'tree', 'water'], but it is not associated with ['zombie', 'coal', 'cow'] \n You can walk directly through path. \n path can only be used for: ['sleep'] \n ",
    "sand": "sand can be found near ['water', 'grass', 'path'], but it is not associated with ['coal', 'diamond', 'lava'] \n You can walk directly through sand. \n ",
    "plant-ripe": "plant-ripe can be found near ['grass', 'water', 'stone'], but it is not associated with ['coal', 'cow', 'diamond'] \n You cannot walk directly through plant-ripe.plant-ripe can only be used for: ['eat_plant'] \n ",
    "table": "table requires {'wood': 2} in the inventory to make or place \n ",
    "furnace": "furnace requires ['table'] within immediate distance to make or place \n furnace requires {'stone': 4} in the inventory to make or place \n ",
    "sapling": "You cannot walk directly through sapling.sapling can only be used for: ['place_plant'] \n sapling can be collected by ['wood_sword', 'wood_pickaxe'] \n ",
    "wood_pickaxe": "wood_pickaxe requires ['table'] within immediate distance to make or place \n wood_pickaxe requires {'wood': 1} in the inventory to make or place \n ",
    "stone_pickaxe": "stone_pickaxe requires ['table'] within immediate distance to make or place \n stone_pickaxe requires {'wood': 1, 'stone': 1} in the inventory to make or place \n ",
    "iron_pickaxe": "iron_pickaxe requires ['furnace', 'table'] within immediate distance to make or place \n iron_pickaxe requires {'wood': 1, 'coal': 1, 'iron': 1} in the inventory to make or place \n ",
    "wood_sword": "wood_sword requires ['table'] within immediate distance to make or place \n wood_sword requires {'wood': 1} in the inventory to make or place \n ",
    "stone_sword": "stone_sword requires ['table'] within immediate distance to make or place \n stone_sword requires {'wood': 1, 'stone': 1} in the inventory to make or place \n ",
    "iron_sword": "iron_sword requires ['furnace', 'table'] within immediate distance to make or place \n iron_sword requires {'coal': 1, 'iron': 1, 'wood': 1} in the inventory to make or place \n "
}

class Discover:
    def __init__(self, trajectory_dir='./dynamics/subgoal/segmented_trajectory.json', save_dir='./dynamics/subgoal'):
        self._save_dir = save_dir
        self._load_trajectory(trajectory_dir)

    
    def _load_trajectory(self, trajectory_dir):
        self._trajectory = []
        with open(trajectory_dir, 'r') as f:
            trajectory = json.load(f)
        for _, subtasks in trajectory.items():
            self._trajectory.append(subtasks)
        

    def _discover_plan(self):
        output_format = """{
            "subtasks_contribute_to_the_final_goals": [subtask_1, subtask_2, ......], 
            "reordered_subtasks": [subtask_1, subtask_2, ......], 
            "plan": {
                "subgoal_1": "subgoal_1_description",
                "subgoal_2": "subgoal_2_description",
                ......
            }
        }"""

        output_example = """
        {...,
        "subgoal_3": "Make 1 wood pickaxe and maintain a healthy level of health, food, drink and energy",
        "subgoal_4": "Make 1 wood sword and maintain a healthy level of health, food, drink and energy", 
        "subgoal_5": "Collect 1 sapling and maintain a healthy level of health, food, drink and energy", 
        "subgoal_6": "Place 1 plant and maintain a healthy level of health, food, drink and energy", 
        ...
        },
        """

        human_demo = self._trajectory[:3]
        prefix_prompt = "You are a helpful assistant, tasked with generating the plan that the player needs to achieve the game's final goal. Please respond in JSON format."

        prompt = f"""
        Given the following considerations:
        - The game's final goal: collect diamonds and survive.
        - All the subtasks: {['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 'make_wood_sword', 'move', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']}
        - Environment dynamics: {env_dynamics}
        - Human player completed subtasks in chronological order: {human_demo}
        Note: action_x_y means this action is performed consecutively for y times

        Your task is to generate a plan by reordering the subtasks to help the player achieve the final game goal with different subgoals.

        For plan generation, consider:
        - List all the subtasks that contributes to the final goal from the human player's trajectory.
        - Re-order the subtasks that fits the game's dynamics.
        - For each subtask, state it as a subgoal with a description and the exact repetition of the subtask if needed.

        Lastly, output the plan in this format: {output_format}; 

        For example: {output_example}
        """


        plan = gpt_json(prefix_prompt, prompt)
        plan = json.loads(plan)
        print(plan)
        
        with open(f'{self._save_dir}/subgoal_plan.json', 'w') as f:
            json.dump(plan, f, indent=4)



if __name__ == '__main__':
    discover = Discover()
    discover._discover_plan()