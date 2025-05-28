import sys
sys.path.append('./')
from __init__ import *

def final_merge(action_dir, object_dir):
    # Load action dynamnics
    with open(os.path.join(action_dir, 'facing_object_change.json'), 'r') as f:
        action_facing_object_change = json.load(f)

    with open(os.path.join(action_dir, 'facing_object_preconditions.json'), 'r') as f:
        action_facing_object_preconditions = json.load(f)
    
    with open(os.path.join(action_dir, 'immediate_object_preconditions.json'), 'r') as f:
        action_immediate_object_preconditions = json.load(f)

    with open(os.path.join(action_dir, 'inventory_materials_precondition.json'), 'r') as f:
        action_inventory_materials_precondition = json.load(f)
    
    with open(os.path.join(action_dir, 'inventory_outcome.json'), 'r') as f:
        action_inventory_outcome = json.load(f)
    
    with open(os.path.join(action_dir, 'inventory_tool_precondition.json'), 'r') as f:
        action_inventory_tool_precondition = json.load(f)

    # Load object dynamics
    with open(os.path.join(object_dir, 'objects.json'), 'r') as f:
        objects_distribution = json.load(f)

    # Final merge
    env_dynamics = dict()
    env_objects = ['grass', 'coal', 'cow', 'diamond', 'iron', 'lava', 'skeleton', 'stone', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe', 'table', 'furnace', 'sapling']
    env_tools = ['wood_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'wood_sword', 'stone_sword', 'iron_sword', 'table', 'furnace']
    for object_name in env_objects:
        env_dynamics[object_name] = ""
        if object_name in objects_distribution.keys():
            env_dynamics[object_name] += f"{object_name} can be found near {objects_distribution[object_name]['top']}, but it is not associated with {objects_distribution[object_name]['bottom']} \n "
        usage = []
        for action_name, action_precondition in action_inventory_materials_precondition.items():
            if object_name == 'tree':
                if 'wood' in action_precondition.keys():
                    usage.append(action_name)
            if object_name in list(action_precondition.keys()):
                usage.append(action_name)
        for action_name, immediate_objects in action_immediate_object_preconditions.items():
            if object_name == 'tree':
                if 'wood' in immediate_objects:
                    usage.append(action_name)
            if object_name in immediate_objects:
                usage.append(action_name)

        for action_name, facing_objects in action_facing_object_preconditions.items():
            if action_name != 'move':
                continue
            if object_name in facing_objects:
                env_dynamics[object_name] += f"You can walk directly through {object_name}. \n "
            else:
                env_dynamics[object_name] += f"You cannot walk directly through {object_name}."

        for action_name, facing_object_change in action_facing_object_change.items():
            if object_name in action_name and 'None' not in facing_object_change and 'place' not in action_name:
                env_dynamics[object_name] += f"{object_name} turn into {facing_object_change[0]} after {action_name} \n "
            if object_name in action_name and 'None' not in facing_object_change and 'place' in action_name:
                env_dynamics[object_name] += f"{object_name} can be placed after {action_name}\n "        
        
        if len(usage) > 0:
            env_dynamics[object_name] += f"{object_name} can only be used for: {usage} \n "
        
        for action_name, inventory_tool in action_inventory_tool_precondition.items():
            if object_name in action_name and 'collect' in action_name:
                env_dynamics[object_name] += f"{object_name} can be collected by {inventory_tool} \n "

    tool_dynamics = dict()
    for tool_name in env_tools:
        tool_dynamics[tool_name] = ""
        for action_name, immediate_objects in action_immediate_object_preconditions.items():
            if tool_name not in action_name:
                continue
            if len(immediate_objects) == 0:
                continue
            tool_dynamics[tool_name] += f"{tool_name} requires {immediate_objects} within immediate distance to make or place \n "

        for action_name, action_precondition in action_inventory_materials_precondition.items():
            if tool_name not in action_name:
                continue
            if len(action_precondition) == 0:
                continue
            
            tool_dynamics[tool_name] += f"{tool_name} requires {action_precondition} in the inventory to make or place \n "

    env_dynamics.update(tool_dynamics)
    # print(env_dynamics)
    with open('./dynamics/merged_dynamics.json', 'w') as f:
        json.dump(env_dynamics, f, indent=4)
        



if __name__ == '__main__':
    action_dir = './dynamics/action/dynamics/merged'
    object_dir = './dynamics/object/dynamics/merged'
    final_merge(action_dir, object_dir)