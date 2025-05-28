import os
import json

def merge_facing_object_preconditions(facing_object_dir, save_dir):
    objects = ['grass', 'coal', 'cow', 'diamond', 'furnace', 'iron', 'lava', 'skeleton', 'stone', 'table', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe']
    actions_facing_objects = dict()

    for action_json in os.listdir(facing_object_dir):
        print(action_json)
        action_merged_set = []

        # Skip non-JSON files
        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(facing_object_dir, action_json)
        try:
            with open(file_path) as f:
                faction_facing_object = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for key, value in faction_facing_object.items():
            for object_name in objects:
                if isinstance(value, list):
                    if object_name in value:
                        action_merged_set.append(object_name)
                elif isinstance(value, dict):
                    if object_name in value.keys() or object_name in value.values():
                        action_merged_set.append(object_name)

        actions_facing_objects[action_json[:-5]] = list(set(action_merged_set))

    save_path = os.path.join(save_dir, 'facing_object_preconditions.json')
    with open(save_path, 'w') as f:
        json.dump(actions_facing_objects, f, indent=4)


def merge_immediate_objects_preconditions(immediate_object_dir, save_dir):
    objects = ['grass', 'coal', 'cow', 'diamond', 'furnace', 'iron', 'lava', 'skeleton', 'stone', 'table', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe']
    actions_immediate_objects = dict()

    for action_json in os.listdir(immediate_object_dir):
        action_merged_set = []

        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(immediate_object_dir, action_json)
        try:
            with open(file_path) as f:
                faction_immediate_object = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for key, value in faction_immediate_object.items():
            for object_name in objects:
                if isinstance(value, list):
                    if object_name in value:
                        action_merged_set.append(object_name)
                elif isinstance(value, dict):
                    if object_name in value.keys() or object_name in value.values():
                        action_merged_set.append(object_name)
        print(action_json)
        print(set(action_merged_set))
        actions_immediate_objects[action_json[:-5]] = list(set(action_merged_set))

    save_path = os.path.join(save_dir, 'immediate_object_preconditions.json')
    with open(save_path, 'w') as f:
        json.dump(actions_immediate_objects, f, indent=4)


def merge_inventory_materials_preconditions(inventory_material_dir, save_dir):
    materials = ['wood', 'stone', 'coal', 'iron', 'diamond', 'sapling']
    actions_inventory_materials = dict()

    for action_json in os.listdir(inventory_material_dir):
        action_merged_dict = dict()

        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(inventory_material_dir, action_json)
        try:
            with open(file_path) as f:
                faction_inventory_material = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for key, value in faction_inventory_material.items():
            if value is None:
                continue
            for material_name in materials:
                if material_name in value:
                    quantity = value[material_name]
                    if quantity > 0:
                        action_merged_dict[material_name] = quantity

        actions_inventory_materials[action_json[:-5]] = action_merged_dict

    save_path = os.path.join(save_dir, 'inventory_materials_precondition.json')
    with open(save_path, 'w') as f:
        json.dump(actions_inventory_materials, f, indent=4)


def merge_inventory_tool_preconditions(inventory_material_dir, save_dir):
    tools = ['wood_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'wood_sword', 'stone_sword', 'iron_sword', 'None']
    actions_inventory_tool = dict()

    for action_json in os.listdir(inventory_material_dir):
        action_merged_set = set()

        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(inventory_material_dir, action_json)
        try:
            with open(file_path) as f:
                faction_inventory_material = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for key, value in faction_inventory_material.items():
            if value is None:
                action_merged_set.add('None')
            for tool_name in tools:
                if tool_name in value:
                    action_merged_set.add(tool_name)

        if 'None' in action_merged_set:
            action_merged_set = {'None'}
        if 'wood_pickaxe' in action_merged_set and 'stone_pickaxe' in action_merged_set:
            action_merged_set.remove('stone_pickaxe')
        if 'wood_pickaxe' in action_merged_set and 'iron_pickaxe' in action_merged_set:
            action_merged_set.remove('iron_pickaxe')
        if 'stone_pickaxe' in action_merged_set and 'iron_pickaxe' in action_merged_set:
            action_merged_set.remove('iron_pickaxe')
        
        if 'wood_sword' in action_merged_set and 'stone_sword' in action_merged_set:
            action_merged_set.remove('stone_sword')
        if 'wood_sword' in action_merged_set and 'iron_sword' in action_merged_set:
            action_merged_set.remove('iron_sword')
        if 'stone_sword' in action_merged_set and 'iron_sword' in action_merged_set:
            action_merged_set.remove('iron_sword')

        actions_inventory_tool[action_json[:-5]] = list(action_merged_set)

    save_path = os.path.join(save_dir, 'inventory_tool_precondition.json')
    with open(save_path, 'w') as f:
        json.dump(actions_inventory_tool, f, indent=4)


def merge_facing_object_change(immediate_object_dir, save_dir):
    objects = ['grass', 'coal', 'cow', 'diamond', 'furnace', 'iron', 'lava', 'skeleton', 'stone', 'table', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe']
    actions_immediate_objects = dict()

    for action_json in os.listdir(immediate_object_dir):
        action_merged_set = []

        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(immediate_object_dir, action_json)
        try:
            with open(file_path) as f:
                faction_immediate_object = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for key, value in faction_immediate_object.items():
            if value is None:
                action_merged_set.append('None')
            if 'None' in value:
                action_merged_set.append('None')
            for object_name in objects:
                try:
                    if object_name in value['to']:
                        action_merged_set.append(object_name)
                except:
                    pass
        action_merged_set = list(set(action_merged_set))
        if 'None' in action_merged_set:
            action_merged_set = ['None']
        actions_immediate_objects[action_json[:-5]] = action_merged_set

    save_path = os.path.join(save_dir, 'facing_object_change.json')
    with open(save_path, 'w') as f:
        json.dump(actions_immediate_objects, f, indent=4)


def merge_facing_inventory_outcome(immediate_object_dir, save_dir):
    inventory = ['wood', 'stone', 'coal', 'iron', 'diamond', 'sapling', 'wood_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'wood_sword', 'stone_sword', 'iron_sword']
    status = ['health', 'food', 'drink', 'energy']
    actions_immediate_objects = dict()

    for action_json in os.listdir(immediate_object_dir):
        # if 'place_stone' not in action_json:
        #     continue
        inventory_merged_set = []
        status_merged_set = []

        if not action_json.endswith('.json'):
            continue

        file_path = os.path.join(immediate_object_dir, action_json)
        try:
            with open(file_path) as f:
                faction_immediate_object = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for _, value in faction_immediate_object.items():
            for inventory_name in inventory:
                try:
                    if value['inventory_increase'] is None or 'None' in value['inventory_increase']:
                        inventory_merged_set.append('None')
                        continue
                    if inventory_name in value['inventory_increase'].keys() and value['inventory_increase'][inventory_name] > 0:
                        inventory_merged_set.append(inventory_name)
                except:
                    for inventory_name in inventory:
                        inventory_value = value['inventory_increase']
                        if type(value['inventory_increase']) is list and len(value['inventory_increase']) > 0:
                            inventory_value = value['inventory_increase'][0]
                        if inventory_name in inventory_value:
                            inventory_merged_set.append(inventory_name)

            for status_name in status:
                try:
                    if value['status_increase'] is None or 'None' in value['status_increase']:
                        status_merged_set.append('None')
                        continue
                    if status_name in value['status_increase'].keys():
                        if type(value['status_increase']) == dict:
                            if '0' not in str(value['status_increase'][status_name]) and 'none' not in str(value['status_increase'][status_name]).lower() and '-' not in str(value['status_increase'][status_name]):
                                status_merged_set.append(status_name)
                        else:
                            status_merged_set.append(status_name)
                except:
                    for status_name in status:
                        status_value = value['status_increase']
                        if type(value['status_increase']) is list and len(value['status_increase']) > 0:
                            status_value = value['status_increase'][0]
                        if status_name in status_value:
                            status_merged_set.append(status_name)
        
        inventory_merged_set = set(inventory_merged_set)
        status_merged_set = set(status_merged_set)
        if 'wood' in inventory_merged_set and 'wood_pickaxe' in inventory_merged_set:
            inventory_merged_set.remove('wood')
        if 'wood' in inventory_merged_set and 'wood_sword' in inventory_merged_set:
            inventory_merged_set.remove('wood')
        if 'stone' in inventory_merged_set and 'stone_pickaxe' in inventory_merged_set:
            inventory_merged_set.remove('stone')
        if 'stone' in inventory_merged_set and 'stone_sword' in inventory_merged_set:
            inventory_merged_set.remove('stone')
        if 'None' in inventory_merged_set:
            inventory_merged_set.remove('None')
        if 'None' in status_merged_set:
            status_merged_set.remove('None')

        actions_immediate_objects[action_json[:-5]] = {'inventory': list(set(inventory_merged_set)), 'status': list(set(status_merged_set))}
        
    save_path = os.path.join(save_dir, 'inventory_outcome.json')
    with open(save_path, 'w') as f:
        json.dump(actions_immediate_objects, f, indent=4)
        

if __name__ == '__main__':
    facing_object_dir = './Dynamics/action/dynamics/verified/inventory_tool_precondition'
    save_dir = './Dynamics/action/dynamics/merged'
    merge_inventory_tool_preconditions(facing_object_dir, save_dir)
