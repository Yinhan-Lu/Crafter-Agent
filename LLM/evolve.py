from __init__ import *

action_dynamics = {
    "collect_coal": {
        "related_dynamics": {
            "You must be facing coal in the immediate surroundings to execute the action 'collect_coal'.",
            "A pickaxe (wood or stone) must be present in the inventory to execute the 'collect_coal' action.",
            "The amount of coal in the inventory increases by 1 unit after the 'collect_coal' action.",
            "The cluster of 'coal' you are facing gets replaced by path, indicating that the coal has been collected.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["coal"]
    }, 
    "collect_diamond": {
        "related_dynamics": {
            "You must be facing diamond in the immediate surroundings to execute the action 'collect_diamond'.",
            "An iron pickaxe must be present in the inventory to execute the 'collect_diamond' action.",
            "The amount of diamond in the inventory increases by 1 unit after the 'collect_diamond' action.",
            "The cluster of 'diamond' you are facing gets replaced by path, indicating that the diamond has been collected.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["diamond"]
    }, 
    "collect_water": {
        "related_dynamics": {
            "Player must be facing water.",
            "Drink level in the status increases by 1 point.",
            "No change in the health, food, or energy levels from this action.",
            "The surrounding environment does not change.",
            "You do not need any equipment to collect water"
        },
        "related_objects": ["water"]
    },
    "collect_iron": {
        "related_dynamics": {
            "You must be facing iron in the immediate surroundings to execute the action 'collect_iron'.",
            "An stone pickaxe must be present in the inventory to execute the 'collect_iron' action.",
            "The amount of iron in the inventory increases by 1 unit after the 'collect_iron' action.",
            "The cluster of 'iron' you are facing gets replaced by path, indicating that the iron has been collected.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["iron"]
    }, 
    "collect_sapling": {
        "related_dynamics": {
            "You must be facing grass in the immediate surroundings to execute the action 'collect_sapling'.",
            "No equipments are need to execute the 'collect_sapling' action.",
            "The amount of sapling in the inventory increases by 1 unit after the 'collect_sapling' action.",
            "The surrounding environment does not change.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["grass"]
    },
    "collect_stone": {
        "related_dynamics": {
            "You must be facing stone in the immediate surroundings to execute the action 'collect_stone'.",
            "An wood pickaxe must be present in the inventory to execute the 'collect_stone' action.",
            "The amount of stone in the inventory increases by 1 unit after the 'collect_stone' action.",
            "The cluster of 'stone' you are facing gets replaced by path, indicating that the stone has been collected.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["stone"]
    }, 
    "collect_tree": {
        "related_dynamics": {
            "You must be facing tree in the immediate surroundings to execute the action 'collect_tree'.",
            "No equipments are required to execute the 'collect_tree' action.",
            "The amount of wood in the inventory increases by 1 unit after the 'collect_tree' action.",
            "The cluster of 'tree' you are facing gets replaced by grass, indicating that the tree has been collected.",
            "Your health, food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["tree"]
    }, 
    "defeat_skeleton":{
        "related_dynamics": {
            "You need to have a 'wood_sword' in your inventory to defeat the skeleton.",
            "You must be facing a skeleton to execute this action.",
            "Health, food, and drink levels can vary and do not necessarily change as a direct result of the defeat_skeleton action.",
            "The skeleton is defeated and no longer exists as an object in the observation.",
            "Your food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["skeleton"]
    },
    "defeat_zombie":{
        "related_dynamics": {
            "You need to have a 'wood_sword' in your inventory to defeat the zombie.",
            "You must be facing a zombie to execute this action.",
            "Health, food, and drink levels can vary and do not necessarily change as a direct result of the defeat_zombie action.",
            "The zombie is defeated and no longer exists as an object in the observation.",
            "Your food, drink, and energy levels will remain unchanged after the action."
        },
        "related_objects": ["zombie"]
    },
    "eat_cow":{
        "related_dynamics": {
            "You need to have a 'wood_sword' in your inventory to defeat the cow.",
            "You must be facing a cow to execute this action.",
            "Health, food, and drink levels can vary and do not necessarily change as a direct result of the eat_cow action.",
            "The cow is defeated and no longer exists as an object in the observation.",
            "Your food level will increase 6."
        },
        "related_objects": ["cow"]
    },
    "make_wood_pickaxe":{
        "related_dynamics": {
            "requires 1 wood",
            "you have be within 1-block radius to the table",
            "you will receive 1 wood pickaxe"
        },
        "related_objects": ["table"]
    },
    "make_wood_sword":{
        "related_dynamics": {
            "requires 1 wood",
            "you have be within 1-block radius to the table",
            "you will receive 1 wood sword"
        },
        "related_objects": ["table"]
    },
    "make_stone_pickaxe":{
        "related_dynamics": {
            "requires 1 wood, 1 stone",
            "you have be within 1-block radius to the table",
            "you will receive 1 stone pickaxe"
        },
        "related_objects": ["table"]
    },
    "make_stone_sword":{
        "related_dynamics": {
            "requires 1 wood, 1 stone",
            "you have be within 1-block radius to the table",
            "you will receive 1 stone sword"
        },
        "related_objects": ["table"]
    },
    "make_iron_pickaxe":{
        "related_dynamics": {
            "requires 1 wood, 1 coal, 1 iron",
            "you have be within 1-block radius to the table and to the furnace",
            "you will receive 1 iron pickaxe"
        },
        "related_objects": ["table", "furnace"]
    },
    "make_iron_sword":{
        "related_dynamics": {
            "requires 1 wood, 1 coal, 1 iron",
            "you have be within 1-block radius to the table and to the furnace",
            "you will receive 1 iron sword"
        },
        "related_objects": ["table", "furnace"]
    },
    "place_table":{
        "related_dynamics": {
            "requires 2 wood",
            "you have to face grass, path and sand to place the table",
            "You will be facing a table in the same direction you were facing before placing the table"
        },
        "related_objects": ["table"]
    },
    "place_furnace":{
        "related_dynamics": {
            "requires 4 stone",
            "you have to face grass, path and sand to place the furnace",
            "You will be facing a furnace in the same direction you were facing before placing the furnace"
        },
        "related_objects": ["furnace"]
    },
    "sleep":{
        "related_dynamics": {
            "you do not need any equipment to sleep", 
            "your energy will increase by 1"
        },
        "related_objects": []
    }
}

object_dynamics = {
    "coal": {
        "description": "Coal can be found near stone, iron, diamond, path, and lava. It can be collected with a wood pickaxe and turns into a walkable path. Without a wood pickaxe, you must take a detour as it is not walkable."
    },
    "cow": {
        "description": "Cow can be found near grass and can be defeated with a wood sword. It is not walkable."
    },
    "diamond": {
        "description": "Diamonds can be found near stone, iron, coal, path, and lava. They can be collected with an iron pickaxe and turn into a walkable path. Without an iron pickaxe, you must take a detour as it is not walkable."
    },
    "furnace": {
        "description": "A furnace can be placed facing grass, sand, or path. It requires 4 stones to build and is not walkable."
    },
    "grass": {
        "description": "Grass can be found near trees and is walkable."
    },
    "iron": {
        "description": "Iron can be found near stone, diamond, coal, path, and lava. It can be collected with a stone pickaxe and turns into a walkable path. Without a stone pickaxe, you must take a detour as it is not walkable."
    },
    "lava": {
        "description": "Lava can be found near stone, diamond, coal, path, and other lava. It is dangerous and not walkable."
    },
    "path": {
        "description": "A path can be found near stone, diamond, coal, iron, and lava. It is walkable."
    },
    "sand": {
        "description": "Sand can be found near water and is not walkable."
    },
    "skeleton": {
        "description": "Skeletons appear at night. They are not walkable and can shoot arrows."
    },
    "stone": {
        "description": "Stone can be found near iron, diamond, coal, path, and lava. It can be collected with a wood pickaxe and turns into a walkable path. Without a wood pickaxe, you must take a detour as it is not walkable."
    },
    "table": {
        "description": "A table can be placed facing grass, sand, or path. It requires 2 wood to build and is not walkable."
    },
    "tree": {
        "description": "Tree can be found near grass and can be collected without equipment. They are not walkable. After collecting a tree, it is replaced by walkable grass."
    },
    "water": {
        "description": "Water can be found near sand. It can be collected without equipment. It is not walkable, and you must take a detour."
    },
    "zombie": {
        "description": "Zombies appear at night. They are not walkable and can attack players."
    },
}


obj_1 = {"water": {
        "description": "Water can be found near sand. It can be collected without any equipment. It is not walkable."
    }}
obj_2 = { "coal": {
        "description": "Coal can be found near stone, iron, diamond, path, and lava. It can be collected using a wooden pickaxe. It is not walkable."
    },}
combination_outputs = "{'situation_1_name': 'situation_description', 'situation_2_name': 'situation_description', ...}"
for action_name, action_dynamic in action_dynamics.items():
    related_dynamics = action_dynamic["related_dynamics"]
    related_objects = action_dynamic["related_objects"]
    prefix_prompt = "You are a helpful assistant tasked with listing all possible combinations for the provided objects. Please respond in JSON format."
    prompt = f"""
    Here are the related objects: {obj_1} {obj_2}.
    In the environment, an object might appear close to the player, between the player and another object, or be out of the player's current view.
    Only list all the possible combination of the related objects.
    Lastly, output in this format: {combination_outputs}
    """
    combinations = gpt_json(prefix_prompt, prompt)
    combinations = json.loads(combinations)
    print(combinations)

    deduction_format = "{'situation_1_name': {'steps':1. ... 2. ..., 'derived_dynamics': ...}, 'situation_2_name': {'steps':1. ... 2. ..., 'derived_dynamics': ...}"
    prefix_prompt = "You are a helpful logician and are asked to use deductive reasoning to discover dynamics for circumventing the provided situation. Please answer in JSON format."
    prompt = f"""
    You are nearing the completion of the task: '{action_name}', its discovered dynamics are: {related_dynamics}.
    You are currently encountering scenarios: {combinations} that may require a revision of the existing dynamics to successfully overcome it.
    To address these scenarios, follow these guidelines:
    - Employ deductive reasoning to develop new dynamics.
    - Rely only on the provided dynamics during the reasoning process.
    - Briefly introduce the deducted dynamics if they are not similar to the existing ones.
    Document the reasoning steps for each scenario, along with any new dynamics you derive.
    Ensure that the output adheres to the specified format: {deduction_format}.
    """
    deduction = gpt_json(prefix_prompt, prompt)
    deduction = json.loads(deduction)
    print(deduction)

    break


# output_format = "{combination_name_1: dediction_steps, combination_name_2: dediction_steps, ......}"
# prefix_prompt = "You are a helpful logician and are asked to use deductive reasoning to discover new and advanced dynamics. Please answer in JSON format."
# prompt = f"""
# You are asked to merge these dynamics: {outer_object_dynamics} to discover new and advanced dynamics.
# First, you should identify all the possible combination situation in the environment for the merging dynamics.
# List all the possible combination situation of the merging dynamics

# Remember: In the environment, an object can appear near the player, or between another object and the player.
# """
# evolved_dynamics = gpt_json(prefix_prompt, prompt)
# evolved_dynamics = json.loads(evolved_dynamics)
# print(evolved_dynamics)


# You should:
# - Identify a reasonable combination situation in the environment for the merging dynamics.
# - Use deductive reasoning to discover new dynamics by merging the candidate dynamics under the specified combination scenario.
# - Only use the discovered dynamics for the deduction process.
# Lastly, if no reasonable combination can be found, simply output 'none'; otherwise, output in this format: {output_format}.
# Here are all the discovered dynamics: {object_dynamics}