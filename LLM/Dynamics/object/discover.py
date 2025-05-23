import sys
sys.path.append('./')
from __init__ import *
from descriptor import SimplifiedStateDescriptor

class Discover:
    def __init__(self, trajectory_dir='Dynamics/object/segmented_trajectory', 
                save_dir='Dynamics/object/dynamics/discovered'):
        self._load_trajectory(trajectory_dir)
        self._describe()
        self._save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)


    def _load_trajectory(self, trajectory_dir):
        self.loaded_trajectory = dict()
        for trajectory_name in os.listdir(trajectory_dir):
            with open(os.path.join(trajectory_dir, trajectory_name)) as f:
                trajectory = json.load(f)
                self.loaded_trajectory[trajectory_name[:-5]] = trajectory


    def _describe(self):
        self._description = dict()
        for obj in self.loaded_trajectory:
            self._description[obj] = []
            for _, description in self.loaded_trajectory[obj].items():
                self._description[obj].append(description)


    def discover(self, maximum_indices=16, maxim_sample=16*20):
        for obj in self._description:
            save_path = os.path.join(self._save_dir, f'{obj}.json')
            if os.path.exists(save_path):
                continue

            obj_relationship = dict()
            description = self._description[obj]
            random.shuffle(description)

            maximum_sample = min(len(description), maxim_sample)
            for obj_i in range(0, maximum_sample, maximum_indices):
                initial_index, final_index = obj_i, min(maximum_sample, (obj_i + maximum_indices))
                description = description[initial_index:final_index]
                prefix_prompt = "You are a helpful assistant tasked with identifying object relationships in the Crafter environment. Please respond in JSON format."
                object_relationship_format = """{
                    "related_objects": {
                        "object_1": "relationship to object_1",
                        "object_2": "relationship to object_2",
                        ...
                        }
                    }"""

                prompt = f"""Given randomly selected frames featuring '{obj}', please complete the following:
                1. Identify which objects are most closely related to '{obj}'.
                - Rate their relevance using these terms: 'Very related', 'Not related'.
                - Here are the selected frames concerning '{obj}': {description}
                2. Format your response as follows: {object_relationship_format}

                Only consider the relationship with the following objects: ['grass', 'coal', 'cow', 'diamond', 'iron', 'lava', 'skeleton', 'stone', 'tree', 'water', 'zombie', 'plant', 'path', 'sand', 'plant-ripe']
                For the relationship definitions:
                - Very related: They can always be found together.
                - Not related: They cannot be found together.
                """

                relationship = gpt_json(prefix_prompt, prompt)
                relationship = json.loads(relationship)
                obj_relationship[initial_index] = relationship
                with open(save_path, 'w') as f:
                    json.dump(obj_relationship, f, indent=4)

            

if __name__ == '__main__':
    discover = Discover()
    discover.discover()