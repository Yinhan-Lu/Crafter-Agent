
import sys
sys.path.append('./')
from utils import *
from __init__ import *
from descriptor import *


def segment_with_action(trajectory_dir: str, save_path: str, target_action_name: str):
    segment_action = dict()
    state_descriptor = StateDescriptor()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_action[os.path.join(seed, trajectory_name)] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            trajectory_length = len(trajectory['image'])
            description = trajectory['description']

            action_description = state_descriptor.describe_action(trajectory, 0, trajectory_length)
            for action_i in range(len(action_description)-1):
                (action_name, action_index), = action_description[action_i].items()

                if description[action_index] == description[action_index+1]:
                    continue
                
                if action_name != target_action_name:
                    continue
                else:
                    transition = {'previous_description': description[action_index],
                                  'current_description': description[action_index+1], 
                                  'action': action_name}
                    segment_action[os.path.join(seed, trajectory_name)].append(transition)

    with open(save_path, 'w') as f:
        json.dump(segment_action, f, indent=4)


def segment_with_object(trajectory_dir: str, save_path: str, object_name: str) -> None:
    segment_objects = dict()
  
    count = 0
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            trajectory = np.load(trajectory_path, allow_pickle=True)

            description = trajectory['description']
            for description_i in range(len(description)-1):
                if object_name not in description[description_i]:
                    continue
                segment_objects[count] = description[description_i]
                count += 1
    
    with open(save_path, 'w') as f:
        json.dump(segment_objects, f, indent=4)
    


def segment_with_subtask(trajectory_dir: str, save_path: str, target_action_name: str):
    segment_action = dict()
    state_descriptor = StateDescriptor()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_action[os.path.join(seed, trajectory_name)] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            trajectory_length = len(trajectory['image'])
            description = trajectory['description']

            action_description = state_descriptor.describe_action(trajectory, 0, trajectory_length)
            for action_i in range(len(action_description)-1):
                (action_name, action_index), = action_description[action_i].items()

                if description[action_index] == description[action_index+1]:
                    continue
                
                if action_name != target_action_name:
                    continue
                else:
                    prev_actions = []
                    for prev_action_pairs in action_description[action_index-5: action_index+1]:
                        prev_actions.extend(list(prev_action_pairs.keys()))
                    transition = {'descriptions': description[action_index-5: action_index+1].tolist(), 
                                  'action': prev_actions}
                    segment_action[os.path.join(seed, trajectory_name)].append(transition)

    with open(save_path, 'w') as f:
        json.dump(segment_action, f, indent=4)




def segment_with_move_action(trajectory_dir: str, save_path: str):
    segment_action = dict({'move': []})
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_action[os.path.join(seed, trajectory_name)] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            semantic = trajectory['semantic'].tolist()
            pos = trajectory['player_pos'].tolist()
            action = trajectory['action'].tolist()
            trajectory_length = len(trajectory['image'])
            description = trajectory['description']

            for action_i in range(len(action)-1):
                ##TODO: change to the GPS comparision only
                if pos[action_i] != pos[action_i+1] and ('facing grass' in  description[action_i].lower() or 'facing sand' in  description[action_i].lower() or 'facing path' in  description[action_i].lower()):
                    print(description[action_i])
                    transition = {'previous_description': description[action_i],
                                  'current_description': description[action_i+1], 
                                  'action': 'move'}
                    segment_action['move'].append(transition)
            
    with open(save_path, 'w') as f:
        json.dump(segment_action, f, indent=4)


def segment_with_only_subtasks(trajectory_dir: str, save_path: str):
    segment_action = dict()
    state_descriptor = StateDescriptor()
    for seed in os.listdir(trajectory_dir):
        seed_dir = os.path.join(trajectory_dir, seed)
        for trajectory_name in os.listdir(seed_dir):
            if not trajectory_name.endswith('.npz'):
                continue
            trajectory_path = os.path.join(seed_dir, trajectory_name)
            segment_action[os.path.join(seed, trajectory_name)] = []
            trajectory = np.load(trajectory_path, allow_pickle=True)
            trajectory_length = len(trajectory['image'])
            description = trajectory['description']

            action_description = state_descriptor.describe_action(trajectory, 0, trajectory_length)

            useful_actions = []
            previous_action = None
            action_count = 0
            
            for action_i in range(len(action_description) - 1):
                action_i_name = list(action_description[action_i].keys())[0]
                if 'moving' in action_i_name or 'move' in action_i_name or 'do' in action_i_name or 'noop' in action_i_name or 'cow' in action_i_name or 'zombie' in action_i_name or 'skeleton' in action_i_name or 'drink' in action_i_name:
                    continue
                
                if action_i_name == previous_action:
                    action_count += 1
                else:
                    if action_count > 1:
                        useful_actions.append(f"{previous_action}_x_{action_count}")
                    elif previous_action is not None:
                        useful_actions.append(previous_action)
                    previous_action = action_i_name
                    action_count = 1
            
            # Append the last action
            if action_count > 1:
                useful_actions.append(f"{previous_action}_x_{action_count}")
            elif previous_action is not None:
                useful_actions.append(previous_action)

            segment_action[os.path.join(seed, trajectory_name)] = useful_actions

    with open(save_path, 'w') as f:
        json.dump(segment_action, f, indent=4)


if __name__ == '__main__':
    trajectory_dir = 'Dynamics/new_trajectory'
    # save_dir = 'Dynamics/action/segmented_trajectory'
    # actions = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
    #             'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
    #             'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']
    # movement_actions = ['move']
    # save_path = os.path.join(save_dir, 'move.json')
    # segment_with_move_action(trajectory_dir, save_path)

    # save_dir = 'Dynamics/object/segmented_trajectory'
    # objects = ['grass', 'coal', 'cow', 'diamond', 'furnace', 'iron', 'lava', 'skeleton', 'stone', 'table', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe']
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)
    # for object_name in objects:
    #     save_path = os.path.join(save_dir, f'{object_name}.json')
    #     segment_with_object(trajectory_dir, save_path, object_name)


    # save_dir = 'Dynamics/subgoal/segmented_trajectory'
    # subtasks = ['collect_coal', 'collect_diamond', 'collect_drink', 'collect_iron', 'collect_sapling', 'collect_stone', 'collect_wood', 'defeat_skeleton', 
    #             'defeat_zombie', 'eat_cow', 'eat_plant', 'make_iron_pickaxe', 'make_iron_sword', 'make_stone_pickaxe', 'make_stone_sword', 'make_wood_pickaxe', 
    #             'make_wood_sword', 'place_furnace', 'place_plant', 'place_stone', 'place_table', 'sleep']
    # for subtask_name in subtasks:
    #     save_path = os.path.join(save_dir, f'{subtask_name}.json')
    #     segment_with_subtask(trajectory_dir, save_path, subtask_name)

    save_dir = 'Dynamics/subgoal/segmented_trajectory.json'
    segment_with_only_subtasks(trajectory_dir, save_dir)