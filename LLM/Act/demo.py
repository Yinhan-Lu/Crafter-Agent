from plan import *
from utils import *
from __init__ import *
from descriptor import SimplifiedStateDescriptor
import heapq

class Pathfinder:
    def __init__(self, matrix, inventory, object_requirements):
        self.matrix = matrix
        self.inventory = inventory
        self.object_requirements = object_requirements

    def is_traversable(self, node):
        item = self.matrix[node[0]][node[1]]
        required_tool = self.object_requirements[item]
        return required_tool is None or self.inventory[required_tool] > 0

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for d in directions:
            neighbor = (node[0] + d[0], node[1] + d[1])
            if 0 <= neighbor[0] < len(self.matrix) and 0 <= neighbor[1] < len(self.matrix[0]):
                result.append(neighbor)
        return result

    def a_star_search(self, start, goal_item):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: 0}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if self.matrix[current[0]][current[1]] == goal_item:
                return self.reconstruct_path(came_from, current)

            for neighbor in self.get_neighbors(current):
                if self.is_traversable(neighbor):
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score_neighbor = tentative_g_score + self.heuristic(neighbor, start)
                        if neighbor not in [n[1] for n in open_set]:
                            heapq.heappush(open_set, (f_score_neighbor, neighbor))

        return None

    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(current)
        path.reverse()
        return path

    def get_next_move(self, start, path):
        if not path or len(path) < 2:
            return "explore for tools or new areas"
        
        next_pos = path[1]  # path[0] is the start itself
        if next_pos[0] < start[0]:
            return "move_north"
        elif next_pos[0] > start[0]:
            return "move_south"
        elif next_pos[1] < start[1]:
            return "move_west"
        elif next_pos[1] > start[1]:
            return "move_east"

    def path_search(self, start, goal_item):
        path_to_goal = self.a_star_search(start, goal_item)
        if path_to_goal:
            return self.get_next_move(start, path_to_goal)
        else:
            return "No path found, need to explore more."
        
class Actor:

    def __init__(self, save_dir='./Act/trajectory', 
                 assets_dir='./Act/assets', 
                 initial_size=(600, 600), map_size=64, 
                 seed=11):
        # Load actions
        with open('./Act/ground_truth_action.json', 'r') as f:
            self._ground_truth_action = json.load(f)

        self._planner = Subtask_Planner()
        self._state_descriptor = SimplifiedStateDescriptor()
        
        self._time_step = 0
        self._total_reward = 0.0
        self._episode_history = dict()
        now = datetime.datetime.now()
        time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        if not os.path.exists(os.path.join(save_dir, str(seed))):
            os.makedirs(os.path.join(save_dir, str(seed)))
        self._save_path = os.path.join(save_dir, str(seed), f'{time_str}.json')

        self._transition = {'subtask': None}
        
        self._map_size = map_size
        self._initial_size = initial_size
        self._external_map = [['unexplored_area' for _ in range(64)] for _ in range(64)]
        self._seed = seed

        self._set_up_env(save_dir)
        self._set_up_assests(assets_dir)
        # self._load_trajectory(os.path.join(save_dir, str(seed), '2024-05-28_13-51-30.json'))
        self.visualize_map()


    def _set_up_env(self, save_path):
        self._env = crafter.Env(seed=self._seed)
        self._env = crafter.Recorder(
            self._env, save_path,
            save_stats=False,
            save_episode=False,
            save_video=False,
        )
        self._env.reset()
        self._env.step(0)
        self._env.remove_all_objects()

        player_pos = self._env.player_pos()
        
        for x in range(0, 64):
            for y in range(0, 64):
                pos = (x, y)
                self._env.set_up_specific_material(pos, 'grass')

        self._env.set_up_player_inventory({'stone': 3, 'wood_pickaxe': 1})
        water_1_pos = (player_pos[0], player_pos[1]+1)
        water_2_pos = (player_pos[0]-1, player_pos[1]+1)
        water_3_pos = (player_pos[0]+1, player_pos[1]+1)
        water_4_pos = (player_pos[0]-2, player_pos[1]+1)
        water_5_pos = (player_pos[0]+2, player_pos[1]+1)

        water_6_pos = (player_pos[0], player_pos[1]+2)
        water_7_pos = (player_pos[0]-1, player_pos[1]+2)
        water_8_pos = (player_pos[0]+1, player_pos[1]+2)
        water_9_pos = (player_pos[0]-2, player_pos[1]+2)
        water_10_pos = (player_pos[0]+2, player_pos[1]+2)

        stone_1_pos = (player_pos[0]+3, player_pos[1])
        stone_2_pos = (player_pos[0]-3, player_pos[1])
        tree_pos = (player_pos[0]+1, player_pos[1]+3)
        stone_3_pos = (player_pos[0], player_pos[1]+4)
        stone_4_pos = (player_pos[0], player_pos[1]+3)
        stone_5_pos = (player_pos[0]+2, player_pos[1]+3)

        self._env.set_up_specific_material(water_1_pos, 'water')
        self._env.set_up_specific_material(water_2_pos, 'water')
        self._env.set_up_specific_material(water_3_pos, 'water')
        self._env.set_up_specific_material(water_4_pos, 'water')
        self._env.set_up_specific_material(water_5_pos, 'water')

        self._env.set_up_specific_material(water_6_pos, 'water')
        self._env.set_up_specific_material(water_7_pos, 'water')
        self._env.set_up_specific_material(water_8_pos, 'water')
        self._env.set_up_specific_material(water_9_pos, 'water')
        self._env.set_up_specific_material(water_10_pos, 'water')        


        self._env.set_up_specific_material(stone_1_pos, 'iron')
        self._env.set_up_specific_material(stone_2_pos, 'iron')
        self._env.set_up_specific_material(tree_pos, 'tree')
        # self._env.set_up_specific_material(stone_3_pos, 'iron')
        # self._env.set_up_specific_material(stone_4_pos, 'iron')
        # self._env.set_up_specific_material(stone_5_pos, 'iron')
        
        self._env.render()
        self._update_map()


    def _set_up_assests(self, assets_dir):
        self._assets = dict()
        for asset in os.listdir(assets_dir):
            asset_name = asset.removesuffix('.png')
            self._assets[asset_name] = Image.open(os.path.join(assets_dir, asset))


    def _load_trajectory(self, trajectory_path):
        with open(trajectory_path, 'r') as f:
            trajectory = json.load(f)
        for _, transition in trajectory.items():
            self._episode_history[self._time_step] = transition
            action = transition['action']
            _, mapped_action = map_action(action)
            self._env.render(self._initial_size)
            self._update_map()
            _, reward, done, info = self._env.step(mapped_action)
            self._total_reward += reward

            self._episode_history[self._time_step] = {
                'subgoal': transition['subgoal'],
                'subtask': transition['subtask'], 
                'state_description': transition['state_description'], 
                'termination': transition['termination'], 
                'action': transition['action'], 
                'previous_actions': transition['previous_actions'][-5:]
            }
            self._transition = transition
            self._time_step += 1

            if done:
                print('The environment has been ended with the reward: ', self._total_reward)
                return
        print('The trajectory has been loaded with the reward: ', self._total_reward)


    def _update_map(self, player_rel_pos=(3, 4)):
        text_description = self._env.text_description()
        player_pos = self._env._player.pos
        # Since text_description is accessed via text_description.T, player_pos must be inverted for alignment.
        player_pos = (player_pos[1], player_pos[0])
        offset = tuple(player_pos_i - player_rel_pos_i for player_pos_i, player_rel_pos_i in zip(player_pos, player_rel_pos))
        
        for row_i, row in enumerate(text_description):
            for col_j, text_object in enumerate(row):
                object_pos = (offset[0] + row_i, offset[1] + col_j)

                if 0 <= object_pos[0] < len(self._external_map) and 0 <= object_pos[1] < len(self._external_map[0]):
                    self._external_map[object_pos[0]][object_pos[1]] = text_object
                else:
                    continue


    def visualize_map(self, image_size=16):
        canvas = Image.new('RGBA', (self._map_size*image_size, self._map_size*image_size))
        for y, row in enumerate(self._external_map):
            for x, element in enumerate(row):
                canvas.paste(self._assets[element], (x * image_size, y * image_size)) 

        plt.figure(figsize=(image_size, image_size))
        plt.imshow(canvas)
        plt.axis('off')
        plt.show()


    def main(self):
        done = False
        mapped_action = 0
        self._transition['previous_actions'] = []

        while not done:
            self._env.render(self._initial_size) 
            self._update_map()

            info = {
                'text_description': self._external_map,
                'inventory': self._env.get_player_inventory(),
            }

            state_description = self._state_descriptor.describe(info)
            available_actions = self._env._player._available_action()
            self._transition.update([('state_description', state_description), 
                                     ('available_actions', available_actions), 
                                     ('inventory', info['inventory']),
                                     ('external_map', self._external_map), 
                                     ('text_description', self._env.text_description().tolist())])

            self.act()
            action = self._transition['action']
            _, mapped_action = map_action(action)   
            print(_, mapped_action)
            _, reward, done, _ = self._env.step(mapped_action)
            self._total_reward += reward
            
            self._episode_history[self._time_step] = {
                # TODO: modify back
                'subgoal': 'Collect wood',
                'subtask': self._transition['subtask'], 
                'state_description': self._transition['state_description'], 
                'termination': self._transition['termination'], 
                'action': self._transition['action'], 
                'previous_actions': self._transition['previous_actions'][-5:],
                'reward': self._total_reward
            }
            with open(self._save_path, 'w') as f:
                json.dump(self._episode_history, f, indent=4)

            self._time_step += 1
            print('toatl reward:', self._total_reward)
            print('state_description:', state_description)
            print('action', self._transition['action'])
            print('==========================================================================================')
        

    def act(self):
        if self._env._player.sleeping:
            return 
        termination, termination_reason = self._terminate_plan()
        self._transition['termination'] = {termination: termination_reason}
        if termination:
            previous_subtask = f"Here is the previous subtask's description: {self._transition['subtask']} and its has been terminated, because {termination_reason}."
            print('Terminating: ', termination_reason)
            self._transition['previous_subtask'] = previous_subtask
            transition = self._planner.plan(self._transition)
            self._transition = transition
            self._transition.update([('previous_actions', [])])
        self.select_action()

    def _terminate_plan(self):
        if self._transition['subtask'] is None:
            return True, None
        
        prefix_prompt = "You are a helpful assistant, tasked with deciding whether the current subtask should be terminated or not. Please answer in JSON format."
        output_format = '{"Termination": "Yes/No", "Justification": "..."}'
        prompt = f"""
        Given the following details:
        - Subtask description: {self._transition['subtask']},
        - Current observation: {self._transition['state_description']},
        - Previous observations and actions: {self._transition['previous_actions'][-5:]}
        you are asked to decide whether the subtask should be terminated or not.

        For deciding whether to terminate the subtask, consider:
        - The previous action, provided it was executed successfully.
        - The differences between the current and previous observations, including changes in the inventory.
        - The differences between the current observation and the subtask’s feasible situation. If any condition of the feasible situation is violated, then the subtask is inappropriate.

        If one of the subtask's termination conditions has been met, the subtask should be terminated. Output 'Yes' if this is the case; otherwise, output 'No'. Also, provide a concise justification for the decision.
        Output in this format: {output_format}.
        """
        termination = gpt_json(prefix_prompt, prompt)
        termination = json.loads(termination)
        if 'yes' in termination['Termination'].lower():
            return True, termination['Justification']
        return False, termination['Justification']


    def select_action(self):
        action = None
        feedback = set()

        # object_requirements = {
        #     'grass': None,
        #     'tree': None,
        #     'player-down': None,
        #     'player-up': None,
        #     'player-left': None,
        #     'player-right': None,
        #     'stone': 'wood_pickaxe',
        #     'water': 'impossible',
        #     'path': None,
        #     'unexplored_area': 'impossible'
        # }
        inventory = self._env.get_player_inventory().copy()
        inventory['impossible'] = 0
        print('available actions:', self._transition['available_actions'])
        # path_finder = Pathfinder(self._external_map, inventory, object_requirements)
        # player_pos = self._env.player_pos().tolist()
        # print('player_pos:', player_pos)
        # next_action = path_finder.path_search((player_pos[1], player_pos[0]), 'tree')
        # print('next action:', next_action)
        while action not in self._transition['available_actions']:
            prefix_prompt = "You are a helpful assistant, tasked with selecting the best action for completing the current subtask. Please provide your answer in JSON format."
            action_format = """{
                'subtask_related_objects': {'object_1_name': {'location': object 1's location, 'dynamic': object 1's dynamic}, ......},
                'top_3_actions_objects': {'action_name_1': {'object_1_name': {'location': object 1's location, 'dynamic': object 1's dynamic}, ......}
                                          'action_name_2': ......
                                          'action_name_3': ......},
                'top_3_actions_consequences': {'action_name_1': 'consequences', 'action_name_2': 'consequences', 'action_name_3': 'consequences'},
                'action_name': 'action_name',
                'action_justification': 'justification'
            }"""
            prompt = f"""
            Given the following details:
            - Current observation: {self._transition['state_description']}
            - Current subtask's description: {self._transition['subtask']}
            - Previous observation and actions: {self._transition['previous_actions'][-5:]}
            - Primitive dynamics: {self._transition['primitive_dynamics']}
            - Evolved dynamics: {self._transition['filtered_evolved_dynamics']}

            You are asked to:
            - identify the objects related to the current subtask and provide their locations and dynamics.
            - select the top 3 actions that you considered to be the best for completing the current subtask and provide all the objects and dynamics directly related with each action.
            - based on each action's related objects, provide the rationale and detailed consequences of executing each action on the objects.
            - select the best action to execute next and provide the justification for your choice.

            Lastly, select the action only from the available actions: {self._transition['available_actions']}; {feedback}.
            
            Please format your response in the following format: {action_format}
            """
            action_and_thoughts = gpt_json(prefix_prompt, prompt)
            action_and_thoughts = json.loads(action_and_thoughts)
            print(action_and_thoughts)
            try:
                action = action_and_thoughts['action_name']
                thoughts = f"At timestep {self._time_step}, you observed {self._transition['state_description']} and selected {action} because {action_and_thoughts['action_justification']}."
            except KeyError:
                print('keyerror')
                print(action_and_thoughts)
            if action not in self._transition['available_actions']:
                print('invalid action: ', action)
                feedback.add(f'{action} is not available in the current state.')
                continue
        self._transition['action'] = action
        self._transition['previous_actions'].append(thoughts)


if __name__ == '__main__':
    actor = Actor()
    actor.main()