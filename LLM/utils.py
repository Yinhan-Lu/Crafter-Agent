from __init__ import *
from descriptor import *

def segment_with_subtask(trajectory_dir: str, save_path: str, target_subtask_name: str) -> None:
    state_descriptor = StateDescriptor()
    segment_subtask = dict()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_subtask[trajectory_name] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            trajectory_length = len(trajectory['image'])
            action = trajectory['action'].tolist()
            semantic = trajectory['semantic'].tolist()

            subtasks = state_descriptor.describe_subtask(trajectory, 0, trajectory_length)
            initial_index, subtask_count = 0, 0
            for subtask_i in range(len(subtasks) - 1):
                (subtask_name, subtask_index),  = subtasks[subtask_i].items()
                (next_subtask_name, _),  = subtasks[subtask_i+1].items()
                if subtask_name != target_subtask_name:
                    continue
                if subtask_name == next_subtask_name:
                    subtask_count += 1
                    continue
                elif subtask_name == 'do(mine_or_collect_or_attack)' and next_subtask_name in do_actions:
                    subtask_count += 1
                    continue
                else:
                    transition = {'initial_index': initial_index, 
                                'final_index': subtask_index, 
                                'count': subtask_count + 1, 
                                'semantic': semantic[initial_index + 1], 
                                'previous_action': action[0: initial_index+1+1]}
                    initial_index = subtask_index
                    subtask_count = 0
                    segment_subtask[trajectory_name].append(transition)
        with open(save_path, 'w') as f:
            json.dump(segment_subtask, f, indent=4)


def map_action(text_action):
    if 'face' in text_action:
        text_action = text_action.replace('face', 'move')
    for action, number in action_mapping.items():
        if action in text_action:
            return action, number
        
    return 'do(mine, collect, attack)', 5


def reverse_action_mapping(number):
    reverse_mapping = {v: k for k, v in action_mapping.items()}
    return reverse_mapping.get(number, "Unknown Action")


def segment_with_action(trajectory_dir: str, save_path: str, target_action_name: str):
    segment_action = dict()
    state_descriptor = StateDescriptor()
    simplified_state_descriptor = SimplifiedStateDescriptor()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_action[os.path.join(seed, trajectory_name)] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            semantic = trajectory['semantic'].tolist()
            action = trajectory['action'].tolist()
            trajectory_length = len(trajectory['image'])

            action_description = state_descriptor.describe_action(trajectory, 0, trajectory_length)
            inventory_description = state_descriptor.describe_inventory(trajectory, 0, trajectory_length)
            text_description = trajectory['text_description'].tolist()
            text_description = text_description[2:]
            for action_i in range(len(action_description)-1):
                (action_name, action_index), = action_description[action_i].items()
                if action_name != target_action_name:
                    continue
                else:
                    previous_description = simplified_state_descriptor.describe({'text_description': text_description[action_index - 1], 'inventory': inventory_description[action_index - 1]})
                    description = simplified_state_descriptor.describe({'text_description': text_description[action_index], 'inventory': inventory_description[action_index]})
                    transition = {'action_index': action_index,
                                  'semantic': semantic[action_index+1], 
                                  'previous_text_description': text_description[action_index-1],
                                  'text_description': text_description[action_index], 
                                  'previous_action': action[:action_index + 2], 
                                  'previous_state_description': previous_description, 
                                  'state_description': description}
                    segment_action[os.path.join(seed, trajectory_name)].append(transition)
    with open(save_path, 'w') as f:
        json.dump(segment_action, f, indent=4)


def add_id(dynamics_file_path: str, save_file_path: str):
    dynamics_with_id = {
        'Very confident': {},
        'Confident': {},
        'Less confident': {}
    }
    id_counters = {
        'Very confident': 0,
        'Confident': 0,
        'Less confident': 0
    }
    with open(dynamics_file_path, 'r') as f:
        dynamics = json.load(f)
    for index in dynamics:
        for condition in dynamics[index]:
            for dynamic_name, dynamic_info in dynamics[index][condition].items():
                confidence = dynamic_info['confidence']
                if confidence in dynamics_with_id:
                    dynamics_with_id[confidence][id_counters[confidence]] = dynamic_info
                    id_counters[confidence] += 1
                else:
                    raise ValueError(f"The confidence level '{confidence}' is not listed.")
    with open(save_file_path, 'w') as f:
        json.dump(dynamics_with_id, f, indent=4)


def segment_trajectory_with_action():
    action = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
              'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
              'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'wake_up']
    trajectory_dir = '../crafter/trajectory'
    save_dir = './DVE/action/segmented_trajectory'
    for action_name in action:
        save_path = os.path.join(save_dir, f'{action_name}.json')
        segment_with_action(trajectory_dir, save_path, action_name)


def segment_trajectory_with_subtask():
    # subtask = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
    #           'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
    #           'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'wake_up']
    subtask = ['eat_cow']
    trajectory_dir = '../crafter/trajectory'
    save_dir = './DVE/subtask/segmented_trajectory'
    for subtask_name in subtask:
        save_path = os.path.join(save_dir, f'{subtask_name}.json')
        segment_with_subtask(trajectory_dir, save_path, subtask_name)


def reformat_trajectory_with_dynamics_id(trajectory_dir='./DVE/action/discover'):
    for trajectory_name in os.listdir(trajectory_dir):
        if not trajectory_name.startswith('discover_'):
            continue
        print(trajectory_name)
        trajectory_path = os.path.join(trajectory_dir, trajectory_name)
        trajectory_save_path = os.path.join(trajectory_dir, f'reformat_{trajectory_name}')
        add_id(trajectory_path, trajectory_save_path)


def discover_plan_demo(trajectory_dir: str):
    state_descriptor = StateDescriptor()
    simplified_descriptor = SimplifiedStateDescriptor()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            if trajectory_name != '20240319T115053-ach15-len418.npz':
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            trajectory = np.load(trajectory_path, allow_pickle=True)
            trajectory_length = len(trajectory['image'])
            text_description = trajectory['text_description']
            subtasks = state_descriptor.describe_subtask(trajectory, 0, trajectory_length)
            inventory = state_descriptor.describe_inventory(trajectory, 0, trajectory_length)
            subtasks_description = ""
            for transition_i in range(len(subtasks)):
                if transition_i == 0:
                    subtask_start_i = 1
                else:
                    (_, subtask_start_i), = subtasks[transition_i-1].items()
                subtask_start_text_description = text_description[subtask_start_i]
                (subtask_name, _), = subtasks[transition_i-1].items()   
                subtask_starting_inventory = inventory[subtask_start_i]
                state_description = simplified_descriptor.describe({'text_description':subtask_start_text_description, 'inventory': subtask_starting_inventory})
                subtasks_description += f'The player starts the subtask {subtask_name}, when {state_description}'
            prefix_prompt = "You are a helpful agent to discover the plan for the human demonstration"
            prompt = f"""Given the trajectory {subtasks_description}. 
                        I hope you can discover the plan for the human demonstration, especially in the overall order of subtask completed. 
                        - e.g. why human player doing this order and what is each subtask's meaning?
                        Here are some dynamics that will aid you to understand the basic world dynamics: 
                            - wood pickaxe and wood sword require wood and crafting table nearby to make. 
                            - stone pickaxe and stone sword require wood, stone and crafting table nearby to make.
                            - iron pickaxe and iron sword require wood, stone, iron and crafting tablem furnace nearby to make. 
                            - zombie, skeleton and its arrow are dangerous
                            - the goal of the game is to mine the diamond
                            - food level can be recovered by eating cow, drink level can be recovered by collecting water and energy level can be recovered by sleeping
                            - tree produces wood and can be found near grassy area. There are no trees in the cave.
                            - stone, iron, iron and diamond can be found in the cave. """
            answer = gpt(prefix_prompt, prompt)
            print(answer)
            return


def flatten_list(nested_list):
    flat_list = []
    for element in nested_list:
        if isinstance(element, list):
            flat_list.extend(flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list


def find_object_locations(transition, objects, player_pos):
    text_description = transition['external_map']
    object_coordinates = {}

    for obj in objects:
        object_coordinates[obj] = []

    for row_idx, row in enumerate(text_description):
        for col_idx, item in enumerate(row):
            if item in objects:
                row_relative = row_idx - player_pos[0]
                col_relative = col_idx - player_pos[1]
                relative_pos = []
                if row_relative > 0:
                    relative_pos.append(f'South {row_relative} blocks')
                elif row_relative < 0:
                    relative_pos.append(f'North {abs(row_relative)} blocks')
                if col_relative > 0:
                    relative_pos.append(f'East {col_relative} blocks')
                elif col_relative < 0:
                    relative_pos.append(f'West {abs(col_relative)} blocks')
                relative_pos = ' and '.join(relative_pos)
                object_coordinates[item].append(relative_pos)

    return object_coordinates


if __name__ == '__main__':
    import cv2
    import numpy as np
    ## TODO: need a totally different file name for saving
    # add_id('./DVE/action/discover/discover_collect_coal.json', './DVE/action/discover/discover_collect_coal.json')
    discover_plan_demo('../crafter/trajectory')
