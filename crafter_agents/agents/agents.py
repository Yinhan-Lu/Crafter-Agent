from PIL import Image
import base64
import io
import crafter
import openai
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import time
from utils.memory import *
from run_agents import *
from game.game_state import *
from basic_actions import *
from game.action_space import *
from agents.prompts import *
from utils.helper_functions import *
from game.game_infos import *
from agents.structured_prompts import *


class lan_agent_react_v2:
    def __init__(self, game_state, action_space: "ActionSpace", api_key):
        self.game_state = game_state
        self.action_space = action_space
        self.api_key = api_key
        self.prompt = ""
        
        # Initialize memory with correct parameter name
        self.recent_results = Recent_Results(num_of_results=5)
        
        openai.api_key = api_key
        self.time = 0
        self.token_count = 0
        self.current_reasoning = None
        self.current_action = None
        self.current_observation = None
        self.step_count = 0
    

    def get_current_reasoning(self):
        self.current_reasoning =add_newlines(self.current_reasoning)
        return self.current_reasoning
    def get_current_action(self):
        
        return self.current_action
    def get_current_observation(self):
        self.current_observation =add_newlines(self.current_observation)
        return self.current_observation
    
    def prompt_creator(self):
        """
        最终prompt的组成部分：
        1到6是写死的，7可能会call一个function来获取，8来自sub goal manager的，9是写死的，10来自memory的recent_results，11是写死的
        
        1. Crafter的基本规则（这个游戏总体上是在干嘛，游戏目标是什么，游戏规则是什么，例如这个游戏是个2D沙盒游戏等这些最general的信息），不包含具体每个action的意义，每个material的性质或每个player condition的作用，这些在后面会给出
        2. 每个material的性质：每个material的性质是什么，例如wood是可收集的，stone是可收集的，water是可收集的，等等
        3. 每个生物的性质：每个生物的性质是什么，例如cow是可收集的，zombie是可攻击的，等等
        3. 每个action具体描述：每个action可以做的前提条件（例如collect stone必须要有pickaxe，并且游戏人物面前是石头），每个action会得到什么
        4. 每个道具的具体描述：每个道具(pickaxe, sword, 工具台，etc)的获取条件和用途
        5. 每个游戏状态的具体描述：例如口渴的数值到了什么情况会有什么问题，该如何避免，饥饿的数值到了什么情况会有什么问题，该如何避免，等等
        7. current state：
        7.1 当前游戏人物的inventory
        7.2 当前游戏人物的condition（例如口渴，饥饿，facing direction等等）
        7.2 player周围 9x9这个范围内的信息（例如周围的树的位置等等）
        8.对goal的描述。包括写死的goal和动态的sub goal。写死的goal是：找到钻石，动态的sub goal是：根据当前的inventory和condition，以及周围的环境，由sub goal manager生成subgoal
        9. 对React这个回答框架的描述（什么叫ReAct，以及一个例子，用于few shot learning）
        10. 之前n步的react格式信息（step number，observation，reasoning，action， etc）
        11. 对回答格式的要求（例如必须返回json格式，并且json格式必须能够被json.loads()函数解析，回答的action的范围，等等）
        """
        # Use the new structured prompt system that follows the 10-part structure
        self.prompt = build_complete_prompt(
            game_state=self.game_state,
            action_space=self.action_space,
            recent_results=self.recent_results
        )
    
    def act(self):
        """
        1. retrieve game state from the game state class and update the prompt to the agent api
        2. send the prompt to the agent api and get the response(json file)
        3. parse the json file and get the action
        4. return the action
        """
        
        self.prompt_creator()
        start_time = time.time()
        
        # The new structured prompt returns a single string, not a list
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": self.prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        
        # Initialize default values
        observation = "encode observation failed"
        reasoning = "encode reasoning failed"
        action = None
        
        # Try to parse the response
        try: 
            content = response.choices[0].message.content.strip()
            
            # Handle markdown code blocks - strip ```json and ``` markers
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            elif content.startswith('```'):
                content = content[3:]   # Remove ```
            
            if content.endswith('```'):
                content = content[:-3]  # Remove trailing ```
            
            content = content.strip()  # Remove any remaining whitespace
            
            response_json = json.loads(content)
            observation = response_json.get('observation', observation)
            reasoning = response_json.get('reasoning', reasoning)
            action = response_json.get('action')
            
            # print("observation is :", observation, '\n')
            # print("reasoning is :", reasoning, "\n")
            
        except Exception as e:
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Error: {e}")
        
        # Validate and process the action
        final_action = self._process_action(action)
        
        # Update agent state
        self.current_observation = observation
        self.current_reasoning = reasoning
        self.current_action = final_action
        self.step_count += 1
        
        # Store result
        self.recent_results.add_result(
            reasoning=reasoning,
            observation=observation,
            current_step=self.step_count,
            action=final_action
        )
        

        return final_action
    
    def _process_action(self, action):
        """Process and validate the action, returning a valid action."""
        if action is None:
            return self._get_random_action("No action provided")
        
        try:
            action = action.strip()
            if action in legal_actions:
                return action
            else:
                return self._get_random_action(f"Invalid action from GPT: {action}")
        except (AttributeError, ValueError) as e:
            return self._get_random_action(f"Error processing action: {e}")
    
    def _get_random_action(self, reason):
        """Get a random action and log the reason."""
        random_action = random.choice(legal_actions)
        print(f"{reason}. Choosing random action: {random_action}")
        return random_action






class random_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key

    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer one signal word. only answer one of these four actions:'move_left', 'move_right', 'move_up', 'move_down'"},
                {"role": "user", "content": prompt},
            ],
        )
        
        
        action_text = response.choices[0].message.content
        print(response.choices[0].message.content)
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']
        try:
            action = action_text.strip()  
            if action in legal_actions:  
                return action
            else:
                print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                return legal_actions.sample()
        except ValueError:
            print(f"Invalid GPT response: {action_text}. Choosing a random action instead.")
            return legal_actions.sample()
class cot_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key

    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        example_prompt = """
            Here is an example of answer:

            {
  "reasoning": "1. **Current Position**: The player is located in an open grassy area with no visible nearby resources that indicate the presence of diamonds. 2. **Conditions for Finding Diamonds**: Diamonds are located near elements such as stone, iron, coal, lava, and paths. 3. **Exploration Requirement**: The current area shows no immediate signs of any of these elements. To find diamonds, exploring nearby areas is necessary. 4. **Possible Directions**: - **Left**: There may be more unobserved areas, potentially leading to resources. - **Right**: This area also appears unvisited, which could yield necessary elements. - **Up**: The area above doesn't provide much information regarding resources. - **Down**: Like the left and right, the down direction is unexplored. 5. **Conclusion**: Since the player is surrounded by unobserved areas on multiple sides, moving either left, right, or down might yield potential discoveries. However, to maximize exploration of unknown terrain, moving down seems to offer a clearer path to new areas, avoiding the limited visibility upwards.",
  "answer": "move_down"
    }
    ```
            """

        json_example_prompt = """
    Please return the following data in valid JSON format.
    The JSON should have the keys "reasoning" and "answer".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:

    {
    "reasoning": "Detailed explanation of the reasoning process",
    "answer": "move_left"  # Must be one of 'move_left', 'move_right', 'move_up', 'move_down'
    }. 
    """
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer step by step using the Chain of Thought method. For each problem, you must show your reasoning process in detail before providing the final answer(shaped like \"reasoning process: 'the reasoning process'\"). After that, you should give a one-word answer shaped like \"answer: 'move_left'\". one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. "+example_prompt+json_example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('answer')
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:

            print(f"Unable encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class react_agent:
    def __init__(self, env, api_key):
        self.env = env
        self.action_space = env.action_space
        openai.api_key = api_key
        self.time = 0
        self.token_count = 0
    def act(self, image_base64):
        prompt = [ 
            {"type": "text", "text": "Here is the map"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}", "detail": "high"}},
            {"type": "text", "text": """Given there are no diamonds in the map and diamonds can be found near stone, iron, coal, lava and path, which direction should the player to explore?"""}
        ]
        example_prompt = """
            You are an AI agent that uses the ReAct (Reasoning + Acting) framework to understanding the map. Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 

        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be a simple command (e.g., 'move_left', 'move_right', 'pick_item', etc.) that reflects your next move.
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.

        ### Example:
        #### Step 1:
        - **Observation**: The player is standing at a crossroads, with paths leading left, right, and forward. The left path is covered in dense forest, the right path shows signs of a river, and the forward path appears to lead to an open field.
        - **Reasoning**: Moving into the dense forest might slow progress and make exploration difficult. The river to the right could block further movement. The forward path seems to provide the most direct route for exploration.
        - **Action**: move_forward

        #### Step 2:
        - **Observation**: The player moved forward and now stands in the open field. There are mountains visible in the distance.
        - **Reasoning**: The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.
        - **Action**: move_towards_mountains

        Furthermore, In this environment, for the action, one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. 
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:

    {
    "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
    "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
    "action": "move_down"
    }.
    ```
            """

        start_time = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('action')
            print("observation is :",response_json.get('observation'),'\n')
            print("reasoning is :",response_json.get('reasoning'),"\n")
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:

            print(f"Unable encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_random:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }
        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    def act(self, local_view_mat,local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer one signal word. Only answer one of these four actions: 'move_left', 'move_right', 'move_up', 'move_down'"},
                {"role": "user", "content": prompt},
            ],
        )
        
        action_text = response.choices[0].message.content
        print(response.choices[0].message.content)
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']
        try:
            action = action_text.strip()  
            if action in legal_actions:  
                return action
            else:
                print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                return random.choice(legal_actions)
        except ValueError:
            print(f"Invalid GPT response: {action_text}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_cot:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }
        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    
    def act(self, local_view_mat, local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        example_prompt = """
            Here is an example of answer:
    
            {
    "reasoning": "1. **Current Position**: The player is located in an open grassy area with no visible nearby resources that indicate the presence of diamonds. 2. **Conditions for Finding Diamonds**: Diamonds are located near elements such as stone, iron, coal, lava, and paths. 3. **Exploration Requirement**: The current area shows no immediate signs of any of these elements. To find diamonds, exploring nearby areas is necessary. 4. **Possible Directions**: - **Left**: There may be more unobserved areas, potentially leading to resources. - **Right**: This area also appears unvisited, which could yield necessary elements. - **Up**: The area above doesn't provide much information regarding resources. - **Down**: Like the left and right, the down direction is unexplored. 5. **Conclusion**: Since the player is surrounded by unobserved areas on multiple sides, moving either left, right, or down might yield potential discoveries. However, to maximize exploration of unknown terrain, moving down seems to offer a clearer path to new areas, avoiding the limited visibility upwards.",
    "answer": "move_down"
    }
        """
        
        json_example_prompt = """
    Please return the following data in valid JSON format.
    The JSON should have the keys "reasoning" and "answer".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
    "reasoning": "Detailed explanation of the reasoning process",
    "answer": "move_left"  # Must be one of 'move_left', 'move_right', 'move_up', 'move_down'
    }. 
    """
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful agent for understanding the map. Please answer step by step using the Chain of Thought method. For each problem, you must show your reasoning process in detail before providing the final answer (shaped like \"reasoning process: 'the reasoning process'\"). After that, you should give a one-word answer shaped like \"answer: 'move_left'\". One of these four actions: 'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. " + example_prompt + json_example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('answer')
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
class lan_agent_react:
    def __init__(self, env, api_key):
        self.env = env
        openai.api_key = api_key
        self.time = 0
        self.token_count = 0
    
    def lang_wrapper(self,world,player):
        def extract_subarray(big_array, x, y, size=9):
            half_size = size // 2
            # Compute the boundaries while ensuring they don't go out of bounds
            x_min = max(0, x - half_size)
            x_max = min(big_array.shape[0], x + half_size + 1)

            y_min = max(0, y - half_size)
            y_max = min(big_array.shape[1], y + half_size + 1)

            # Extract the 9x9 subarray
            subarray = big_array[x_min:x_max, y_min:y_max]
            return subarray
        
        def map_array_to_text(array, mapping):
            reverse_mapping_dict = {v:k for k, v in mapping.items()}
            text_array = [[reverse_mapping_dict[element] for element in row] for row in array]
            return text_array
        
        wbarr_mat = world._world._mat_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_mat =  extract_subarray(wbarr_mat,wx,wy)

        wbarr_obj = world._world._obj_map
        wx, wy  = player.pos[0], player.pos[1]
        local_view_obj =  extract_subarray(wbarr_obj,wx,wy)

        mapping_mat = world._mat_ids
        mapping_obj_objform = world._obj_ids
        mapping_obj_strform = {
            "Nothing": 0,
            "Player" : 13,
            "Cow" : 14,
            "Zombie": 15,
            "Skeleton": 16,
            "Arrow":17,
            "Plant": 18
        }

        world_objs = world._world._objects
        def map_obj_to_num(obj):
            if obj is None:
                return 0
            else:
                return mapping_obj_objform.get(type(obj))
            
        world_objs_arr = np.array(world_objs)
        vectorized_map = np.vectorize(map_obj_to_num)
        list_objs_numform = vectorized_map(world_objs)

        world_objs_numform = np.array(list_objs_numform)[wbarr_obj]
        local_view_obj =  extract_subarray(world_objs_numform,wx,wy)
        text_local_view_mat = map_array_to_text(local_view_mat,mapping_mat)
        text_local_view_obj = map_array_to_text(local_view_obj,mapping_obj_strform)
        return text_local_view_mat, text_local_view_obj
    
    def act(self, local_view_mat, local_view_obj):
        # Convert the 9x9 arrays to a string format for the prompt
        def array_to_string(array):
            return '\n'.join([' '.join(map(str, row)) for row in array])
        
        mat_str = array_to_string(local_view_mat)
        obj_str = array_to_string(local_view_obj)
        
        prompt = [
            {"type": "text", "text": "Here is the local view of the map:"},
            {"type": "text", "text": f"Materials:\n{mat_str}"},
            {"type": "text", "text": f"Objects:\n{obj_str}"},
            {"type": "text", "text": """Given the materials and objects around the player, which direction should the player explore?"""}
        ]
        
        example_prompt = """
            You are an AI agent that uses the ReAct (Reasoning + Acting) framework to understanding the map. Your task is to observe the current situation, reason about the next best action, and then act based on your reasoning. You will alternate between reasoning and acting to achieve your goals. 
    
        For each step, follow these guidelines:
        1. **Reasoning**: Analyze the current environment and explain your reasoning step by step. Consider the current state and any available information to deduce the best possible action.
        2. **Action**: After reasoning, provide a specific action based on your analysis. The action should be a simple command (e.g., 'move_left', 'move_right', 'pick_item', etc.) that reflects your next move.
        3. **Environment Feedback**: After taking an action, observe the environment's feedback and incorporate it into your next reasoning step.
        4. **Iterate**: Repeat this process by alternating between reasoning and acting until the problem is solved.
    
        ### Example:
        #### Step 1:
        - **Observation**: The player is standing at a crossroads, with paths leading left, right, and forward. The left path is covered in dense forest, the right path shows signs of a river, and the forward path appears to lead to an open field.
        - **Reasoning**: Moving into the dense forest might slow progress and make exploration difficult. The river to the right could block further movement. The forward path seems to provide the most direct route for exploration.
        - **Action**: move_forward
    
        #### Step 2:
        - **Observation**: The player moved forward and now stands in the open field. There are mountains visible in the distance.
        - **Reasoning**: The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.
        - **Action**: move_towards_mountains
    
        Furthermore, In this environment, for the action, one of these four actions:'move_left', 'move_right', 'move_up', 'move_down' is the only acceptable answer. 
        Please return the following data in valid JSON format.
        The JSON should have the keys "observation","reasoning" and "action".  This JSON-like string you generate must be able to convert to json format by json.loads() function Here's an example of the expected format:
    
    {
      "observation": "The player moved forward and now stands in the open field. There are mountains visible in the distance.",
      "reasoning": "The open field is clear and provides visibility of distant landmarks. Heading toward the mountains may reveal new resources or opportunities.",
      "action": "move_down"
    }.
        """
        start_time = time.time()
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": example_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        end_time = time.time()
        each_time = end_time - start_time
        legal_actions = ['move_left', 'move_right', 'move_up', 'move_down']  
        tokens = response.usage.total_tokens
        self.token_count += tokens
        self.time += each_time
        try: 
            response_json = json.loads(response.choices[0].message.content)
            action = response_json.get('action')
            print("observation is :",response_json.get('observation'),'\n')
            print("reasoning is :",response_json.get('reasoning'),"\n")
            try:
                action = action.strip()  
                if action in legal_actions:  
                    return action
                else:
                    print(f"Invalid action from GPT: {action}. Choosing a random action instead.")
                    return random.choice(legal_actions)
            except ValueError:
                print(f"Invalid GPT response: {action}. Choosing a random action instead.")
                return random.choice(legal_actions) 
        except:
            print(f"Unable to encode json. This is the json-like string: {response.choices[0].message.content}. Choosing a random action instead.")
            return random.choice(legal_actions)
